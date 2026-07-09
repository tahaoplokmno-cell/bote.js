import json, os, random, re, string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8700905522:AAE30w5iFr8jmhIRf_eE0EpSAmk6j1lMfn8"
ADMIN_CHANNEL_ID = "-1004479419959"
ADMIN_ID = "8243108672"
ADMIN_PASSWORD = "T13AHA990POL"
DEVELOPER_USERNAME = "@MrXT1_3"
DB_FILE = 'database.json'
SYRIA_CASH_NUMBER = "8bf19e519ba13641f2a8ae981b8f3081"
SYRIA_CASH_NAME = "شام كاش"
NIGHT_START_HOUR, NIGHT_END_HOUR, PAGE_SIZE = 0, 8, 6

REDEMPTION_INSTRUCTIONS = "\n\n📦 تعليمات الاستبدال:\n1️⃣https://www.midasbuy.com/midasbuy/ng/zh/game/pubgmobile  ادخل إلى الموقع الرسمي للشحن\n2️⃣ اختر لعبتك وأدخل آيدي حسابك\n3️⃣ اختر استرداد الاكواد وأدخل الكود\n4️⃣ اضغط استرداد\n🔔 شغّل VPN إذا كنت داخل سوريا"

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
    add("g7","🎯 كود 1800 شدة (السعر غير محدد)","games","g3","product","game_code",None,active=False)
    add("g8","📁 Call of Duty","games",None,"folder")
    add("g13","📁 320 CP","games","g8","folder")
    add("g14","🎯 320 Cp ~ 5.0$","games","g13","product","game_code",5.0)
    add("g15","📁 480 CP","games","g8","folder")
    add("g16","🎯 480 Cp ~ 7.15$","games","g15","product","game_code",7.15)
    add("g17","📁 560 CP","games","g8","folder")
    add("g18","🎯 560 Cp ~ 8.30$","games","g17","product","game_code",8.30)
    add("g19","📁 1120 CP","games","g8","folder")
    add("g20","🎯 1120 Cp ~ 17.0$","games","g19","product","game_code",17.0)
    add("g21","📁 Free Fire","games",None,"folder")
    add("g22","📁 فري فاير شرق اوسط","games","g21","folder")
    add("g23","📁 فري فاير Garena","games","g22","folder")
    add("g24","🎯 100+10 جوهرة ~ 1.06$","games","g23","product","game_code",1.06)
    add("g25","🎯 210+21 جوهرة ~ 2.09$","games","g23","product","game_code",2.09)
    add("g26","🎯 530+53 جوهرة ~ 5.07$","games","g23","product","game_code",5.07)
    add("g27","🎯 1080+108 جوهرة ~ 11.0$","games","g23","product","game_code",11.0)
    add("g28","📁 ROBLOX","games",None,"folder")
    add("g29","🎯 كود روبوكس 10$ إمريكي ~ 11.0$","games","g28","product","game_code",11.0)
    add("g30","🎯 كود روبوكس 15$ إمريكي ~ 16.02$","games","g28","product","game_code",16.02)
    add("g31","📁 FC Mobile","games",None,"folder")
    add("g32","📁 FC Mobile Cambodia","games","g31","folder")
    add("g33","🎯 Silver 99 ~ 1.20$","games","g32","product","game_code",1.20)
    add("g34","🎯 Silver 499 ~ 5.99$","games","g32","product","game_code",5.99)
    add("g35","🎯 100 FC Points ~ 1.20$","games","g32","product","game_code",1.20)
    add("g36","🎯 520 FC Points ~ 5.99$","games","g32","product","game_code",5.99)
    add("g37","📁 Minecraft","games",None,"folder")
    add("g38","🎯 كود 3500 كوينز ~ 22.0$","games","g37","product","game_code",22.0)
    add("g39","🎯 كود 1720 كوينز ~ 11.0$","games","g37","product","game_code",11.0)
    add("g40","📁 Stumble Guys (نفذ المخزون مؤقتاً)","games",None,"folder")
    add("c1","📁 Steam Card","cards",None,"folder")
    add("c2","📁 Steam USA","cards","c1","folder")
    add("c3","🎯 Steam 20$ USA ~ 23$","cards","c2","product","card",23.0)
    add("c4","🎯 Steam 50$ USA ~ 57$","cards","c2","product","card",57.0)
    add("c5","🎯 Steam 100$ USA ~ 112$","cards","c2","product","card",112.0)
    add("c6","📁 XBOX Card","cards",None,"folder")
    add("c7","📁 XBOX USA","cards","c6","folder")
    add("c8","🎯 XBOX 20$ USA ~ 23$","cards","c7","product","card",23.0)
    add("c9","🎯 XBOX 50$ USA ~ 57$","cards","c7","product","card",57.0)
    add("c10","🎯 XBOX 100$ USA ~ 112$","cards","c7","product","card",112.0)
    number_warning = "⚠️ **تنبيه هام قبل الطلب:**\nسيتم إظهار الرقم بشكل مباشر ويمكنك طلب الكود من واتساب الرسمي.\n❌ حال لم يصل كود التفعيل، سيتم رفض الطلب تلقائياً واستعادة رصيدك.\n🚫 ممنوع طلب الكود مرتين على نفس الرقم: إن طلبت الكود مرتين، الكود الذي يصل لأول طلب فقط هو الصالح.\n✅ اطلب الكود مرة واحدة فقط.\nℹ️ أحياناً عند وضع الرقم في واتساب يُرسل الطلب تلقائياً، تأكد قبل الطلب.\n⚠️ الأرقام وهمية وغير مكفولة نهائياً."
    add("n2","📁 أرقام واتساب","numbers",None,"folder")
    add("n3","🎯 المانيا 49+ ~ 2.00$","numbers","n2","product","whatsapp_number",2.00,warning=number_warning)
    add("n4","🎯 مصر 20+ ~ 1.50$","numbers","n2","product","whatsapp_number",1.50,warning=number_warning)
    add("n5","🎯 بريطانيا 44+ ~ 1.00$","numbers","n2","product","whatsapp_number",1.00,warning=number_warning)
    add("n6","📁 أرقام تيليجرام (نفذ المخزون مؤقتاً)","numbers",None,"folder")
    return cat

def default_roots():
    return {"games":["g1","g8","g21","g28","g31","g37","g40"],"cards":["c1","c6"],"numbers":["n2","n6"]}

def load_db():
    try:
        with open(DB_FILE,'r',encoding='utf-8') as f: data = json.load(f)
    except: data = {}
    defaults = {"users":{},"banned":{},"exchange_rate":13800,"admin_notes":"","bot_maintenance":False,"pending_orders":{},"catalog":default_catalog(),"catalog_roots":default_roots(),"next_node_seq":100,"authenticated_admins":[],"stats":{"purchases":0,"refunds":0,"deposits":0,"complaints":0},"activity_log":[],"bot_orders":{},"user_history":{}}
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
def is_night_time(): h=datetime.now().hour; return NIGHT_START_HOUR<=h<NIGHT_END_HOUR if NIGHT_START_HOUR<NIGHT_END_HOUR else (h>=NIGHT_START_HOUR or h<NIGHT_END_HOUR)
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

main_menu = ReplyKeyboardMarkup([['🏪 المتجر','🤖 إنشاء بوت'],['💳 المحفظة','💰 استرجاع الأموال'],['⚙️ الإعدادات','📞 الدعم الفني']],resize_keyboard=True)
store_menu = InlineKeyboardMarkup([[InlineKeyboardButton("🎮 قسم الألعاب",callback_data="root#games#0")],[InlineKeyboardButton("🎟️ قسم البطاقات",callback_data="root#cards#0")],[InlineKeyboardButton("📱 الأرقام",callback_data="root#numbers#0")],[InlineKeyboardButton("📱 شحن رصيد هاتف",callback_data="store#phone")],[InlineKeyboardButton("🔙 القائمة الرئيسية",callback_data="main_menu")]])
phone_menu = InlineKeyboardMarkup([[InlineKeyboardButton("📱 سيريتل",callback_data="phone#syr")],[InlineKeyboardButton("📱 إم تي إن",callback_data="phone#mtn")],[InlineKeyboardButton("🔙 رجوع للمتجر",callback_data="store#back")],[InlineKeyboardButton("🔙 القائمة الرئيسية",callback_data="main_menu")]])
wallet_menu = InlineKeyboardMarkup([[InlineKeyboardButton("💵 شحن بالدولار",callback_data="charge#usd")],[InlineKeyboardButton("🇸🇾 شحن بالليرة",callback_data="charge#syr")],[InlineKeyboardButton("🔙 القائمة الرئيسية",callback_data="main_menu")]])
refund_menu = InlineKeyboardMarkup([[InlineKeyboardButton("💵 استرجاع بالدولار",callback_data="refund#usd")],[InlineKeyboardButton("🇸🇾 استرجاع بالليرة",callback_data="refund#syr")],[InlineKeyboardButton("🔙 القائمة الرئيسية",callback_data="main_menu")]])
support_menu = InlineKeyboardMarkup([[InlineKeyboardButton("📩 إرسال شكوى / استفسار",callback_data="support#start")],[InlineKeyboardButton("🔙 القائمة الرئيسية",callback_data="main_menu")]])
CANCEL_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء العملية",callback_data="cancel_flow")]])

