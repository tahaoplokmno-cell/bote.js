import json
import os
import random
import re
import string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== إعدادات البوت ====================
BOT_TOKEN = "8700905522:AAE30w5iFr8jmhIRf_eE0EpSAmk6j1lMfn8"
ADMIN_CHANNEL_ID = "-1004479419959"
ADMIN_ID = "8243108672"
ADMIN_PASSWORD = "T13AHA990POL"
DEVELOPER_USERNAME = "@MrXT1_3"
DB_FILE = 'database.json'

# ==================== إعدادات الدفع ====================
SYRIA_CASH_NUMBER = "8bf19e519ba13641f2a8ae981b8f3081"
SYRIA_CASH_NAME = "شام كاش"

NIGHT_START_HOUR = 0
NIGHT_END_HOUR = 8
PAGE_SIZE = 6

WELCOME_MESSAGE = (
    "🔥 **أهلاً بك في بوت شام إن جيم** 🔥\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "👤 مرحباً: {name}\n"
    "💰 رصيدك: ${balance:.2f}\n"
    "🇸🇾 بالليرة: {syr_balance:,.0f} ل.س\n"
    "📈 سعر الصرف: 1$ = {rate:,} ل.س\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ ** تنبيه:** انا الأدمن الوحيد لذلك الرد بتاخر أحياناً\n"
    "🌙 في الليل (12 صباحاً - 8 صباحاً): احتمال 50% تأخير\n"
    "📞 للدعم الفوري: {developer}\n"
    "💳للشحن:شام كاش {cash_number}"
)

# ==================== الكتالوج الافتراضي ====================
def default_catalog():
    cat = {}
    def add(nid, name, section, parent, ntype, kind=None, price=None, active=True, warning=None):
        cat[nid] = {"name":name,"section":section,"parent":parent,"type":ntype,"kind":kind,"price":price,"active":active,"deleted":False,"children":[],"warning":warning}
        if parent: cat[parent]["children"].append(nid)
    
    add("g1","📁 PUBG MOBILE","games",None,"folder")
    add("g2","📁 ببجي عالمية","games","g1","folder")
    add("g3","📁 ببجي اكواد","games","g2","folder")
    add("g4","🎯 كود 60 شدة ~ 1.10$","games","g3","product","game_code",1.10)
    add("g5","🎯 كود 325 شدة ~ 5.0$","games","g3","product","game_code",5.0)
    add("g6","🎯 كود 660 شدة ~ 10.0$","games","g3","product","game_code",10.0)
    add("g8","📁 Call of Duty","games",None,"folder")
    add("g14","🎯 320 Cp ~ 5.0$","games","g8","product","game_code",5.0)
    add("g21","📁 Free Fire","games",None,"folder")
    add("g24","🎯 100 جوهرة ~ 1.06$","games","g21","product","game_code",1.06)
    add("g28","📁 ROBLOX","games",None,"folder")
    add("g29","🎯 كود روبوكس 10$ ~ 11.0$","games","g28","product","game_code",11.0)
    add("c1","📁 Steam Card","cards",None,"folder")
    add("c3","🎯 Steam 20$ ~ 23$","cards","c1","product","card",23.0)
    add("c6","📁 XBOX Card","cards",None,"folder")
    add("c8","🎯 XBOX 20$ ~ 23$","cards","c6","product","card",23.0)
    return cat

def default_roots():
    return {"games":["g1","g8","g21","g28"],"cards":["c1","c6"],"numbers":[]}

# ==================== قاعدة البيانات ====================
def load_db():
    try:
        with open(DB_FILE,'r',encoding='utf-8') as f: data = json.load(f)
    except: data = {}
    defaults = {"users":{},"banned":{},"exchange_rate":13800,"bot_maintenance":False,"pending_orders":{},"catalog":default_catalog(),"catalog_roots":default_roots(),"next_node_seq":100,"authenticated_admins":[],"stats":{"purchases":0,"refunds":0,"deposits":0,"complaints":0},"activity_log":[],"bot_orders":{},"user_history":{}}
    for k,v in defaults.items():
        if k not in data: data[k] = v
    return data

def save_db(data):
    with open(DB_FILE,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False)

def get_balance(db,uid): return db["users"].get(str(uid),{}).get("balance_usd",0)
def update_balance(db,uid,amount):
    uid = str(uid)
    if uid not in db["users"]: db["users"][uid] = {"name":"مستخدم","balance_usd":0,"joined":datetime.now().isoformat()}
    db["users"][uid]["balance_usd"] = db["users"][uid].get("balance_usd",0) + amount
    if amount != 0:
        htype = "deposit" if amount > 0 else "purchase"
        db.setdefault("user_history",{}).setdefault(uid,[]).append({"type":htype,"amount":amount,"date":datetime.now().isoformat()})

def generate_order_id(): return ''.join(random.choices(string.digits,k=6))
def new_node_id(db,prefix="x"): seq=db.get("next_node_seq",100); db["next_node_seq"]=seq+1; return f"{prefix}{seq}"
def is_night_time(): h=datetime.now().hour; return (NIGHT_START_HOUR<=h<NIGHT_END_HOUR) if NIGHT_START_HOUR<NIGHT_END_HOUR else (h>=NIGHT_START_HOUR or h<NIGHT_END_HOUR)
def is_admin(db,uid): return str(uid) in db.get("authenticated_admins",[])
def log_activity(db,text): db.setdefault("activity_log",[]).append(f"{datetime.now().strftime('%m-%d %H:%M')} | {text}"); db["activity_log"]=db["activity_log"][-50:]
async def notify_admin_dm(context,text,markup=None):
    try: await context.bot.send_message(ADMIN_ID,text,reply_markup=markup)
    except: pass
def clear_awaiting(ud):
    for k in list(ud.keys()):
        if k.startswith('awaiting_'): ud[k]=False
def safe_md(text):
    if not text: return ""
    return str(text).replace('*','').replace('_','').replace('`','').replace('[','')