def get_admin_main_panel(db):
    total_users = len(db.get("users",{}))
    s = db.get("stats",{})
    maintenance = "🛠️ مفعل" if db.get("bot_maintenance") else "✅ متوقف"
    total_balance = sum(u.get("balance_usd",0) for u in db["users"].values())
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📊 إحصائيات شاملة",callback_data="adm#stats")],
        [InlineKeyboardButton(f"💰 إجمالي الأرصدة: ${total_balance:.2f}",callback_data="adm#view_balances")],
        [InlineKeyboardButton(f"👥 المستخدمين: {total_users} | 📩 الشكاوى: {s.get('complaints',0)}",callback_data="adm#users_list")],
        [InlineKeyboardButton(f"📦 الطلبات المعلقة: {len(db.get('pending_orders',{}))}",callback_data="adm#pending_list")],
        [InlineKeyboardButton(f"🛠️ الصيانة: {maintenance}",callback_data="adm#toggle_maintenance")],
        [InlineKeyboardButton("🔧 إعدادات البوت المتقدمة",callback_data="echo#main")],
        [InlineKeyboardButton("📋 آخر العمليات (سجل)",callback_data="adm#log"),InlineKeyboardButton("🔎 بحث عن مستخدم",callback_data="adm#search_user")],
        [InlineKeyboardButton("🤖 بحث عن طلب بوت",callback_data="adm#search_bot_order"),InlineKeyboardButton("📝 ملاحظات الإدارة",callback_data="adm#admin_notes")],
        [InlineKeyboardButton("👮 قائمة الأدمنية",callback_data="adm#list_admins"),InlineKeyboardButton("📤 تصدير المستخدمين",callback_data="adm#export_users")],
        [InlineKeyboardButton("📢 إرسال إعلان",callback_data="adm#broadcast"),InlineKeyboardButton("📊 عرض الأرصدة",callback_data="adm#view_balances")],
        [InlineKeyboardButton("➕ إضافة رصيد",callback_data="adm#add_balance"),InlineKeyboardButton("➖ خصم رصيد",callback_data="adm#sub_balance")],
        [InlineKeyboardButton("🚫 حظر مستخدم",callback_data="adm#ban_user"),InlineKeyboardButton("✅ رفع الحظر",callback_data="adm#unban_user")],
        [InlineKeyboardButton("📈 تعديل سعر الصرف",callback_data="adm#edit_rate")],
        [InlineKeyboardButton("🗂️ عرض شجرة المتجر",callback_data="adm#tree")],
        [InlineKeyboardButton("➕ إضافة قسم",callback_data="adm#add_category"),InlineKeyboardButton("➕ إضافة منتج",callback_data="adm#add_product")],
        [InlineKeyboardButton("✏️ تعديل سعر منتج",callback_data="adm#edit_price"),InlineKeyboardButton("⛔ تعطيل/تفعيل منتج",callback_data="adm#toggle")],
        [InlineKeyboardButton("🗑️ حذف عنصر",callback_data="adm#delete_node"),InlineKeyboardButton("♻️ استرجاع محذوف",callback_data="adm#restore_node")],
        [InlineKeyboardButton("🧹 تنظيف الطلبات المعلقة",callback_data="adm#clean")],
        [InlineKeyboardButton("💾 نسخة احتياطية",callback_data="adm#backup")],
        [InlineKeyboardButton("📌 نشر لوحة التحكم في القناة",callback_data="adm#post_channel")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية",callback_data="main_menu")]
    ])

def get_echo_main_settings(db):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 رسالة الترحيب",callback_data="echo#welcome")],
        [InlineKeyboardButton("🤖 الردود التلقائية",callback_data="echo#auto_reply")],
        [InlineKeyboardButton("🔘 إدارة الأزرار الرئيسية",callback_data="echo#buttons")],
        [InlineKeyboardButton("💳 إعدادات الدفع والتحويل",callback_data="echo#payment")],
        [InlineKeyboardButton("📢 قناة الإشعارات",callback_data="echo#channel")],
        [InlineKeyboardButton("🌙 وضع الليل",callback_data="echo#night_mode")],
        [InlineKeyboardButton("💰 سعر الصرف",callback_data="adm#edit_rate")],
        [InlineKeyboardButton("📊 عرض الإحصائيات",callback_data="adm#stats")],
        [InlineKeyboardButton("👥 إدارة المستخدمين",callback_data="echo#users_mgmt")],
        [InlineKeyboardButton("🛒 إدارة المتجر",callback_data="echo#store_mgmt")],
        [InlineKeyboardButton("🤖 إدارة طلبات البوتات",callback_data="echo#bot_orders")],
        [InlineKeyboardButton("📋 سجل العمليات",callback_data="adm#log")],
        [InlineKeyboardButton("🛠️ وضع الصيانة",callback_data="adm#toggle_maintenance")],
        [InlineKeyboardButton("💾 نسخة احتياطية",callback_data="adm#backup")],
        [InlineKeyboardButton("🔙 رجوع للوحة التحكم",callback_data="open_panel")],
    ])

def get_users_management_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 بحث عن مستخدم",callback_data="adm#search_user")],
        [InlineKeyboardButton("📊 عرض كل الأرصدة",callback_data="adm#view_balances")],
        [InlineKeyboardButton("👥 عرض كل المستخدمين",callback_data="adm#users")],
        [InlineKeyboardButton("➕ إضافة رصيد",callback_data="adm#add_balance")],
        [InlineKeyboardButton("➖ خصم رصيد",callback_data="adm#sub_balance")],
        [InlineKeyboardButton("🚫 حظر مستخدم",callback_data="adm#ban_user")],
        [InlineKeyboardButton("✅ رفع الحظر",callback_data="adm#unban_user")],
        [InlineKeyboardButton("📤 تصدير المستخدمين",callback_data="adm#export_users")],
        [InlineKeyboardButton("🔙 رجوع للإعدادات",callback_data="echo#main")],
    ])