# ==================== القوائم ====================
main_menu = ReplyKeyboardMarkup([['🏪 المتجر','🤖 إنشاء بوت'],['💳 المحفظة','💰 استرجاع الأموال'],['⚙️ الإعدادات','📞 الدعم الفني']],resize_keyboard=True)
store_menu = InlineKeyboardMarkup([[InlineKeyboardButton("🎮 الألعاب",callback_data="root#games#0")],[InlineKeyboardButton("🎟️ البطاقات",callback_data="root#cards#0")],[InlineKeyboardButton("🔙 الرئيسية",callback_data="main_menu")]])
wallet_menu = InlineKeyboardMarkup([[InlineKeyboardButton("💵 شحن دولار",callback_data="charge#usd")],[InlineKeyboardButton("🇸🇾 شحن ليرة",callback_data="charge#syr")],[InlineKeyboardButton("🔙 الرئيسية",callback_data="main_menu")]])
refund_menu = InlineKeyboardMarkup([[InlineKeyboardButton("💵 استرجاع دولار",callback_data="refund#usd")],[InlineKeyboardButton("🇸🇾 استرجاع ليرة",callback_data="refund#syr")],[InlineKeyboardButton("🔙 الرئيسية",callback_data="main_menu")]])
support_menu = InlineKeyboardMarkup([[InlineKeyboardButton("📩 شكوى/استفسار",callback_data="support#start")],[InlineKeyboardButton("🔙 الرئيسية",callback_data="main_menu")]])
CANCEL_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء",callback_data="cancel_flow")]])

def get_admin_main_panel(db):
    total_users = len(db.get("users",{}))
    s = db.get("stats",{})
    maintenance = "🛠️ مفعل" if db.get("bot_maintenance") else "✅ متوقف"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📊 إيداع:{s.get('deposits',0)} | شراء:{s.get('purchases',0)} | استرجاع:{s.get('refunds',0)}",callback_data="adm#stats")],
        [InlineKeyboardButton(f"👥 المستخدمين:{total_users} | 📩 الشكاوى:{s.get('complaints',0)}",callback_data="adm#users_list")],
        [InlineKeyboardButton(f"📦 طلبات معلقة:{len(db.get('pending_orders',{}))}",callback_data="adm#pending_list")],
        [InlineKeyboardButton(f"🛠️ الصيانة:{maintenance}",callback_data="adm#toggle_maintenance")],
        [InlineKeyboardButton("🔧 إعدادات البوت المتقدمة",callback_data="echo#main")],
        [InlineKeyboardButton("📋 سجل العمليات",callback_data="adm#log"),InlineKeyboardButton("🔎 بحث مستخدم",callback_data="adm#search_user")],
        [InlineKeyboardButton("🤖 طلبات البوتات",callback_data="echo#bot_orders"),InlineKeyboardButton("📝 ملاحظات",callback_data="adm#admin_notes")],
        [InlineKeyboardButton("➕ إضافة رصيد",callback_data="adm#add_balance"),InlineKeyboardButton("➖ خصم رصيد",callback_data="adm#sub_balance")],
        [InlineKeyboardButton("🚫 حظر",callback_data="adm#ban_user"),InlineKeyboardButton("✅ رفع حظر",callback_data="adm#unban_user")],
        [InlineKeyboardButton("📈 سعر الصرف",callback_data="adm#edit_rate"),InlineKeyboardButton("📢 إعلان",callback_data="adm#broadcast")],
        [InlineKeyboardButton("🗂️ شجرة المتجر",callback_data="adm#tree")],
        [InlineKeyboardButton("➕ إضافة منتج",callback_data="adm#add_product"),InlineKeyboardButton("✏️ تعديل سعر",callback_data="adm#edit_price")],
        [InlineKeyboardButton("🗑️ حذف عنصر",callback_data="adm#delete_node"),InlineKeyboardButton("♻️ استرجاع",callback_data="adm#restore_node")],
        [InlineKeyboardButton("💾 نسخة احتياطية",callback_data="adm#backup")],
        [InlineKeyboardButton("🔙 الرئيسية",callback_data="main_menu")]
    ])

def get_echo_main_settings(db):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 رسالة الترحيب",callback_data="echo#welcome")],
        [InlineKeyboardButton("💳 إعدادات الدفع",callback_data="echo#payment")],
        [InlineKeyboardButton("📢 قناة الإشعارات",callback_data="echo#channel")],
        [InlineKeyboardButton("🛒 إدارة المتجر",callback_data="echo#store_mgmt")],
        [InlineKeyboardButton("🤖 طلبات البوتات",callback_data="echo#bot_orders")],
        [InlineKeyboardButton("👥 المستخدمين",callback_data="echo#users_mgmt")],
        [InlineKeyboardButton("📊 إحصائيات",callback_data="adm#stats")],
        [InlineKeyboardButton("🛠️ صيانة",callback_data="adm#toggle_maintenance")],
        [InlineKeyboardButton("💾 نسخة احتياطية",callback_data="adm#backup")],
        [InlineKeyboardButton("🔙 لوحة التحكم",callback_data="open_panel")],
    ])

def render_listing(db,children_ids,back_cb,nav_prefix,page=0):
    cat=db["catalog"]; items=[]
    for cid in children_ids:
        node=cat.get(cid)
        if not node or node.get("deleted"): continue
        if node["type"]=="product" and not node.get("active",True): continue
        items.append((cid,node))
    total_pages=max(1,(len(items)+PAGE_SIZE-1)//PAGE_SIZE); page=max(0,min(page,total_pages-1))
    subset=items[page*PAGE_SIZE:(page+1)*PAGE_SIZE]
    buttons=[]
    for cid,node in subset:
        cb=f"buy#{cid}" if node["type"]=="product" else f"nav#{cid}#0"
        buttons.append([InlineKeyboardButton(node["name"],callback_data=cb)])
    nav_row=[]
    if page>0: nav_row.append(InlineKeyboardButton("⬅️",callback_data=f"{nav_prefix}#{page-1}"))
    if page<total_pages-1: nav_row.append(InlineKeyboardButton("➡️",callback_data=f"{nav_prefix}#{page+1}"))
    if nav_row: buttons.append(nav_row)
    buttons.append([InlineKeyboardButton("🔙 رجوع",callback_data=back_cb)])
    buttons.append([InlineKeyboardButton("🔙 الرئيسية",callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def back_cb_for(node):
    if node.get("parent"): return f"nav#{node['parent']}#0"
    return f"root#{node['section']}#0"

# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id in db.get("banned",{}):
        await update.message.reply_text("🚫 حسابك محظور."); return
    if user_id not in db["users"]:
        db["users"][user_id] = {"name":update.effective_user.first_name or "مستخدم","balance_usd":0,"joined":datetime.now().isoformat()}
        save_db(db)
    balance = db["users"][user_id]["balance_usd"]
    rate = db.get("exchange_rate",13800)
    name = safe_md(update.effective_user.first_name or "مستخدم")
    night_text = "\n🌙 **تنبيه:** قد يتأخر الرد 50% في الليل (12ص-8ص)" if is_night_time() else ""
    text = WELCOME_MESSAGE.format(name=name,balance=balance,syr_balance=balance*rate,rate=rate,developer=DEVELOPER_USERNAME,cash_number=SYRIA_CASH_NUMBER) + night_text
    await update.message.reply_text(text,reply_markup=main_menu)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db(); user_id = str(update.effective_user.id)
    if is_admin(db,user_id): await update.message.reply_text("✅ مصادق! /panel"); return
    clear_awaiting(context.user_data); context.user_data['awaiting_password'] = True
    await update.message.reply_text("🔐 كلمة السر:")

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db(); user_id = str(update.effective_user.id)
    if is_admin(db,user_id): await update.message.reply_text("🛸 لوحة التحكم",reply_markup=get_admin_main_panel(db))
    else: await update.message.reply_text("❌ لا صلاحية.")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear(); await update.message.reply_text("✅ تم الإلغاء.",reply_markup=main_menu)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) == ADMIN_CHANNEL_ID:
        await notify_admin_dm(context,"⚠️ ارد هنا في الخاص وليس في القناة!")

# ==================== معالج النصوص ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = str(update.effective_user.id); text = update.message.text; db = load_db(); ud = context.user_data

    if user_id in db.get("banned",{}) and not is_admin(db,user_id): await update.message.reply_text("🚫 محظور."); return
    if db.get("bot_maintenance",False) and not is_admin(db,user_id): await update.message.reply_text("🛠️ صيانة."); return

    if ud.get('awaiting_charge_proof'):
        amount = ud.get('charge_amount'); usd_amount = ud.get('charge_usd_amount'); currency = ud.get('charge_currency','usd')
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type":"charge","user_id":user_id,"usd_amount":usd_amount,"amount":amount,"currency":currency,"ref":text}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,
            f"🏦 طلب شحن\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n🆔 {user_id}\n💰 {amount} {'$' if currency=='usd' else 'ل.س'} = ${usd_amount:.2f}\n🧾 {safe_md(text)}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ قبول",callback_data=f"charge_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"charge_no#{order_id}")]]))
        ud['awaiting_charge_proof'] = False
        await update.message.reply_text(f"🚀 تم إرسال طلب الشحن {order_id}"); return

    if text == '🏪 المتجر': await update.message.reply_text("🛍️ اختر:",reply_markup=store_menu); return
    if text == '💳 المحفظة': await update.message.reply_text(f"💳 رصيدك: ${get_balance(db,user_id):.2f}",reply_markup=wallet_menu); return
    if text == '💰 استرجاع الأموال': await update.message.reply_text("💰 اختر العملة:",reply_markup=refund_menu); return
    if text == '🤖 إنشاء بوت':
        clear_awaiting(ud); ud['awaiting_bot_desc'] = True
        await update.message.reply_text("🤖 اكتب مواصفات البوت:",reply_markup=CANCEL_BTN); return
    if text == '⚙️ الإعدادات': await update.message.reply_text(f"⚙️ الإعدادات\n👤 {safe_md(update.effective_user.first_name or '?')}\n🆔 {user_id}"); return
    if text == '📞 الدعم الفني': await update.message.reply_text(f"📞 الدعم: {DEVELOPER_USERNAME}\n💳 شام كوس: {SYRIA_CASH_NUMBER}",reply_markup=support_menu); return

    if ud.get('awaiting_password'):
        ud['awaiting_password'] = False
        if text.strip() == ADMIN_PASSWORD:
            if user_id not in db['authenticated_admins']: db['authenticated_admins'].append(user_id); save_db(db)
            await update.message.reply_text("✅ تم! /panel"); return
        else: await update.message.reply_text("❌ خطأ!"); return

    if ud.get('awaiting_complaint'):
        ud['awaiting_complaint'] = False; db['stats']['complaints'] += 1; log_activity(db,f"شكوى {user_id}"); save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"📩 شكوى\n👤 {safe_md(update.effective_user.first_name or '?')}\n🆔 {user_id}\n📝 {safe_md(text)}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ رد",callback_data=f"reply_user#{user_id}")]]))
        await update.message.reply_text("✅ تم."); return

    if ud.get('awaiting_reply_to_user'):
        target_id = ud.get('reply_target_id'); ud['awaiting_reply_to_user'] = False
        try: await context.bot.send_message(target_id,f"💬 رد الدعم:\n{text}"); await update.message.reply_text(f"✅ تم الرد.")
        except Exception as e: await update.message.reply_text(f"❌ {e}"); return

    if ud.get('awaiting_broadcast'):
        ud['awaiting_broadcast'] = False; count = 0
        for uid in db["users"]:
            try: await context.bot.send_message(uid,f"📢 {text}"); count += 1
            except: pass
        await update.message.reply_text(f"✅ تم لـ {count}"); return

    if ud.get('awaiting_add_balance'):
        try:
            parts = text.split('|'); target_id,amount = parts[0].strip(),float(parts[1].strip())
            if amount <= 0: raise ValueError
            update_balance(db,target_id,amount); log_activity(db,f"إضافة ${amount} لـ {target_id}"); save_db(db)
            await update.message.reply_text(f"✅ تم."); await context.bot.send_message(target_id,f"🎉 +${amount}")
        except: await update.message.reply_text("❌ صيغة: آيدي|المبلغ",reply_markup=CANCEL_BTN); return
        ud['awaiting_add_balance'] = False; return

    if ud.get('awaiting_sub_balance'):
        try:
            parts = text.split('|'); target_id,amount = parts[0].strip(),float(parts[1].strip())
            if amount <= 0: raise ValueError
            update_balance(db,target_id,-amount); log_activity(db,f"خصم ${amount}"); save_db(db)
            await update.message.reply_text(f"✅ تم."); await context.bot.send_message(target_id,f"⚠️ -${amount}")
        except: await update.message.reply_text("❌ صيغة: آيدي|المبلغ",reply_markup=CANCEL_BTN); return
        ud['awaiting_sub_balance'] = False; return

    if ud.get('awaiting_ban_user'): target_id=text.strip(); db.setdefault("banned",{})[target_id]=True; save_db(db); await update.message.reply_text(f"🚫 {target_id}"); ud['awaiting_ban_user']=False; return
    if ud.get('awaiting_unban_user'): target_id=text.strip(); db.setdefault("banned",{}).pop(target_id,None); save_db(db); await update.message.reply_text(f"✅ {target_id}"); ud['awaiting_unban_user']=False; return

    if ud.get('awaiting_search_user'):
        target=text.strip(); info=db['users'].get(target); ud['awaiting_search_user']=False
        if not info: await update.message.reply_text("❌ لا يوجد."); return
        history=db.get('user_history',{}).get(target,[])
        hist_text="\n".join([f"{h['date'][:10]} - {h['type']}: ${h['amount']:.2f}" for h in history[-10:]]) or "لا يوجد"
        await update.message.reply_text(f"🔎 {target}\n👤 {safe_md(info.get('name','?'))}\n💰 ${info.get('balance_usd',0):.2f}\n🚫 {'نعم' if target in db.get('banned',{}) else 'لا'}\n📋 {hist_text}"); return

    # إضافة منتج
    if ud.get('awaiting_add_product'):
        try:
            parts = text.split('|'); parent,kind,name,price = parts[0].strip(),parts[1].strip(),parts[2].strip(),float(parts[3].strip())
            if parent not in db['catalog'] or price <= 0: raise ValueError
            nid = new_node_id(db); section = db['catalog'][parent]['section']
            db['catalog'][nid] = {"name":f"🎯 {name} ~ {price}$","section":section,"parent":parent,"type":"product","kind":kind,"price":price,"active":True,"deleted":False,"children":[],"warning":None}
            db['catalog'][parent]['children'].append(nid); save_db(db)
            await update.message.reply_text(f"✅ تم إضافة [{name}] بمعرف {nid}")
        except: await update.message.reply_text("❌ صيغة: parent_id|kind|الاسم|السعر\nمثال: g3|game_code|كود|10.0",reply_markup=CANCEL_BTN); return
        ud['awaiting_add_product'] = False; return

    if ud.get('awaiting_edit_price'):
        try:
            parts=text.split('|'); nid,price=parts[0].strip(),float(parts[1].strip())
            node=db['catalog'][nid]; node['price']=price; node['active']=True
            base=node['name'].split(' ~ ')[0]; node['name']=base+f" ~ {price}$"; save_db(db)
            await update.message.reply_text(f"✅ تم تعديل {nid}")
        except: await update.message.reply_text("❌ صيغة: node_id|السعر",reply_markup=CANCEL_BTN); return
        ud['awaiting_edit_price'] = False; return

    if ud.get('awaiting_delete_node'):
        nid=text.strip(); node=db['catalog'].get(nid)
        if node: node['deleted']=True; save_db(db); await update.message.reply_text(f"🗑️ {nid}")
        else: await update.message.reply_text("❌",reply_markup=CANCEL_BTN); return
        ud['awaiting_delete_node']=False; return

    if ud.get('awaiting_restore_node'):
        nid=text.strip(); node=db['catalog'].get(nid)
        if node: node['deleted']=False; save_db(db); await update.message.reply_text(f"♻️ {nid}")
        else: await update.message.reply_text("❌",reply_markup=CANCEL_BTN); return
        ud['awaiting_restore_node']=False; return

    # شحن
    if ud.get('awaiting_charge'):
        try:
            amount=float(text)
            if amount<=0: raise ValueError
            currency=ud.get('charge_currency','usd'); rate=db.get('exchange_rate',13800)
            usd_amount=amount if currency=='usd' else (amount/rate)
            ud['charge_amount']=amount; ud['charge_usd_amount']=usd_amount; ud['awaiting_charge_proof']=True
            msg=f"📸 {amount} {'$' if currency=='usd' else 'ل.س'} = ${usd_amount:.2f}\n\n💳 **للتحويل:**\nسام كوس: {SYRIA_CASH_NUMBER}\nالاسم: {SYRIA_CASH_NAME}\n\n📤 أرسل صورة الوصل أو رقم المرجع:"
            await update.message.reply_text(msg,reply_markup=CANCEL_BTN)
        except: await update.message.reply_text("❌ رقم!",reply_markup=CANCEL_BTN); return
        ud['awaiting_charge']=False; return

    # استرجاع
    if ud.get('awaiting_refund'):
        try:
            amount=float(text)
            if amount<=0: raise ValueError
            currency=ud.get('refund_currency','usd'); usd_amount=amount if currency=='usd' else amount/db.get('exchange_rate',13800)
            balance=get_balance(db,user_id)
            if balance<usd_amount: await update.message.reply_text(f"❌ رصيدك ${balance:.2f} غير كافٍ!"); ud['awaiting_refund']=False; return
            ud['refund_amount']=amount; ud['refund_usd_amount']=usd_amount; ud['awaiting_refund']=False
            btn=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد",callback_data="confirm_refund")],[InlineKeyboardButton("❌ إلغاء",callback_data="cancel_flow")]])
            await update.message.reply_text(f"💰 {amount} {'$' if currency=='usd' else 'ل.س'} = ${usd_amount:.2f}\n\n📝 **للاسترجاع أرسل:**\nرقم سام كوس + اسمك الكامل\n\nتأكد؟",reply_markup=btn)
        except: await update.message.reply_text("❌ رقم!",reply_markup=CANCEL_BTN); return
        return

    if ud.get('awaiting_refund_info'):
        refund_info = text; ud['refund_info'] = refund_info; ud['awaiting_refund_info'] = False
        amount = ud.get('refund_amount'); usd_amount = ud.get('refund_usd_amount'); currency = ud.get('refund_currency','usd')
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type":"refund","user_id":user_id,"amount":usd_amount,"refund_info":refund_info}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,
            f"💰 استرجاع\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n🆔 {user_id}\n💵 ${usd_amount:.2f}\n📝 السام كوس: {safe_md(refund_info)}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ موافقة",callback_data=f"refund_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"refund_no#{order_id}")]]))
        await update.message.reply_text(f"✅ تم إرسال طلب الاسترجاع {order_id}"); return

    if ud.get('awaiting_game_id'):
        game_id=text; node_id=ud.get('pending_node_id'); node=db['catalog'].get(node_id); ud['awaiting_game_id']=False
        if not node: await update.message.reply_text("❌ خطأ."); return
        ud['pending_game_id']=game_id
        btn=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد",callback_data=f"confirm_game_buy#{node_id}")],[InlineKeyboardButton("❌ إلغاء",callback_data="cancel_flow")]])
        await update.message.reply_text(f"🎁 {safe_md(node['name'])}\n💰 ${node['price']}\n🆔 {safe_md(game_id)}\nتأكد!",reply_markup=btn); return

    if ud.get('awaiting_bot_desc'): ud['bot_desc']=text; ud['awaiting_bot_desc']=False; ud['awaiting_bot_contact']=True; await update.message.reply_text("✍️ رقم تواصلك:",reply_markup=CANCEL_BTN); return
    if ud.get('awaiting_bot_contact'):
        ud['bot_contact']=text; ud['awaiting_bot_contact']=False
        btn=InlineKeyboardMarkup([[InlineKeyboardButton("🔥 قوي 5$/شهر",callback_data="srv#strong")],[InlineKeyboardButton("💤 عادي 2$/شهر",callback_data="srv#normal")]])
        await update.message.reply_text("🖥️ السيرفر:",reply_markup=btn); return

    if ud.get('awaiting_bot_price'):
        m=re.search(r'(\d+(\.\d+)?)',text)
        if not m: await update.message.reply_text("❌ رقم!",reply_markup=CANCEL_BTN); return
        price=float(m.group(1)); target_id=ud.get('bot_target_id'); order_id=ud.get('bot_order_id'); ud['awaiting_bot_price']=False
        order=db.get('bot_orders',{}).get(order_id)
        if order: order['price']=price; save_db(db)
        await context.bot.send_message(target_id,f"💰 السعر: ${price:.2f}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ دفع ${price:.2f}",callback_data=f"bot_pay#{order_id}")]]))
        await update.message.reply_text(f"✅ تم."); return

    if ud.get('awaiting_delivery_code'):
        order_id=ud.get('delivery_order_id'); order=db['pending_orders'].get(order_id); ud['awaiting_delivery_code']=False
        if not order: await update.message.reply_text("❌ غير موجود."); return
        target_id=order['user_id']; delivery_text=f"✅ تم!\n🎁 {safe_md(order.get('item_name',''))}\n📋 {order_id}\n🎟️ الكود: {safe_md(text)}"
        if order.get('kind')=='game_code': delivery_text+=REDEMPTION_INSTRUCTIONS
        try:
            await context.bot.send_message(target_id,delivery_text); await update.message.reply_text(f"✅ تم تسليم {order_id}")
            db['stats']['purchases']+=1; del db['pending_orders'][order_id]; save_db(db)
        except Exception as e: await update.message.reply_text(f"❌ {e}"); ud['awaiting_delivery_code']=True; ud['delivery_order_id']=order_id
        return

    await update.message.reply_text("⚠️ لم أفهم. /cancel",reply_markup=CANCEL_BTN)