def get_store_management_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗂️ عرض شجرة المتجر",callback_data="adm#tree")],
        [InlineKeyboardButton("➕ إضافة قسم",callback_data="adm#add_category")],
        [InlineKeyboardButton("➕ إضافة منتج",callback_data="adm#add_product")],
        [InlineKeyboardButton("✏️ تعديل سعر منتج",callback_data="adm#edit_price")],
        [InlineKeyboardButton("⛔ تعطيل/تفعيل منتج",callback_data="adm#toggle")],
        [InlineKeyboardButton("🗑️ حذف عنصر",callback_data="adm#delete_node")],
        [InlineKeyboardButton("♻️ استرجاع محذوف",callback_data="adm#restore_node")],
        [InlineKeyboardButton("🔙 رجوع للإعدادات",callback_data="echo#main")],
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
    if page>0: nav_row.append(InlineKeyboardButton("⬅️ السابق",callback_data=f"{nav_prefix}#{page-1}"))
    if page<total_pages-1: nav_row.append(InlineKeyboardButton("التالي ➡️",callback_data=f"{nav_prefix}#{page+1}"))
    if nav_row: buttons.append(nav_row)
    buttons.append([InlineKeyboardButton("🔙 رجوع",callback_data=back_cb)])
    buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية",callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def back_cb_for(node):
    if node.get("parent"): return f"nav#{node['parent']}#0"
    return f"root#{node['section']}#0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id in db.get("banned",{}): await update.message.reply_text("🚫 حسابك محظور من استخدام هذا البوت. تواصل مع الدعم إن كنت تعتقد أن هذا خطأ."); return
    if user_id not in db["users"]: db["users"][user_id] = {"name":update.effective_user.first_name or "مستخدم","balance_usd":0,"joined":datetime.now().isoformat()}; save_db(db)
    balance = db["users"][user_id]["balance_usd"]; rate = db.get("exchange_rate",13800)
    name = safe_md(update.effective_user.first_name or "مستخدم")
    text = f"🔥 **أهلاً بك في بوت شام إن جيم** 🔥\n━━━━━━━━━━━━━━━━━━━━\n👤 مرحباً: {name}\n💰 رصيدك: ${balance:.2f}\n🇸🇾 بالليرة: {balance*rate:,.0f} ل.س\n📈 سعر الصرف: 1$ = {rate:,} ل.س\n━━━━━━━━━━━━━━━━━━━━\n⚠️ استخدم الأزرار للتنقل ❤️"
    if is_night_time(): text += "\n\n🌙 **ملاحظة:** نحن حالياً خارج أوقات الدعم المباشر، قد يتأخر الرد قليلاً وسنجيبك بأسرع وقت ممكن 🙏"
    await update.message.reply_text(text,reply_markup=main_menu)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db(); user_id = str(update.effective_user.id)
    if is_admin(db,user_id): await update.message.reply_text("✅ أنت مصادق بالفعل! استخدم /panel للوحة التحكم."); return
    clear_awaiting(context.user_data); context.user_data['awaiting_password'] = True
    await update.message.reply_text("🔐 اكتب كلمة السر للتحقق (مرة واحدة فقط، ستُحفظ دائماً):")

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db(); user_id = str(update.effective_user.id)
    if is_admin(db,user_id): await update.message.reply_text("🛸 **لوحة التحكم الإدارية الخارقة**",reply_markup=get_admin_main_panel(db))
    else: await update.message.reply_text("❌ ليس لديك صلاحية. استخدم /admin أولاً وأدخل كلمة السر.")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db(); user_id = str(update.effective_user.id)
    context.user_data.clear(); await update.message.reply_text("✅ تم إلغاء أي عملية معلقة.",reply_markup=main_menu)
    if is_admin(db,user_id):
        await update.message.reply_text("لديك صلاحية أدمن. إن أردت فتح لوحة التحكم اضغط الزر:",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛸 فتح لوحة التحكم",callback_data="open_panel")]]))

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) == ADMIN_CHANNEL_ID:
        await notify_admin_dm(context,"⚠️ **انتبه:** كتبت رداً داخل القناة نفسها ولن يصل للزبون!\nالرجاء الرد **هنا في هذه المحادثة الخاصة معي** وليس داخل القناة.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = str(update.effective_user.id); text = update.message.text; db = load_db(); ud = context.user_data
    if user_id in db.get("banned",{}) and not is_admin(db,user_id): await update.message.reply_text("🚫 حسابك محظور من استخدام هذا البوت."); return
    if db.get("bot_maintenance",False) and not is_admin(db,user_id): await update.message.reply_text("🛠️ البوت حالياً في وضع الصيانة، الرجاء المحاولة لاحقاً. نعتذر عن الإزعاج 🙏"); return

    if ud.get('awaiting_charge_proof'):
        amount=ud.get('charge_amount'); usd_amount=ud.get('charge_usd_amount'); currency=ud.get('charge_currency','usd')
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"charge","user_id":user_id,"usd_amount":usd_amount,"amount":amount,"currency":currency,"ref":text}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"🏦 **طلب شحن رصيد (برقم العملية)**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n💰 {amount} {'$' if currency=='usd' else 'ل.س'} = **${usd_amount:.2f}**\n🧾 رقم/مرجع العملية: {safe_md(text)}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ قبول وإضافة الرصيد",callback_data=f"charge_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"charge_no#{order_id}")]]))
        ud['awaiting_charge_proof']=False; await update.message.reply_text(f"🚀 تم إرسال طلب الشحن (رقم {order_id}) للإدارة.\nℹ️ يمكنك أيضاً إرسال صورة الوصل بدلاً من رقم العملية إن أردت."); return

    if text == '🏪 المتجر': await update.message.reply_text("🛍️ اختر القسم:",reply_markup=store_menu); return
    if text == '💳 المحفظة':
        balance=get_balance(db,user_id)
        await update.message.reply_text(f"💳 **رصيدك الحالي:**\n💰 ${balance:.2f}",reply_markup=wallet_menu); return
    if text == '💰 استرجاع الأموال': await update.message.reply_text("💰 اختر عملة الاسترجاع:",reply_markup=refund_menu); return
    if text == '🤖 إنشاء بوت':
        clear_awaiting(ud); ud['awaiting_bot_desc']=True
        await update.message.reply_text("🤖 اكتب مواصفات البوت الذي تريده:",reply_markup=CANCEL_BTN); return
    if text == '⚙️ الإعدادات': await update.message.reply_text(f"⚙️ **الإعدادات**\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 `{user_id}`"); return
    if text == '📞 الدعم الفني':
        await update.message.reply_text(
            f"📞 **الدعم الفني**\nللتواصل المباشر: {DEVELOPER_USERNAME}\nأو أرسل شكواك/استفسارك مباشرة من هنا:",
            reply_markup=support_menu
        )
        return

    if ud.get('awaiting_password'):
        ud['awaiting_password']=False
        if text.strip()==ADMIN_PASSWORD:
            if user_id not in db['authenticated_admins']: db['authenticated_admins'].append(user_id); save_db(db)
            await update.message.reply_text("✅ تم التحقق نهائياً! استخدم /panel للوحة التحكم في أي وقت لاحقاً بدون كلمة سر.")
            return
        else:
            await update.message.reply_text("❌ كلمة سر خاطئة!")
            return

    if ud.get('awaiting_complaint'):
        ud['awaiting_complaint'] = False
        db['stats']['complaints'] += 1
        log_activity(db, f"شكوى جديدة من {user_id}")
        save_db(db)
        try:
            await context.bot.send_message(ADMIN_CHANNEL_ID, f"📩 **شكوى / استفسار جديد**\n━━━━━━━━━━━━━━━━━━━━\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n\n📝 {safe_md(text)}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ الرد على الزبون", callback_data=f"reply_user#{user_id}")]]))
            await update.message.reply_text("✅ تم استلام رسالتك وسيتم الرد عليك بأقرب وقت ممكن 🙏")
        except:
            await update.message.reply_text("✅ تم استلام رسالتك وسيتم الرد عليك بأقرب وقت ممكن 🙏")
        return

    if ud.get('awaiting_reply_to_user'):
        target_id=ud.get('reply_target_id'); ud['awaiting_reply_to_user']=False
        try: await context.bot.send_message(target_id,f"💬 **رد الدعم الفني:**\n{text}"); await update.message.reply_text(f"✅ تم إرسال الرد إلى {target_id}")
        except Exception as e: await update.message.reply_text(f"❌ فشل إرسال الرد: {e}"); return

    if ud.get('awaiting_broadcast'):
        ud['awaiting_broadcast']=False; await update.message.reply_text("🚀 جاري الإرسال..."); count=0
        for uid in db["users"]:
            try: await context.bot.send_message(uid,f"📢 **إعلان عام**\n━━━━━━━━━━━━━━━━━━━━\n{text}"); count+=1
            except: pass
        await update.message.reply_text(f"✅ تم إرسال الإعلان إلى {count} مستخدم."); return

    if ud.get('awaiting_add_balance'):
        try:
            parts=text.split('|'); target_id,amount=parts[0].strip(),float(parts[1].strip())
            if amount<=0 or target_id not in db["users"]: raise ValueError
            update_balance(db,target_id,amount); log_activity(db,f"إضافة يدوية ${amount} لـ {target_id} من الأدمن"); save_db(db)
            await update.message.reply_text(f"✅ تم إضافة ${amount} إلى {safe_md(db['users'][target_id]['name'])}")
            await context.bot.send_message(target_id,f"🎉 تم إضافة ${amount} إلى محفظتك!")
        except: await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم: `آيدي|المبلغ` — حاول مجدداً",reply_markup=CANCEL_BTN); return
        ud['awaiting_add_balance']=False; return

    if ud.get('awaiting_sub_balance'):
        try:
            parts=text.split('|'); target_id,amount=parts[0].strip(),float(parts[1].strip())
            if amount<=0 or target_id not in db["users"]: raise ValueError
            update_balance(db,target_id,-amount); log_activity(db,f"خصم يدوي ${amount} من {target_id} من الأدمن"); save_db(db)
            await update.message.reply_text(f"✅ تم خصم ${amount} من {safe_md(db['users'][target_id]['name'])}")
            await context.bot.send_message(target_id,f"⚠️ تم خصم ${amount} من محفظتك من قبل الإدارة.")
        except: await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم: `آيدي|المبلغ` — حاول مجدداً",reply_markup=CANCEL_BTN); return
        ud['awaiting_sub_balance']=False; return

    if ud.get('awaiting_ban_user'):
        target_id=text.strip()
        if target_id not in db["users"]: await update.message.reply_text("❌ لا يوجد مستخدم بهذا المعرف.",reply_markup=CANCEL_BTN); return
        db.setdefault("banned",{})[target_id]=True; log_activity(db,f"حظر المستخدم {target_id}"); save_db(db)
        await update.message.reply_text(f"🚫 تم حظر `{target_id}`"); ud['awaiting_ban_user']=False; return

    if ud.get('awaiting_unban_user'):
        target_id=text.strip(); db.setdefault("banned",{}).pop(target_id,None); log_activity(db,f"رفع الحظر عن {target_id}"); save_db(db)
        await update.message.reply_text(f"✅ تم رفع الحظر عن `{target_id}`"); ud['awaiting_unban_user']=False; return

    if ud.get('awaiting_search_user'):
        target=text.strip(); info=db['users'].get(target); ud['awaiting_search_user']=False
        if not info: await update.message.reply_text("❌ لا يوجد مستخدم بهذا المعرف."); return
        history=db.get('user_history',{}).get(target,[]); hist_text="\n".join([f"{h['date'][:10]} - {h['type']}: ${h['amount']:.2f}" for h in history[-10:]]) or "لا يوجد"
        await update.message.reply_text(f"🔎 **بيانات المستخدم**\n🆔 `{target}`\n👤 {safe_md(info.get('name','مجهول'))}\n💰 ${info.get('balance_usd',0):.2f}\n🚫 محظور: {'نعم' if target in db.get('banned',{}) else 'لا'}\n📅 انضم: {info.get('joined','?')[:10]}\n\n📋 **آخر العمليات:**\n{hist_text}"); return

    if ud.get('awaiting_search_bot_order'):
        query_val=text.strip(); ud['awaiting_search_bot_order']=False; bot_orders=db.get('bot_orders',{}); found=[]
        if query_val in bot_orders: found=[(query_val,bot_orders[query_val])]
        else: found=[(oid,o) for oid,o in bot_orders.items() if o.get('user_id')==query_val]
        if not found: await update.message.reply_text("❌ لم يتم إيجاد أي طلب بوت بهذا المعرف."); return
        for oid,o in found[:5]:
            price_txt=f"${o['price']:.2f}" if o.get('price') is not None else "غير محدد"
            msg=f"🤖 **طلب بوت** `{oid}`\n👤 الزبون: `{o.get('user_id')}`\n💬 التواصل: {safe_md(o.get('contact',''))}\n📝 الوصف: {safe_md(o.get('desc',''))}\n🖥️ السيرفر: {safe_md(o.get('srv_name',''))}\n💰 السعر: {price_txt}\n📌 الحالة: {o.get('status')}\n🗒️ التفاصيل المحفوظة:\n{safe_md(o.get('details') or 'لا يوجد')}"
            buttons=[]
            if o.get('file_id'): buttons.append([InlineKeyboardButton("📂 إعادة إرسال الملف للزبون",callback_data=f"resend_botfile#{oid}")])
            await update.message.reply_text(msg,reply_markup=InlineKeyboardMarkup(buttons) if buttons else None); return

    if ud.get('awaiting_admin_notes'): db['admin_notes']=text; save_db(db); ud['awaiting_admin_notes']=False; await update.message.reply_text("✅ تم تحديث ملاحظات الإدارة."); return

    if ud.get('awaiting_new_rate'):
        try:
            r=float(text)
            if r<=0: raise ValueError
            db['exchange_rate']=r; save_db(db); await update.message.reply_text(f"✅ تم تعديل سعر الصرف إلى {r:,} ل.س")
        except: await update.message.reply_text("❌ اكتب رقماً صحيحاً! ",reply_markup=CANCEL_BTN); return
        ud['awaiting_new_rate']=False; return

    if ud.get('awaiting_add_category'):
        try:
            parts=text.split('|'); parent_raw,section,name=parts[0].strip(),parts[1].strip(),parts[2].strip()
            parent=None if parent_raw.lower()=='root' else parent_raw
            if section not in db['catalog_roots'] or (parent and parent not in db['catalog']): raise ValueError
            nid=new_node_id(db,"x")
            db['catalog'][nid]={"name":f"📁 {name}","section":section,"parent":parent,"type":"folder","kind":None,"price":None,"active":True,"deleted":False,"children":[],"warning":None}
            if parent: db['catalog'][parent]['children'].append(nid)
            else: db['catalog_roots'][section].append(nid)
            save_db(db); await update.message.reply_text(f"✅ تم إضافة القسم [{name}] بمعرف `{nid}`")
        except: await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم:\n`parent_id_او_root|games_او_cards_او_numbers|الاسم`.",reply_markup=CANCEL_BTN); return
        ud['awaiting_add_category']=False; return

    if ud.get('awaiting_add_product'):
        try:
            parts=text.split('|'); parent,kind,name,price=parts[0].strip(),parts[1].strip(),parts[2].strip(),float(parts[3].strip())
            if parent not in db['catalog'] or price<=0 or kind not in ('game_code','card','whatsapp_number','telegram_number'): raise ValueError
            nid=new_node_id(db,"x")
            db['catalog'][nid]={"name":f"🎯 {name} ~ {price}$","section":db['catalog'][parent]['section'],"parent":parent,"type":"product","kind":kind,"price":price,"active":True,"deleted":False,"children":[],"warning":None}
            db['catalog'][parent]['children'].append(nid); save_db(db)
            await update.message.reply_text(f"✅ تم إضافة المنتج [{name}] بمعرف `{nid}`")
        except: await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم:\n`parent_id|kind|الاسم|السعر`\nkind: game_code / card / whatsapp_number / telegram_number.",reply_markup=CANCEL_BTN); return
        ud['awaiting_add_product']=False; return

    if ud.get('awaiting_edit_price'):
        try:
            parts=text.split('|'); nid,price=parts[0].strip(),float(parts[1].strip())
            node=db['catalog'][nid]; node['price']=price; node['active']=True
            base=node['name'].split(' ~ ')[0]; node['name']=base+f" ~ {price}$"; save_db(db)
            await update.message.reply_text(f"✅ تم تعديل سعر `{nid}` إلى {price}$ وتفعيله.")
        except: await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم: `node_id|السعر_الجديد`.",reply_markup=CANCEL_BTN); return
        ud['awaiting_edit_price']=False; return

    if ud.get('awaiting_toggle'):
        nid=text.strip(); node=db['catalog'].get(nid)
        if not node: await update.message.reply_text("❌ لا يوجد عنصر بهذا المعرف.",reply_markup=CANCEL_BTN); return
        node['active']=not node.get('active',True); save_db(db)
        await update.message.reply_text(f"✅ الحالة الآن: {'مفعّل' if node['active'] else 'معطّل'} لـ `{nid}`"); ud['awaiting_toggle']=False; return

    if ud.get('awaiting_delete_node'):
        nid=text.strip(); node=db['catalog'].get(nid)
        if not node: await update.message.reply_text("❌ لا يوجد عنصر.",reply_markup=CANCEL_BTN); return
        node['deleted']=True; save_db(db); await update.message.reply_text(f"🗑️ تم حذف `{nid}` (يمكن استرجاعه لاحقاً)."); ud['awaiting_delete_node']=False; return

    if ud.get('awaiting_restore_node'):
        nid=text.strip(); node=db['catalog'].get(nid)
        if not node: await update.message.reply_text("❌ لا يوجد عنصر.",reply_markup=CANCEL_BTN); return
        node['deleted']=False; save_db(db); await update.message.reply_text(f"♻️ تم استرجاع `{nid}`."); ud['awaiting_restore_node']=False; return

    if ud.get('awaiting_charge'):
        try:
            amount=float(text)
            if amount<=0: raise ValueError
            currency=ud.get('charge_currency','usd'); rate=db.get('exchange_rate',13800)
            usd_amount=amount if currency=='usd' else (amount/rate)
            ud['charge_amount']=amount; ud['charge_usd_amount']=usd_amount; ud['awaiting_charge_proof']=True
            await update.message.reply_text(f"📸 المبلغ: {amount} {'$' if currency=='usd' else 'ل.س'} = **${usd_amount:.2f}**\n\n💳 **معلومات التحويل:**\n🏦 شام كوس: `{SYRIA_CASH_NUMBER}`\n👤 الاسم: {SYRIA_CASH_NAME}\n\n📤 أرسل الآن **صورة الوصل** أو **اكتب رقم/مرجع العملية** لتأكيد طلبك:",reply_markup=CANCEL_BTN)
        except: await update.message.reply_text("❌ اكتب رقماً صحيحاً! ",reply_markup=CANCEL_BTN); return
        ud['awaiting_charge']=False; return

    if ud.get('awaiting_refund'):
        try:
            amount=float(text)
            if amount<=0: raise ValueError
            currency=ud.get('refund_currency','usd'); usd_amount=amount if currency=='usd' else amount/db.get('exchange_rate',13800)
            balance=get_balance(db,user_id)
            if balance<usd_amount: await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ لهذا المبلغ (${usd_amount:.2f})!"); ud['awaiting_refund']=False; return
            ud['refund_amount']=amount; ud['refund_usd_amount']=usd_amount; ud['awaiting_refund']=False
            btn=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد الطلب",callback_data="confirm_refund")],[InlineKeyboardButton("❌ إلغاء",callback_data="cancel_flow")]])
            await update.message.reply_text(f"💰 المبلغ: {amount} {'$' if currency=='usd' else 'ل.س'} = **${usd_amount:.2f}**\n\n📝 **للاسترجاع:** سيُطلب منك إدخال رقم شام كوس + اسمك الكامل\n\nهل تريد تأكيد طلب الاسترجاع؟",reply_markup=btn)
        except: await update.message.reply_text("❌ اكتب رقماً صحيحاً! ",reply_markup=CANCEL_BTN); return
        return

    if ud.get('awaiting_refund_info'):
        refund_info=text; ud['refund_info']=refund_info; ud['awaiting_refund_info']=False
        amount=ud.get('refund_amount'); usd_amount=ud.get('refund_usd_amount'); currency=ud.get('refund_currency','usd')
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"refund","user_id":user_id,"amount":usd_amount,"refund_info":refund_info}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"💰 **طلب استرجاع أموال**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n💵 المبلغ المدخل: {amount} {'$' if currency=='usd' else 'ل.س'}\n💵 المعادل بالدولار: ${usd_amount:.2f}\n📝 شام كوس: {safe_md(refund_info)}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ موافقة",callback_data=f"refund_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"refund_no#{order_id}")]]))
        await update.message.reply_text(f"✅ تم إرسال طلب الاسترجاع (رقم {order_id}) للإدارة."); return

    if ud.get('awaiting_game_id'):
        game_id=text; node_id=ud.get('pending_node_id'); node=db['catalog'].get(node_id); ud['awaiting_game_id']=False
        if not node: await update.message.reply_text("❌ حدث خطأ، حاول من جديد."); return
        ud['pending_game_id']=game_id
        btn=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد الشراء",callback_data=f"confirm_game_buy#{node_id}")],[InlineKeyboardButton("❌ إلغاء",callback_data="cancel_flow")]])
        await update.message.reply_text(f"🎁 {safe_md(node['name'])}\n💰 السعر: ${node['price']}\n🆔 آيدي اللعبة: {safe_md(game_id)}\n\n⚠️ تأكد من صحة الآيدي جيداً قبل التأكيد.\nهل تريد تأكيد الطلب؟",reply_markup=btn); return

    if ud.get('awaiting_phone'):
        ud['phone_number']=text; ud['awaiting_phone']=False; ud['awaiting_phone_amount']=True
        await update.message.reply_text("✍️ اكتب المبلغ بالليرة:"); return

    if ud.get('awaiting_phone_amount'):
        try:
            amount=float(text)
            if amount<=0: raise ValueError
            rate=db.get('exchange_rate',13800); usd_amount=amount/rate; balance=get_balance(db,user_id)
            if balance<usd_amount: await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!"); ud['awaiting_phone_amount']=False; return
            ud['phone_amount']=amount; ud['phone_usd_amount']=usd_amount; ud['awaiting_phone_amount']=False
            btn=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد الشحن",callback_data="confirm_phone_order")],[InlineKeyboardButton("❌ إلغاء",callback_data="cancel_flow")]])
            await update.message.reply_text(f"📱 **مراجعة طلب شحن الهاتف**\n📞 الرقم: {safe_md(ud.get('phone_number',''))}\n📶 الشبكة: {ud.get('card_type')}\n💰 المبلغ: {amount:,.0f} ل.س (${usd_amount:.2f})\n\nتأكد من صحة رقم الهاتف قبل التأكيد. هل تريد المتابعة؟",reply_markup=btn)
        except: await update.message.reply_text("❌ اكتب رقماً صحيحاً! ",reply_markup=CANCEL_BTN); return
        return

    if ud.get('awaiting_bot_desc'): ud['bot_desc']=text; ud['awaiting_bot_desc']=False; ud['awaiting_bot_contact']=True; await update.message.reply_text("✍️ أرسل رقم تواصلك:",reply_markup=CANCEL_BTN); return
    if ud.get('awaiting_bot_contact'):
        ud['bot_contact']=text; ud['awaiting_bot_contact']=False
        server_btn=InlineKeyboardMarkup([[InlineKeyboardButton("🔥 سيرفر قوي 24 ساعة (5$/شهر + أسبوع مجاناً)",callback_data="srv#strong")],[InlineKeyboardButton("💤 سيرفر عادي 12-18 ساعة (2$/شهر)",callback_data="srv#normal")]])
        await update.message.reply_text("🖥️ **اختر نوع السيرفر:**",reply_markup=server_btn); return

    if ud.get('awaiting_bot_price'):
        target_id=ud.get('bot_target_id'); order_id=ud.get('bot_order_id'); ud['awaiting_bot_price']=False
        m=re.search(r'(\d+(\.\d+)?)',text)
        if not m: await update.message.reply_text("❌ لم أتمكن من إيجاد رقم بالسعر! اكتب مثلاً: `10$` أو `10` — حاول مجدداً.",reply_markup=CANCEL_BTN); return
        price=float(m.group(1))
        order=db.get('bot_orders',{}).get(order_id)
        if order: order['price']=price; save_db(db)
        pay_btn=InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ موافقة ودفع ${price:.2f}",callback_data=f"bot_pay#{order_id}")]])
        await context.bot.send_message(target_id,f"💰 **السعر المتفق عليه لطلب البوت:** ${price:.2f}\nاضغط الزر أدناه للموافقة والدفع من محفظتك:",reply_markup=pay_btn)
        await update.message.reply_text(f"✅ تم إرسال السعر (${price:.2f}) إلى {target_id} مع زر الدفع."); return

    if ud.get('awaiting_bot_time'):
        target_id=ud.get('bot_target_id'); ud['awaiting_bot_time']=False
        await context.bot.send_message(target_id,f"⏰ **الوقت المتوقع:** {text}")
        await update.message.reply_text(f"✅ تم إرسال الوقت إلى {target_id}"); return

    if ud.get('awaiting_bot_notes'):
        order_id=ud.get('bot_order_id'); ud['awaiting_bot_notes']=False
        order=db.get('bot_orders',{}).get(order_id)
        if not order: await update.message.reply_text("❌ الطلب غير موجود."); return
        existing=order.get('details',''); order['details']=(existing+"\n"+text).strip() if existing else text
        save_db(db); await update.message.reply_text(f"✅ تم حفظ التفاصيل لطلب `{order_id}`."); return

    if ud.get('awaiting_delivery_code'):
        order_id=ud.get('delivery_order_id'); order=db['pending_orders'].get(order_id); ud['awaiting_delivery_code']=False
        if not order: await update.message.reply_text("❌ الطلب غير موجود أو تم تسليمه مسبقاً."); return
        target_id=order['user_id']
        delivery_text=f"✅ **تم تفعيل طلبك!**\n━━━━━━━━━━━━━━━━━━━━\n🎁 المنتج: {safe_md(order.get('item_name','رقم/بطاقة'))}\n📋 رقم الطلب: {order_id}\n\n🎟️ **الكود/التفاصيل:**\n{safe_md(text)}"
        if order.get('kind')=='game_code': delivery_text+=REDEMPTION_INSTRUCTIONS
        try:
            await context.bot.send_message(target_id,delivery_text); await update.message.reply_text(f"✅ تم تسليم الطلب (رقم {order_id}) للزبون بنجاح.")
            db['stats']['purchases']+=1; log_activity(db,f"تسليم طلب شراء #{order_id} لـ {target_id}")
            del db['pending_orders'][order_id]; save_db(db)
        except Exception as e: await update.message.reply_text(f"❌ فشل الإرسال للزبون: {e}\nحاول مجدداً."); ud['awaiting_delivery_code']=True; ud['delivery_order_id']=order_id; return

    if ud.get('awaiting_bot_file'):
        target_id=ud.get('bot_target_id'); order_id=ud.get('bot_order_id'); ud['awaiting_bot_file']=False
        order=db.get('bot_orders',{}).get(order_id)
        if order: order['file_text']=text; save_db(db)
        await context.bot.send_message(target_id,f"📂 **ملف البوت:**\n{text}")
        await update.message.reply_text(f"✅ تم إرسال الملف (نص) إلى {target_id} وتم حفظه لطلب `{order_id}` لإعادة الإرسال لاحقاً."); return

    await update.message.reply_text("⚠️ لم أفهم طلبك، استخدم الأزرار من القائمة. (أو اضغط /cancel)",reply_markup=CANCEL_BTN)