# ==================== الصور ====================
async def handle_photo_and_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    user_id=str(update.effective_user.id); db=load_db(); ud=context.user_data
    if ud.get('awaiting_charge_proof') and update.message.photo:
        amount=ud.get('charge_amount'); usd_amount=ud.get('charge_usd_amount'); currency=ud.get('charge_currency','usd')
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"charge","user_id":user_id,"usd_amount":usd_amount,"amount":amount,"currency":currency}
        save_db(db)
        await context.bot.send_photo(ADMIN_CHANNEL_ID,update.message.photo[-1].file_id,
            caption=f"🏦 شحن\n📋 {order_id}\n💰 ${usd_amount:.2f}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅",callback_data=f"charge_ok#{order_id}")],[InlineKeyboardButton("❌",callback_data=f"charge_no#{order_id}")]]))
        ud['awaiting_charge_proof']=False; await update.message.reply_text(f"🚀 {order_id}"); return

# ==================== الأزرار ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query; await query.answer(); data=query.data; user_id=str(update.effective_user.id); db=load_db(); ud=context.user_data

    if data=="cancel_flow": clear_awaiting(ud); await query.edit_message_text("✅ تم."); return
    if data=="open_panel":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        await query.edit_message_text("🛸 لوحة التحكم",reply_markup=get_admin_main_panel(db)); return

    # ============ Echo ============
    if data=="echo#main":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        await query.edit_message_text("🔧 إعدادات متقدمة",reply_markup=get_echo_main_settings(db)); return

    if data=="echo#welcome":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        clear_awaiting(ud); ud['awaiting_echo_welcome']=True
        await query.edit_message_text("✍️ رسالة الترحيب الجديدة:",reply_markup=CANCEL_BTN); return

    if data=="echo#payment":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        await query.edit_message_text(f"💳 إعدادات الدفع\n\nسام كوس: {SYRIA_CASH_NUMBER}\nالاسم: {SYRIA_CASH_NAME}\n\nللتعديل: عدل المتغيرات في الكود.",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙",callback_data="echo#main")]])); return

    if data=="echo#channel":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        await query.edit_message_text(f"📢 القناة: {ADMIN_CHANNEL_ID}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙",callback_data="echo#main")]])); return

    if data=="echo#store_mgmt":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        await query.edit_message_text("🛒 إدارة المتجر:",reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗂️ شجرة",callback_data="adm#tree")],
            [InlineKeyboardButton("➕ منتج",callback_data="adm#add_product"),InlineKeyboardButton("✏️ سعر",callback_data="adm#edit_price")],
            [InlineKeyboardButton("🗑️ حذف",callback_data="adm#delete_node"),InlineKeyboardButton("♻️ استرجاع",callback_data="adm#restore_node")],
            [InlineKeyboardButton("🔙",callback_data="echo#main")]])); return

    if data=="echo#bot_orders":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        orders=db.get('bot_orders',{})
        if not orders: await query.edit_message_text("لا يوجد."); return
        lines=["🤖 طلبات البوتات:"]
        for oid,o in list(orders.items())[:15]: lines.append(f"{oid} - {safe_md(o.get('desc','')[:30])} - {o.get('status','?')}")
        await query.edit_message_text("\n".join(lines),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔎 بحث",callback_data="adm#search_bot_order")],[InlineKeyboardButton("🔙",callback_data="echo#main")]])); return

    if data=="echo#users_mgmt":
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        await query.edit_message_text("👥 المستخدمين:",reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 بحث",callback_data="adm#search_user")],
            [InlineKeyboardButton("📊 الأرصدة",callback_data="adm#view_balances")],
            [InlineKeyboardButton("➕ رصيد",callback_data="adm#add_balance"),InlineKeyboardButton("➖ خصم",callback_data="adm#sub_balance")],
            [InlineKeyboardButton("🚫 حظر",callback_data="adm#ban_user"),InlineKeyboardButton("✅ فك",callback_data="adm#unban_user")],
            [InlineKeyboardButton("🔙",callback_data="echo#main")]])); return

    # ============ ADM ============
    if data.startswith("adm#"):
        if not is_admin(db,user_id): await query.edit_message_text("❌"); return
        action=data.split('#')[1]

        if action=="stats":
            s=db.get("stats",{}); total=len(db["users"]); bal=sum(u.get("balance_usd",0) for u in db["users"].values())
            await query.edit_message_text(f"📊 إحصائيات\n👥 {total}\n💰 ${bal:.2f}\n📦 {len(db.get('pending_orders',{}))}\n🛒 {s.get('purchases',0)}\n💸 {s.get('refunds',0)}\n💳 {s.get('deposits',0)}\n📩 {s.get('complaints',0)}"); return
        if action=="log": log=db.get("activity_log",[])[-15:]; await query.edit_message_text("📋\n"+"\n".join(log) if log else "لا يوجد"); return
        if action=="pending_list": orders=db.get("pending_orders",{}); await query.edit_message_text("\n".join([f"{o} - {d.get('type')}" for o,d in list(orders.items())[:20]]) if orders else "لا يوجد"); return
        if action=="broadcast": clear_awaiting(ud); ud['awaiting_broadcast']=True; await query.edit_message_text("✍️ رسالة:",reply_markup=CANCEL_BTN); return
        if action=="add_balance": clear_awaiting(ud); ud['awaiting_add_balance']=True; await query.edit_message_text("✍️ آيدي|المبلغ:",reply_markup=CANCEL_BTN); return
        if action=="sub_balance": clear_awaiting(ud); ud['awaiting_sub_balance']=True; await query.edit_message_text("✍️ آيدي|المبلغ:",reply_markup=CANCEL_BTN); return
        if action=="ban_user": clear_awaiting(ud); ud['awaiting_ban_user']=True; await query.edit_message_text("✍️ آيدي:",reply_markup=CANCEL_BTN); return
        if action=="unban_user": clear_awaiting(ud); ud['awaiting_unban_user']=True; await query.edit_message_text("✍️ آيدي:",reply_markup=CANCEL_BTN); return
        if action=="search_user": clear_awaiting(ud); ud['awaiting_search_user']=True; await query.edit_message_text("✍️ آيدي:",reply_markup=CANCEL_BTN); return
        if action=="view_balances":
            s="💰:\n"
            for uid,info in list(db["users"].items())[:20]: s+=f"{safe_md(info.get('name','?'))} - ${info.get('balance_usd',0):.2f}\n"
            await query.edit_message_text(s or "لا يوجد"); return
        if action=="users_list":
            s=f"👥 ({len(db['users'])}):\n"
            for uid,info in list(db["users"].items())[:20]: s+=f"{uid} - {safe_md(info.get('name','?'))}\n"
            await query.edit_message_text(s or "لا يوجد"); return
        if action=="edit_rate": clear_awaiting(ud); ud['awaiting_new_rate']=True; await query.edit_message_text(f"📈 الحالي: {db.get('exchange_rate',13800):,}\n✍️ الجديد:",reply_markup=CANCEL_BTN); return
        if action=="tree":
            lines=["🗂️:"]
            for section,roots in db['catalog_roots'].items():
                def walk(nid,depth):
                    node=db['catalog'].get(nid)
                    if not node: return
                    flag=""
                    if node.get('deleted'): flag=" 🗑️"
                    elif node['type']=='product' and not node.get('active',True): flag=" ⛔"
                    price_txt=f" | {node['price']}$" if node.get('price') else ""
                    lines.append(("  "*depth)+f"{nid} {safe_md(node['name'])}{price_txt}{flag}")
                    for c in node.get('children',[]): walk(c,depth+1)
                for r in roots: walk(r,1)
            await query.edit_message_text("\n".join(lines)[:3800]); return
        if action=="add_product": clear_awaiting(ud); ud['awaiting_add_product']=True; await query.edit_message_text("✍️ parent_id|kind|الاسم|السعر\nمثال: g3|game_code|كود|10.0",reply_markup=CANCEL_BTN); return
        if action=="edit_price": clear_awaiting(ud); ud['awaiting_edit_price']=True; await query.edit_message_text("✍️ node_id|السعر",reply_markup=CANCEL_BTN); return
        if action=="delete_node": clear_awaiting(ud); ud['awaiting_delete_node']=True; await query.edit_message_text("✍️ معرف:",reply_markup=CANCEL_BTN); return
        if action=="restore_node": clear_awaiting(ud); ud['awaiting_restore_node']=True; await query.edit_message_text("✍️ معرف:",reply_markup=CANCEL_BTN); return
        if action=="toggle_maintenance": db['bot_maintenance']=not db.get('bot_maintenance',False); save_db(db); await query.edit_message_text(f"🛠️ {'مفعل' if db['bot_maintenance'] else 'متوقف'}"); return
        if action=="admin_notes": clear_awaiting(ud); ud['awaiting_admin_notes']=True; await query.edit_message_text(f"📝 الحالية:\n{db.get('admin_notes','لا')}\n\n✍️ الجديدة:",reply_markup=CANCEL_BTN); return
        if action=="search_bot_order": clear_awaiting(ud); ud['awaiting_search_bot_order']=True; await query.edit_message_text("✍️ آيدي:",reply_markup=CANCEL_BTN); return
        if action=="backup":
            backup_data=json.dumps(db,indent=2,ensure_ascii=False)
            await context.bot.send_document(chat_id=user_id,document=backup_data.encode('utf-8'),filename='backup.json',caption="💾 نسخة")
            await query.edit_message_text("💾 تم"); return
        return

    # ============ باقي الأزرار ============
    if data.startswith("reply_user#"):
        target_id=data.split('#')[1]; clear_awaiting(ud); ud['awaiting_reply_to_user']=True; ud['reply_target_id']=target_id
        await notify_admin_dm(context,f"✍️ رد على {target_id}:"); await query.answer("📩 اكتب في الخاص"); return

    if data=="support#start": clear_awaiting(ud); ud['awaiting_complaint']=True; await query.edit_message_text("📝 اكتب:"); return

    if data.startswith("root#"):
        parts=data.split('#'); section,page=parts[1],int(parts[2]) if len(parts)>2 else 0
        roots=db['catalog_roots'].get(section,[])
        await query.edit_message_text("اختر:",reply_markup=render_listing(db,roots,"store#back",f"root#{section}",page)); return

    if data=="store#back": await query.edit_message_text("🛍️",reply_markup=store_menu); return

    if data.startswith("nav#"):
        parts=data.split('#'); nid,page=parts[1],int(parts[2]) if len(parts)>2 else 0
        node=db['catalog'].get(nid)
        if not node: await query.edit_message_text("⚠️"); return
        await query.edit_message_text(f"📁 {safe_md(node['name'])}",reply_markup=render_listing(db,node['children'],back_cb_for(node),f"nav#{nid}",page)); return

    if data.startswith("buy#"):
        nid=data.split('#')[1]; node=db['catalog'].get(nid)
        if not node or node.get('deleted') or not node.get('active',True) or node.get('price') is None: await query.edit_message_text("⚠️ غير متوفر"); return
        balance=get_balance(db,user_id)
        if balance<node['price']: await query.edit_message_text(f"❌ رصيدك ${balance:.2f} لا يكفي!"); return
        if node['kind']=='game_code':
            clear_awaiting(ud); ud['pending_node_id']=nid; ud['awaiting_game_id']=True
            await query.edit_message_text(f"🎁 {safe_md(node['name'])}\n✍️ الآيدي:",reply_markup=CANCEL_BTN); return
        btn=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد",callback_data=f"confirm_buy#{nid}")],[InlineKeyboardButton("❌",callback_data="cancel_flow")]])
        await query.edit_message_text(f"🎁 {safe_md(node['name'])}\n💰 ${node['price']}\nتأكيد؟",reply_markup=btn); return

    if data.startswith("confirm_buy#"):
        nid=data.split('#')[1]; node=db['catalog'].get(nid)
        if not node or node.get('deleted') or not node.get('active',True): await query.edit_message_text("⚠️"); return
        balance=get_balance(db,user_id)
        if balance<node['price']: await query.edit_message_text("❌ رصيد غير كافٍ!"); return
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"purchase","user_id":user_id,"node_id":nid,"price":node['price'],"item_name":node['name'],"kind":node['kind']}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"🛒 شراء\n📋 {order_id}\n🎁 {safe_md(node['name'])}\n💰 ${node['price']}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅",callback_data=f"order_ok#{order_id}")],[InlineKeyboardButton("❌",callback_data=f"order_no#{order_id}")]]))
        await query.edit_message_text(f"✅ {order_id}"); return

    if data.startswith("confirm_game_buy#"):
        nid=data.split('#')[1]; node=db['catalog'].get(nid); game_id=ud.get('pending_game_id')
        if not node or not game_id: await query.edit_message_text("⚠️"); return
        balance=get_balance(db,user_id)
        if balance<node['price']: await query.edit_message_text("❌"); return
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"purchase","user_id":user_id,"node_id":nid,"price":node['price'],"item_name":node['name'],"game_id":game_id,"kind":node['kind']}
        save_db(db); ud['pending_game_id']=None
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"🛒 شراء\n📋 {order_id}\n🎁 {safe_md(node['name'])}\n💰 ${node['price']}\n🆔 {safe_md(game_id)}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅",callback_data=f"order_ok#{order_id}")],[InlineKeyboardButton("❌",callback_data=f"order_no#{order_id}")]]))
        await query.edit_message_text(f"✅ {order_id}"); return

    if data=="confirm_refund":
        amount=ud.get('refund_amount'); usd_amount=ud.get('refund_usd_amount')
        if amount is None: await query.edit_message_text("⚠️"); return
        balance=get_balance(db,user_id)
        if balance<usd_amount: await query.edit_message_text("❌"); return
        clear_awaiting(ud); ud['awaiting_refund_info']=True
        await query.edit_message_text("📝 أرسل رقم سام كوس + اسمك الكامل لتحويل المبلغ:",reply_markup=CANCEL_BTN); return

    if data.startswith("order_ok#"):
        order_id=data.split('#')[1]; order=db['pending_orders'].get(order_id)
        if not order: await query.edit_message_text("⚠️"); return
        target_id=order['user_id']; balance=get_balance(db,target_id)
        if balance<order['price']: await query.edit_message_text("❌"); return
        update_balance(db,target_id,-order['price']); save_db(db)
        await query.edit_message_text(f"✅ خصم ${order['price']}.\n📩 اكتب الكود في الخاص.")
        clear_awaiting(ud); ud['awaiting_delivery_code']=True; ud['delivery_order_id']=order_id
        await notify_admin_dm(context,f"✍️ كود الطلب {order_id}:"); return

    if data.startswith("order_no#"): order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None); save_db(db); await query.edit_message_text(f"❌ {order_id}"); return
    if data.startswith("charge_ok#"):
        order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None)
        if not order: await query.edit_message_text("⚠️"); return
        update_balance(db,order['user_id'],order['usd_amount']); db['stats']['deposits']+=1; save_db(db)
        await query.edit_message_text(f"✅ {order_id}"); await context.bot.send_message(order['user_id'],f"✅ +${order['usd_amount']:.2f}"); return
    if data.startswith("charge_no#"): order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None); save_db(db); await query.edit_message_text(f"❌ {order_id}"); return
    if data.startswith("refund_ok#"):
        order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None)
        if not order: await query.edit_message_text("⚠️"); return
        update_balance(db,order['user_id'],-order['amount']); db['stats']['refunds']+=1; save_db(db)
        await query.edit_message_text(f"✅ {order_id}"); await context.bot.send_message(order['user_id'],f"✅ تم استرجاع ${order['amount']:.2f}"); return
    if data.startswith("refund_no#"): order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None); save_db(db); await query.edit_message_text(f"❌ {order_id}"); return

    if data.startswith("charge#"): currency=data.split('#')[1]; clear_awaiting(ud); ud['charge_currency']=currency; ud['awaiting_charge']=True; await query.edit_message_text("✍️ المبلغ:",reply_markup=CANCEL_BTN); return
    if data.startswith("refund#"): currency=data.split('#')[1]; clear_awaiting(ud); ud['refund_currency']=currency; ud['awaiting_refund']=True; await query.edit_message_text("✍️ المبلغ:",reply_markup=CANCEL_BTN); return

    if data.startswith("srv#"):
        srv_type=data.split('#')[1]; srv_name="🔥قوي 5$/شهر/اول اسبوع مجانا" if srv_type=='strong' else "💤 عادي 2$/شهر"
        desc=ud.get('bot_desc','غير محدد'); contact=ud.get('bot_contact','غير محدد'); order_id=generate_order_id()
        db.setdefault('bot_orders',{})[order_id]={"user_id":user_id,"desc":desc,"contact":contact,"srv_name":srv_name,"price":None,"details":"","file_id":None,"status":"pending"}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"🤖 بوت\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n💬 {safe_md(contact)}\n📝 {safe_md(desc)}\n🖥️ {srv_name}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 سعر",callback_data=f"bot_price#{user_id}#{order_id}")],[InlineKeyboardButton("⏰ وقت",callback_data=f"bot_time#{user_id}#{order_id}")],[InlineKeyboardButton("📝 تفاصيل",callback_data=f"bot_notes#{user_id}#{order_id}")],[InlineKeyboardButton("📂 ملف",callback_data=f"bot_file#{user_id}#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"bot_reject#{user_id}#{order_id}")]]))
        ud['awaiting_bot_desc']=False; ud['awaiting_bot_contact']=False; await query.edit_message_text("🚀 تم."); return

    if data.startswith("bot_price#"): parts=data.split('#'); clear_awaiting(ud); ud['bot_target_id']=parts[1]; ud['bot_order_id']=parts[2]; ud['awaiting_bot_price']=True; await notify_admin_dm(context,f"✍️ سعر {parts[2]}:"); await query.answer("📩 اكتب في الخاص"); return
    if data.startswith("bot_pay#"):
        order_id=data.split('#')[1]; order=db.get('bot_orders',{}).get(order_id)
        if not order or order['user_id']!=user_id: await query.edit_message_text("⚠️"); return
        if order.get('status')=='paid': await query.edit_message_text("✅ مدفوع"); return
        price=order.get('price')
        if price is None: await query.edit_message_text("⚠️ لا سعر"); return
        balance=get_balance(db,user_id)
        if balance<price: await query.edit_message_text(f"❌ ${balance:.2f}"); return
        update_balance(db,user_id,-price); order['status']='paid'; db['stats']['purchases']+=1; save_db(db)
        await query.edit_message_text(f"✅ خصم ${price:.2f}"); return
    if data.startswith("bot_reject#"): parts=data.split('#'); order=db.get('bot_orders',{}).get(parts[2]); if order: order['status']='rejected'; save_db(db); await query.edit_message_text(f"❌ {parts[2]}"); return

    if data=="main_menu": await context.bot.send_message(chat_id=update.effective_chat.id,text="🎯 الرئيسية",reply_markup=main_menu); return

# ==================== تشغيل ====================
def main():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("admin",admin_command))
    app.add_handler(CommandHandler("panel",panel_command))
    app.add_handler(CommandHandler("cancel",cancel_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,handle_text))
    app.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & filters.ChatType.PRIVATE,handle_photo_and_document))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL,handle_channel_post))
    print("🚀 البوت شغال!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
    main()