async def handle_photo_and_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    user_id=str(update.effective_user.id); db=load_db(); ud=context.user_data

    if ud.get('awaiting_charge_proof') and update.message.photo:
        amount=ud.get('charge_amount'); usd_amount=ud.get('charge_usd_amount'); currency=ud.get('charge_currency','usd')
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"charge","user_id":user_id,"usd_amount":usd_amount,"amount":amount,"currency":currency}
        save_db(db)
        await context.bot.send_photo(ADMIN_CHANNEL_ID,update.message.photo[-1].file_id,caption=f"🏦 **طلب شحن رصيد**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n💰 {amount} {'$' if currency=='usd' else 'ل.س'} = **${usd_amount:.2f}**",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ قبول وإضافة الرصيد",callback_data=f"charge_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"charge_no#{order_id}")]]))
        ud['awaiting_charge_proof']=False; await update.message.reply_text(f"🚀 تم إرسال طلب الشحن (رقم {order_id}) للإدارة."); return

    if ud.get('awaiting_bot_file') and update.message.document:
        target_id=ud.get('bot_target_id'); order_id=ud.get('bot_order_id'); ud['awaiting_bot_file']=False
        order=db.get('bot_orders',{}).get(order_id)
        if order: order['file_id']=update.message.document.file_id; order['file_name']=update.message.document.file_name; save_db(db)
        await context.bot.send_document(target_id,update.message.document.file_id,caption="📂 تفضل ملف البوت الخاص بك جاهزاً!")
        await update.message.reply_text(f"✅ تم إرسال الملف إلى {target_id} وتم حفظه لطلب `{order_id}` لإعادة الإرسال لاحقاً."); return

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query; await query.answer(); data=query.data; user_id=str(update.effective_user.id); db=load_db(); ud=context.user_data

    if data=="cancel_flow": clear_awaiting(ud); await query.edit_message_text("✅ تم إلغاء العملية."); return

    if data.startswith("resend_botfile#"):
        if not is_admin(db,user_id): await query.answer("❌ غير مصرح لك",show_alert=True); return
        order_id=data.split('#')[1]; order=db.get('bot_orders',{}).get(order_id)
        if not order or not order.get('file_id'): await query.answer("❌ لا يوجد ملف محفوظ لهذا الطلب",show_alert=True); return
        try: await context.bot.send_document(order['user_id'],order['file_id'],caption="📂 تفضل ملف البوت الخاص بك مجدداً!"); await query.answer("✅ تم إعادة الإرسال",show_alert=True)
        except Exception as e: await query.answer(f"❌ فشل الإرسال: {e}",show_alert=True); return

    if data=="open_panel":
        if not is_admin(db,user_id): await query.edit_message_text("❌ ليس لديك صلاحية."); return
        await query.edit_message_text("🛸 **لوحة التحكم الإدارية الخارقة**",reply_markup=get_admin_main_panel(db)); return

    if data.startswith("adm#"):
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح لك. استخدم /admin وأدخل كلمة السر."); return
        action=data.split('#')[1]

        if action=="stats":
            total_users=len(db["users"]); total_balance=sum(u.get("balance_usd",0) for u in db["users"].values())
            total_orders=len(db.get("pending_orders",{})); s=db.get("stats",{})
            await query.edit_message_text(f"📊 **الإحصائيات الشاملة**\n━━━━━━━━━━━━━━━━━━━━\n👥 المستخدمين: {total_users}\n💰 إجمالي الأرصدة: ${total_balance:.2f}\n📦 الطلبات المعلقة الآن: {total_orders}\n━━━━━━━━━━━━━━━━━━━━\n🛒 عمليات شراء مكتملة: {s.get('purchases',0)}\n💸 عمليات استرجاع: {s.get('refunds',0)}\n💳 عمليات إيداع: {s.get('deposits',0)}\n📩 شكاوى/استفسارات: {s.get('complaints',0)}"); return
        if action=="log": log=db.get("activity_log",[])[-15:]; await query.edit_message_text("📋 **آخر العمليات**\n━━━━━━━━━━━━━━━━━━━━\n"+("\n".join(log) if log else "لا يوجد سجل بعد.")); return
        if action=="pending_list":
            orders=db.get("pending_orders",{})
            if not orders: await query.edit_message_text("📦 لا يوجد طلبات معلقة حالياً."); return
            lines=["📦 **الطلبات المعلقة**\n━━━━━━━━━━━━━━━━━━━━"]
            for oid,o in list(orders.items())[:25]: lines.append(f"`{oid}` — {o.get('type')} — {o.get('user_id')} — {safe_md(str(o.get('item_name',o.get('amount',''))))}")
            await query.edit_message_text("\n".join(lines)); return
        if action=="broadcast": clear_awaiting(ud); ud['awaiting_broadcast']=True; await query.edit_message_text("✍️ اكتب رسالة الإعلان :",reply_markup=CANCEL_BTN); return
        if action=="add_balance": clear_awaiting(ud); ud['awaiting_add_balance']=True; await query.edit_message_text("✍️ اكتب: `آيدي|المبلغ` ",reply_markup=CANCEL_BTN); return
        if action=="sub_balance": clear_awaiting(ud); ud['awaiting_sub_balance']=True; await query.edit_message_text("✍️ اكتب: `آيدي|المبلغ` لخصمه ",reply_markup=CANCEL_BTN); return
        if action=="ban_user": clear_awaiting(ud); ud['awaiting_ban_user']=True; await query.edit_message_text("✍️ اكتب آيدي المستخدم لحظره :",reply_markup=CANCEL_BTN); return
        if action=="unban_user": clear_awaiting(ud); ud['awaiting_unban_user']=True; await query.edit_message_text("✍️ اكتب آيدي المستخدم لرفع الحظر عنه :",reply_markup=CANCEL_BTN); return
        if action=="search_user": clear_awaiting(ud); ud['awaiting_search_user']=True; await query.edit_message_text("✍️ اكتب آيدي المستخدم :",reply_markup=CANCEL_BTN); return
        if action=="view_balances":
            s="💰 **الأرصدة**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid,info in list(db["users"].items())[:25]: s+=f"👤 {safe_md(info.get('name','مجهول'))} — ${info.get('balance_usd',0):.2f} (`{uid}`)\n"
            await query.edit_message_text(s or "لا يوجد مستخدمين."); return
        if action=="users":
            s="👥 **المستخدمين**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid,info in list(db["users"].items())[:25]: s+=f"`{uid}` — {safe_md(info.get('name','مجهول'))}\n"
            await query.edit_message_text(s or "لا يوجد مستخدمين."); return
        if action=="users_list":
            s=f"👥 **المستخدمين ({len(db['users'])})**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid,info in list(db["users"].items())[:25]: s+=f"`{uid}` — {safe_md(info.get('name','مجهول'))}\n"
            await query.edit_message_text(s or "لا يوجد مستخدمين."); return
        if action=="edit_rate": clear_awaiting(ud); ud['awaiting_new_rate']=True; await query.edit_message_text(f"📈 سعر الصرف الحالي: {db.get('exchange_rate',13800):,} ل.س\n✍️ اكتب السعر الجديد :",reply_markup=CANCEL_BTN); return
        if action=="tree":
            lines=["🗂️ **شجرة المتجر الكاملة** (المعرف: الاسم)\n━━━━━━━━━━━━━━━━━━━━"]
            for section,roots in db['catalog_roots'].items():
                lines.append(f"\n📦 __{section}__")
                def walk(nid,depth):
                    node=db['catalog'].get(nid)
                    if not node: return
                    flag=""
                    if node.get('deleted'): flag=" 🗑️محذوف"
                    elif node['type']=='product' and not node.get('active',True): flag="  ⛔معطّل"
                    price_txt=f" | {node['price']}$" if node.get('price') is not None else ""
                    lines.append(("  "*depth)+f"`{nid}` {safe_md(node['name'])}{price_txt}{flag}")
                    for c in node.get('children',[]): walk(c,depth+1)
                for r in roots: walk(r,1)
            full_text="\n".join(lines)
            if len(full_text)>3800: full_text=full_text[:3800]+"\n...\n(القائمة طويلة)"
            await query.edit_message_text(full_text); return
        if action=="add_category":
            clear_awaiting(ud); ud['awaiting_add_category']=True
            await query.edit_message_text("✍️ اكتب بالصيغة:\n`parent_id_او_root|games_او_cards_او_numbers|الاسم`\n\nمثال (قسم رئيسي جديد): `root|games|لعبة جديدة`\nمثال (مجلد فرعي داخل g1): `g1|games|مجلد فرعي`",reply_markup=CANCEL_BTN); return
        if action=="add_product":
            clear_awaiting(ud); ud['awaiting_add_product']=True
            await query.edit_message_text("✍️ اكتب بالصيغة:\n`parent_id|kind|الاسم|السعر`\n\nkind: game_code / card / whatsapp_number / telegram_number\nمثال: `g3|game_code|كود 3200 شدة|45.5`",reply_markup=CANCEL_BTN); return
        if action=="edit_price": clear_awaiting(ud); ud['awaiting_edit_price']=True; await query.edit_message_text("✍️ اكتب بالصيغة: `node_id|السعر_الجديد`\nمثال: `g7|24.5`\n",reply_markup=CANCEL_BTN); return
        if action=="toggle": clear_awaiting(ud); ud['awaiting_toggle']=True; await query.edit_message_text("✍️ اكتب معرف العنصر (node_id) لتبديل حالته تفعيل/تعطيل :",reply_markup=CANCEL_BTN); return
        if action=="delete_node": clear_awaiting(ud); ud['awaiting_delete_node']=True; await query.edit_message_text("✍️ اكتب معرف العنصر (node_id) لحذفه (قابل للاسترجاع، ):",reply_markup=CANCEL_BTN); return
        if action=="restore_node": clear_awaiting(ud); ud['awaiting_restore_node']=True; await query.edit_message_text("✍️ اكتب معرف العنصر (node_id) لاسترجاعه :",reply_markup=CANCEL_BTN); return
        if action=="clean": db["pending_orders"]={}; save_db(db); await query.edit_message_text("🧹 تم تنظيف كل الطلبات المعلقة."); return
        if action=="search_bot_order": clear_awaiting(ud); ud['awaiting_search_bot_order']=True; await query.edit_message_text("✍️ اكتب رقم طلب البوت (order_id) أو آيدي الزبون للبحث عنه:",reply_markup=CANCEL_BTN); return
        if action=="toggle_maintenance": db['bot_maintenance']=not db.get('bot_maintenance',False); save_db(db); state="مفعّل 🛠️" if db['bot_maintenance'] else "متوقف ✅"; await query.edit_message_text(f"وضع الصيانة الآن: {state}\n(عند التفعيل، الزبائن العاديون لا يستطيعون استخدام البوت وتظهر لهم رسالة صيانة)."); return
        if action=="admin_notes": clear_awaiting(ud); ud['awaiting_admin_notes']=True; current=db.get('admin_notes','') or 'لا توجد ملاحظات بعد.'; await query.edit_message_text(f" 📝 **الملاحظات الحالية:**\n{safe_md(current)}\n\n✍️ اكتب ملاحظات جديدة لتحديثها:",reply_markup=CANCEL_BTN); return
        if action=="list_admins":
            admins=db.get('authenticated_admins',[]); lines=["👮 **الأدمنية المصادقين:**\n━━━━━━━━━━━━━━━━━━━━"]
            for a in admins: name=safe_md(db['users'].get(a,{}).get('name','غير معروف')); lines.append(f"`{a}` — {name}")
            await query.edit_message_text("\n".join(lines) if admins else "لا يوجد أدمنية مصادقين بعد."); return
        if action=="export_users":
            users_data=json.dumps(db.get('users',{}),indent=2,ensure_ascii=False)
            await query.edit_message_text("📤 جاري تصدير المستخدمين...")
            await context.bot.send_document(chat_id=user_id,document=users_data.encode('utf-8'),filename='users_export.json',caption=f"👥 كل المستخدمين ({len(db.get('users',{}))})"); return
        if action=="backup":
            backup_data=json.dumps(db,indent=2,ensure_ascii=False)
            await query.edit_message_text("💾 تم إنشاء نسخة احتياطية.")
            await context.bot.send_document(chat_id=user_id,document=backup_data.encode('utf-8'),filename='database_backup.json',caption="📂 نسخة احتياطية"); return
        if action=="post_channel":
            try: await context.bot.send_message(ADMIN_CHANNEL_ID,"🛸 **لوحة التحكم الإدارية**\nيمكن لأي أدمن مصادق استخدام هذه الأزرار مباشرة من هنا.",reply_markup=get_admin_main_panel(db)); await query.edit_message_text("✅ تم نشر لوحة التحكم في القناة.")
            except Exception as e: await query.edit_message_text(f"❌ فشل النشر في القناة: {e}"); return
        return

    # ============ قائمة Echo ============
    if data=="echo#main":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        await query.edit_message_text("🔧 **إعدادات البوت المتقدمة**",reply_markup=get_echo_main_settings(db)); return

    if data=="echo#welcome":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        clear_awaiting(ud); ud['awaiting_echo_welcome']=True
        await query.edit_message_text("✍️ اكتب رسالة الترحيب الجديدة:",reply_markup=CANCEL_BTN); return

    if data=="echo#auto_reply":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        clear_awaiting(ud); ud['awaiting_echo_auto_reply']=True
        await query.edit_message_text("✍️ اكتب الرد التلقائي الجديد:",reply_markup=CANCEL_BTN); return

    if data=="echo#buttons":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        await query.edit_message_text("🔘 **إدارة الأزرار**\n\nالأزرار الحالية:\n🏪 المتجر | 🤖 إنشاء بوت\n💳 المحفظة | 💰 استرجاع الأموال\n⚙️ الإعدادات | 📞 الدعم الفني\n\nللتعديل استخدم /panel ثم إدارة المتجر",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" 🔙 رجوع للإعدادات",callback_data="echo#main")]])); return

    if data=="echo#payment":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        await query.edit_message_text(f"💳 **إعدادات الدفع والتحويل**\n\n🏦 شام كوس: `{SYRIA_CASH_NUMBER}`\n👤 الاسم: {SYRIA_CASH_NAME}\n\nللتعديل: افتح الكود وعدل المتغيرات.",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للإعدادات",callback_data="echo#main")]])); return

    if data=="echo#channel":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        await query.edit_message_text(f"📢 **قناة الإشعارات**\n\nالقناة الحالية: `{ADMIN_CHANNEL_ID}`\n\nلتغيير القناة، عدل المتغير في الكود.",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للإعدادات",callback_data="echo#main")]])); return

    if data=="echo#night_mode":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        await query.edit_message_text(f"🌙 **وضع الليل**\n\nيبدأ: {NIGHT_START_HOUR}:00\nينتهي: {NIGHT_END_HOUR}:00\n\nلتغيير الوقت، عدل المتغيرات في الكود.",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للإعدادات",callback_data="echo#main")]])); return

    if data=="echo#users_mgmt":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        await query.edit_message_text("👥 **إدارة المستخدمين**",reply_markup=get_users_management_menu()); return

    if data=="echo#store_mgmt":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        await query.edit_message_text("🛒 **إدارة المتجر**",reply_markup=get_store_management_menu()); return

    if data=="echo#bot_orders":
        if not is_admin(db,user_id): await query.edit_message_text("❌ غير مصرح."); return
        bot_orders=db.get('bot_orders',{})
        if not bot_orders: await query.edit_message_text("🤖 لا يوجد طلبات بوت حالياً."); return
        lines=[f"🤖 **طلبات البوتات ({len(bot_orders)}):**\n"]
        for oid,o in list(bot_orders.items())[:15]: lines.append(f"`{oid}` - {safe_md(o.get('desc','')[:30])} - {o.get('status','?')}")
        await query.edit_message_text("\n".join(lines),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔎 بحث عن طلب",callback_data="adm#search_bot_order")],[InlineKeyboardButton("🔙 رجوع للإعدادات",callback_data="echo#main")]])); return

    # ============ الأزرار العادية ============
    if data.startswith("reply_user#"):
        if not is_admin(db,user_id): await query.answer("❌ غير مصرح لك",show_alert=True); return
        target_id=data.split('#')[1]; clear_awaiting(ud); ud['awaiting_reply_to_user']=True; ud['reply_target_id']=target_id
        await notify_admin_dm(context,f"✍️ اكتب الآن هنا ردك على المستخدم `{target_id}`:"); await query.answer("📩 تحقق من رسائلك الخاصة مع البوت لكتابة الرد",show_alert=True); return

    if data=="support#start": clear_awaiting(ud); ud['awaiting_complaint']=True; await query.edit_message_text("📝 اكتب شكواك أو استفسارك الآن بالتفصيل:"); return

    if data.startswith("root#"):
        parts=data.split('#'); section,page=parts[1],int(parts[2]) if len(parts)>2 else 0
        roots=db['catalog_roots'].get(section,[])
        title={"games":"🎮 اختر اللعبة:","cards":"🎟️ اختر البطاقة:","numbers":"📱 اختر النوع:"}.get(section,"اختر:")
        await query.edit_message_text(title,reply_markup=render_listing(db,roots,"store#back",f"root#{section}",page)); return

    if data=="store#phone": await query.edit_message_text("📱 **اختر شبكة الهاتف:**",reply_markup=phone_menu); return
    if data=="store#back": await query.edit_message_text("🛍️ **اختر القسم:**",reply_markup=store_menu); return

    if data.startswith("nav#"):
        parts=data.split('#'); nid,page=parts[1],int(parts[2]) if len(parts)>2 else 0
        node=db['catalog'].get(nid)
        if not node: await query.edit_message_text("⚠️ هذا القسم غير موجود."); return
        await query.edit_message_text(f"📁 **{safe_md(node['name'])}**",reply_markup=render_listing(db,node['children'],back_cb_for(node),f"nav#{nid}",page)); return

    if data.startswith("buy#"):
        nid=data.split('#')[1]; node=db['catalog'].get(nid)
        if not node or node.get('deleted') or not node.get('active',True) or node.get('price') is None: await query.edit_message_text("⚠️ هذا المنتج غير متوفر حالياً."); return
        balance=get_balance(db,user_id)
        if balance<node['price']: await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي لشراء [{safe_md(node['name'])}]!"); return
        if node['kind']=='game_code':
            clear_awaiting(ud); ud['pending_node_id']=nid; ud['awaiting_game_id']=True
            await query.edit_message_text(f"🎁 {safe_md(node['name'])}\n✍️ **أدخل الآيدي (ID) الخاص بك:**",reply_markup=CANCEL_BTN); return
        warn=node.get('warning','')
        btn=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد الشراء",callback_data=f"confirm_buy#{nid}")],[InlineKeyboardButton("❌ إلغاء",callback_data="cancel_flow")]])
        msg=f"{warn}\n\n🎁 {safe_md(node['name'])}\n💰 السعر: ${node['price']}\n\nهل تريد تأكيد الشراء؟" if warn else f"🎁 {safe_md(node['name'])}\n💰 السعر: ${node['price']}\n\nهل تريد تأكيد الشراء؟"
        await query.edit_message_text(msg,reply_markup=btn); return

    if data.startswith("confirm_buy#"):
        nid=data.split('#')[1]; node=db['catalog'].get(nid)
        if not node or node.get('deleted') or not node.get('active',True): await query.edit_message_text("⚠️ هذا المنتج غير متوفر."); return
        balance=get_balance(db,user_id)
        if balance<node['price']: await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي!"); return
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"purchase","user_id":user_id,"node_id":nid,"price":node['price'],"item_name":node['name'],"game_id":None,"kind":node['kind']}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"🛒 **طلب شراء جديد**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n🎁 {safe_md(node['name'])}\n💰 ${node['price']}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ موافقة وخصم",callback_data=f"order_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"order_no#{order_id}")]]))
        await query.edit_message_text(f"✅ تم إرسال طلبك (رقم {order_id}) للإدارة، بانتظار الموافقة."); return

    if data.startswith("confirm_game_buy#"):
        nid=data.split('#')[1]; node=db['catalog'].get(nid); game_id=ud.get('pending_game_id')
        if not node or node.get('deleted') or not node.get('active',True) or not game_id: await query.edit_message_text("⚠️ حدث خطأ، حاول الطلب من جديد."); return
        balance=get_balance(db,user_id)
        if balance<node['price']: await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي!"); return
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"purchase","user_id":user_id,"node_id":nid,"price":node['price'],"item_name":node['name'],"game_id":game_id,"kind":node['kind']}
        save_db(db); ud['pending_game_id']=None
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"🛒 **طلب شراء جديد**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n🎁 {safe_md(node['name'])}\n💰 ${node['price']}\n🆔 آيدي اللعبة: {safe_md(game_id)}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ موافقة وخصم",callback_data=f"order_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"order_no#{order_id}")]]))
        await query.edit_message_text(f"✅ تم إرسال طلبك (رقم {order_id}) للإدارة، بانتظار الموافقة."); return

    if data=="confirm_refund":
        amount=ud.get('refund_amount'); usd_amount=ud.get('refund_usd_amount'); currency=ud.get('refund_currency','usd')
        if amount is None or usd_amount is None: await query.edit_message_text("⚠️ حدث خطأ، حاول من جديد من قائمة استرجاع الأموال."); return
        balance=get_balance(db,user_id)
        if balance<usd_amount: await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لم يعد كافياً!"); return
        clear_awaiting(ud); ud['awaiting_refund_info']=True
        await query.edit_message_text(f"📝 **أدخل معلومات شام كوس لتحويل المبلغ:**\n\n💰 المبلغ: ${usd_amount:.2f}\n\n✍️ اكتب: `رقم_شام_كوس|الاسم_الكامل`\n\nمثال: `0999999999|أحمد محمد`",reply_markup=CANCEL_BTN); return

    if data=="confirm_phone_order":
        amount=ud.get('phone_amount'); usd_amount=ud.get('phone_usd_amount'); phone=ud.get('phone_number'); card_type=ud.get('card_type')
        if amount is None or usd_amount is None or not phone: await query.edit_message_text("⚠️ حدث خطأ، حاول من جديد من قائمة شحن الهاتف."); return
        balance=get_balance(db,user_id)
        if balance<usd_amount: await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!"); return
        order_id=generate_order_id()
        db['pending_orders'][order_id]={"type":"phone","user_id":user_id,"usd_amount":usd_amount,"syr_amount":amount,"phone":phone,"card_type":card_type}
        save_db(db)
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"📱 **طلب شحن هاتف**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n📞 {safe_md(phone)}\n📶 {card_type}\n💰 {amount:,.0f} ل.س (${usd_amount:.2f})",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ موافقة",callback_data=f"phone_ok#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"phone_no#{order_id}")]]))
        await query.edit_message_text(f"✅ تم إرسال طلب الشحن (رقم {order_id}) للإدارة."); return

    # ============ موافقة/رفض ============
    if data.startswith("order_ok#"):
        order_id=data.split('#')[1]; order=db['pending_orders'].get(order_id)
        if not order: await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً (ربما تمت معالجته مسبقاً)."); return
        target_id=order['user_id']; balance=get_balance(db,target_id)
        if balance<order['price']: await query.edit_message_text("❌ رصيد الزبون لم يعد كافياً!"); return
        update_balance(db,target_id,-order['price']); save_db(db)
        await query.edit_message_text(f"✅ تم خصم ${order['price']} من الزبون (رقم الطلب {order_id}).\n📩 تحقق من رسائلك الخاصة مع البوت لإدخال الكود.")
        clear_awaiting(ud); ud['awaiting_delivery_code']=True; ud['delivery_order_id']=order_id
        await notify_admin_dm(context,f"✍️ **اكتب الآن هنا** الكود/الرقم/المعلومات لتسليمها للزبون (طلب {order_id} — {safe_md(order.get('item_name',''))}):"); return

    if data.startswith("order_no#"): order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None); save_db(db); await query.edit_message_text(f"❌ تم رفض الطلب (رقم {order_id})"); return
    if data.startswith("charge_ok#"):
        order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None)
        if not order: await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً."); return
        update_balance(db,order['user_id'],order['usd_amount']); db['stats']['deposits']+=1; log_activity(db,f"إيداع #{order_id} لـ {order['user_id']} بقيمة ${order['usd_amount']:.2f}"); save_db(db)
        await query.edit_message_text(f"✅ تم قبول الشحن (رقم {order_id}) وإضافة ${order['usd_amount']:.2f}")
        await context.bot.send_message(order['user_id'],f"✅ تم شحن ${order['usd_amount']:.2f} إلى محفظتك (رقم {order_id})."); return
    if data.startswith("charge_no#"): order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None); save_db(db); await query.edit_message_text(f"❌ تم رفض طلب الشحن (رقم {order_id})"); return

    if data.startswith("refund_ok#"):
        order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None)
        if not order: await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً."); return
        update_balance(db,order['user_id'],-order['amount']); db['stats']['refunds']+=1; log_activity(db,f"استرجاع #{order_id} لـ {order['user_id']} بقيمة ${order['amount']:.2f}"); save_db(db)
        await query.edit_message_text(f"✅ تم قبول الاسترجاع (رقم {order_id}) وخصم ${order['amount']:.2f}")
        await context.bot.send_message(order['user_id'],f"✅ تم استرجاع ${order['amount']:.2f} وسيتم تحويلها لك (رقم {order_id})."); return
    if data.startswith("refund_no#"): order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None); save_db(db); await query.edit_message_text(f"❌ تم رفض طلب الاسترجاع (رقم {order_id})"); return

    if data.startswith("phone_ok#"):
        order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None)
        if not order: await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً."); return
        update_balance(db,order['user_id'],-order['usd_amount']); save_db(db)
        await query.edit_message_text(f"✅ تم قبول طلب شحن الهاتف (رقم {order_id})")
        await context.bot.send_message(order['user_id'],f"✅ **تم شحن هاتفك!**\n📋 رقم الطلب: {order_id}\n📞 {safe_md(order['phone'])}\n📶 {order['card_type']}\n💰 {order['syr_amount']:,.0f} ل.س"); return
    if data.startswith("phone_no#"): order_id=data.split('#')[1]; order=db['pending_orders'].pop(order_id,None); save_db(db); await query.edit_message_text(f"❌ تم رفض طلب الشحن (رقم {order_id})"); return

    if data.startswith("phone#"): card_type=data.split('#')[1]; ud['card_type']=card_type.upper(); clear_awaiting(ud); ud['awaiting_phone']=True; await query.edit_message_text(f"✍️ **أدخل رقم الهاتف** ({card_type.upper()}):",reply_markup=CANCEL_BTN); return
    if data.startswith("charge#"): currency=data.split('#')[1]; clear_awaiting(ud); ud['charge_currency']=currency; ud['awaiting_charge']=True; await query.edit_message_text(f"✍️ **أدخل المبلغ** {'بالدولار' if currency=='usd' else 'بالليرة السورية'}:",reply_markup=CANCEL_BTN); return
    if data.startswith("refund#"): currency=data.split('#')[1]; clear_awaiting(ud); ud['refund_currency']=currency; ud['awaiting_refund']=True; await query.edit_message_text(f"✍️ **أدخل المبلغ** {'بالدولار' if currency=='usd' else 'بالليرة السورية'} المراد استرجاعه:",reply_markup=CANCEL_BTN); return

    if data.startswith("srv#"):
        srv_type=data.split('#')[1]; srv_name="🔥 قوي 24 ساعة (5$/شهر + أسبوع مجاناً)" if srv_type=='strong' else "💤 عادي 12-18 ساعة (2$/شهر)"
        desc=ud.get('bot_desc','غير محدد'); contact=ud.get('bot_contact','غير محدد'); order_id=generate_order_id()
        db.setdefault('bot_orders',{})[order_id]={"user_id":user_id,"desc":desc,"contact":contact,"srv_name":srv_name,"price":None,"details":"","file_id":None,"file_name":None,"status":"pending"}
        save_db(db); await query.edit_message_text("🚀 جاري إرسال الطلب للإدارة...")
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"🤖 **طلب إنشاء بوت جديد**\n📋 رقم الطلب: {order_id}\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n💬 {safe_md(contact)}\n📝 {safe_md(desc)}\n🖥️ {srv_name}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 السعر (مع خصم من محفظة الزبون)",callback_data=f"bot_price#{user_id}#{order_id}")],[InlineKeyboardButton("⏰ الوقت",callback_data=f"bot_time#{user_id}#{order_id}")],[InlineKeyboardButton("📝 تفاصيل/ملاحظات",callback_data=f"bot_notes#{user_id}#{order_id}")],[InlineKeyboardButton("📂 ملف",callback_data=f"bot_file#{user_id}#{order_id}")],[InlineKeyboardButton("❌ رفض",callback_data=f"bot_reject#{user_id}#{order_id}")]]))
        ud['awaiting_bot_desc']=False; ud['awaiting_bot_contact']=False; return

    if data.startswith("bot_price#"):
        parts=data.split('#'); clear_awaiting(ud); ud['bot_target_id']=parts[1]; ud['bot_order_id']=parts[2]; ud['awaiting_bot_price']=True
        await query.edit_message_text(f"📩 تحقق من رسائلك الخاصة مع البوت لكتابة السعر (طلب {parts[2]}).")
        await notify_admin_dm(context,f"✍️ اكتب السعر الآن هنا للمستخدم `{parts[1]}` (طلب {parts[2]})، مثال: `10$` أو `10`:"); return

    if data.startswith("bot_time#"):
        parts=data.split('#'); clear_awaiting(ud); ud['bot_target_id']=parts[1]; ud['bot_order_id']=parts[2]; ud['awaiting_bot_time']=True
        await query.edit_message_text(f"📩 تحقق من رسائلك الخاصة مع البوت لكتابة الوقت (طلب {parts[2]}).")
        await notify_admin_dm(context,f"✍️ اكتب الوقت المتوقع الآن هنا للمستخدم `{parts[1]}` (طلب {parts[2]}):"); return

    if data.startswith("bot_notes#"):
        parts=data.split('#'); clear_awaiting(ud); ud['bot_target_id']=parts[1]; ud['bot_order_id']=parts[2]; ud['awaiting_bot_notes']=True
        await query.edit_message_text(f"📩 تحقق من رسائلك الخاصة مع البوت لكتابة التفاصيل/الملاحظات (طلب {parts[2]}).")
        await notify_admin_dm(context,f"📝 اكتب الآن التفاصيل/الملاحظات الخاصة بطلب `{parts[2]}` (تُحفظ ليمكنك الرجوع لها لاحقاً، لا تُرسل للزبون):"); return

    if data.startswith("bot_file#"):
        parts=data.split('#'); clear_awaiting(ud); ud['bot_target_id']=parts[1]; ud['bot_order_id']=parts[2]; ud['awaiting_bot_file']=True
        await query.edit_message_text(f"📩 تحقق من رسائلك الخاصة مع البوت لإرسال الملف (طلب {parts[2]}).")
        await notify_admin_dm(context,f"📤 أرسل ملف البوت الآن هنا (كـ Document) للمستخدم `{parts[1]}` (طلب {parts[2]}):"); return

    if data.startswith("bot_pay#"):
        order_id=data.split('#')[1]; order=db.get('bot_orders',{}).get(order_id)
        if not order or order['user_id']!=user_id: await query.edit_message_text("⚠️ هذا الطلب غير موجود."); return
        if order.get('status')=='paid': await query.edit_message_text("✅ تم دفع هذا الطلب مسبقاً."); return
        price=order.get('price')
        if price is None: await query.edit_message_text("⚠️ لم يتم تحديد سعر لهذا الطلب بعد."); return
        balance=get_balance(db,user_id)
        if balance<price: await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي لدفع ${price:.2f}. اشحن محفظتك أولاً."); return
        update_balance(db,user_id,-price); order['status']='paid'; db['stats']['purchases']+=1; log_activity(db,f"دفع طلب بوت #{order_id} من {user_id} بقيمة ${price:.2f}"); save_db(db)
        await query.edit_message_text(f"✅ تم خصم ${price:.2f} من محفظتك. سيتم التواصل معك لإكمال طلب البوت 🤖")
        await context.bot.send_message(ADMIN_CHANNEL_ID,f"💰 تم دفع طلب البوت (رقم {order_id}) من قبل الزبون `{user_id}` — تم خصم ${price:.2f}"); return

    if data.startswith("bot_reject#"):
        parts=data.split('#')
        order=db.get('bot_orders',{}).get(parts[2])
        if order:
            order['status']='rejected'
            save_db(db)
        await query.edit_message_text(f"❌ تم رفض طلب البوت (رقم {parts[2]})")
        await context.bot.send_message(parts[1],f"❌ عذراً، تم رفض طلب إنشاء البوت (رقم {parts[2]}).")
        return

    if data=="main_menu": await context.bot.send_message(chat_id=update.effective_chat.id,text="🎯 **القائمة الرئيسية**",reply_markup=main_menu); return

    await query.edit_message_text("⚠️ هذا الزر غير مفعل حالياً.")


# ==================== تشغيل البوت ====================
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
    print("🚀 البوت شغال بالبايثون!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
