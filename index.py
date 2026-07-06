import json
import os
import logging
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

# ==================== قاعدة البيانات ====================
def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "users": {},
            "banned": {},
            "muted": {},
            "exchange_rate": 14500,
            "admin_notes": "",
            "bot_maintenance": False,
            "orders": [],
            "bot_orders": [],
            "installments": [],
            "products": [],
            "custom_store": {
                "games": {
                    "🎮 ببجي موبايل": ["60 شدة - 1.20$", "325 شدة - 5.00$", "660 شدة - 10.00$", "1800 شدة - 25.00$"],
                    "🔥 فري فاير": ["100 دايموند - 2.00$", "200 دايموند - 4.00$", "400 دايموند - 7.00$"],
                    "🎮 روبلوكس": ["100 روبوكس - 1.50$", "500 روبوكس - 6.00$", "1000 روبوكس - 11.00$"]
                },
                "cards": {
                    "🎟️ بطاقات ستيم": ["فئة 5$ - 5.50$", "فئة 10$ - 11.00$"],
                    "🎟️ بطاقات إكس بوكس": ["فئة 10$ - 10.50$", "فئة 25$ - 26.00$"]
                }
            }
        }

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_balance(user_id):
    db = load_db()
    return db["users"].get(str(user_id), {}).get("balance_usd", 0)

def update_balance(user_id, amount):
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"name": "مستخدم", "balance_usd": 0, "joined": datetime.now().isoformat()}
    db["users"][uid]["balance_usd"] = db["users"][uid].get("balance_usd", 0) + amount
    save_db(db)

# ==================== القوائم الرئيسية ====================
main_menu = ReplyKeyboardMarkup([
    ['🏪 المتجر', '🤖 إنشاء بوت'],
    ['💳 المحفظة', '💰 استرجاع الأموال'],
    ['⚙️ الإعدادات', '📞 الدعم الفني']
], resize_keyboard=True)

# ==================== قوائم المتجر ====================
store_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎮 قسم الألعاب", callback_data="store#games")],
    [InlineKeyboardButton("🎟️ قسم البطاقات", callback_data="store#cards")],
    [InlineKeyboardButton("📱 شحن رصيد هاتف", callback_data="store#phone")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

games_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎮 ببجي موبايل", callback_data="game#ببجي موبايل")],
    [InlineKeyboardButton("🔥 فري فاير", callback_data="game#فري فاير")],
    [InlineKeyboardButton("🎮 روبلوكس", callback_data="game#روبلوكس")],
    [InlineKeyboardButton("🔙 رجوع للمتجر", callback_data="store#back")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

cards_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎟️ بطاقات ستيم", callback_data="card#ستيم")],
    [InlineKeyboardButton("🎟️ بطاقات إكس بوكس", callback_data="card#إكس بوكس")],
    [InlineKeyboardButton("🔙 رجوع للمتجر", callback_data="store#back")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

phone_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("📱 سيريتل", callback_data="phone#syr")],
    [InlineKeyboardButton("📱 إم تي إن", callback_data="phone#mtn")],
    [InlineKeyboardButton("🔙 رجوع للمتجر", callback_data="store#back")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

# ==================== قوائم المحفظة والاسترجاع ====================
wallet_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("💵 شحن بالدولار", callback_data="charge#usd")],
    [InlineKeyboardButton("🇸🇾 شحن بالليرة", callback_data="charge#syr")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

refund_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("💵 استرجاع بالدولار", callback_data="refund#usd")],
    [InlineKeyboardButton("🇸🇾 استرجاع بالليرة", callback_data="refund#syr")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

# ==================== لوحة التحكم الإدارية (ضخمة) ====================
admin_panel = InlineKeyboardMarkup([
    [InlineKeyboardButton("📊 الإحصائيات", callback_data="adm#stats")],
    [InlineKeyboardButton("📢 إرسال إعلان", callback_data="adm#broadcast")],
    [InlineKeyboardButton("💰 إدارة المحفظة", callback_data="adm#wallet")],
    [InlineKeyboardButton("👥 المستخدمين", callback_data="adm#users")],
    [InlineKeyboardButton("🛒 إدارة المتجر", callback_data="adm#store")],
    [InlineKeyboardButton("📱 إدارة الهاتف", callback_data="adm#phone")],
    [InlineKeyboardButton("🤖 طلبات البوتات", callback_data="adm#bot_orders")],
    [InlineKeyboardButton("⚙️ الإعدادات", callback_data="adm#settings")],
    [InlineKeyboardButton("🗑️ تنظيف البيانات", callback_data="adm#clean")],
    [InlineKeyboardButton("💾 نسخة احتياطية", callback_data="adm#backup")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "name": update.effective_user.first_name,
            "balance_usd": 0,
            "joined": datetime.now().isoformat()
        }
        save_db(db)
    balance = db["users"][user_id]["balance_usd"]
    rate = db.get("exchange_rate", 14500)
    await update.message.reply_text(
        f"👑 **بوت شام إن جيم** 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 مرحباً: {update.effective_user.first_name}\n"
        f"💰 رصيدك: ${balance:.2f}\n"
        f"🇸🇾 بالليرة: {balance * rate:,.0f} ل.س\n"
        f"📈 سعر الصرف: 1$ = {rate:,} ل.س\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ استخدم الأزرار للتنقل ❤️",
        reply_markup=main_menu,
        parse_mode='Markdown'
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_password'] = True
    await update.message.reply_text("🔐 اكتب كلمة السر للتحقق:")

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if context.user_data.get('admin_dashboard') or user_id == ADMIN_ID:
        await update.message.reply_text("🛸 **لوحة التحكم الإدارية**", reply_markup=admin_panel, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ ليس لديك صلاحية للدخول.")

# ==================== معالج الرسائل النصية ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    db = load_db()

    # ===== كلمة السر =====
    if context.user_data.get('awaiting_password'):
        if text == ADMIN_PASSWORD:
            context.user_data['admin_dashboard'] = True
            context.user_data['awaiting_password'] = False
            await update.message.reply_text("✅ تم التحقق! استخدم /panel للوحة التحكم.")
        else:
            context.user_data['awaiting_password'] = False
            await update.message.reply_text("❌ كلمة سر خاطئة!")
        return

    # ===== إرسال إعلان =====
    if context.user_data.get('awaiting_broadcast'):
        context.user_data['awaiting_broadcast'] = False
        await update.message.reply_text("🚀 جاري الإرسال...")
        count = 0
        for uid in db["users"]:
            try:
                await context.bot.send_message(uid, f"📢 **إعلان عام**\n━━━━━━━━━━━━━━━━━━━━\n{text}", parse_mode='Markdown')
                count += 1
            except:
                pass
        await update.message.reply_text(f"✅ تم إرسال الإعلان إلى {count} مستخدم.")
        return

    # ===== إضافة رصيد (أدمن) =====
    if context.user_data.get('awaiting_add_balance'):
        try:
            parts = text.split('|')
            if len(parts) != 2:
                raise ValueError
            target_id = parts[0].strip()
            amount = float(parts[1].strip())
            if amount <= 0:
                raise ValueError
            if target_id not in db["users"]:
                await update.message.reply_text("❌ المستخدم غير موجود!")
                return
            db["users"][target_id]["balance_usd"] = db["users"][target_id].get("balance_usd", 0) + amount
            save_db(db)
            context.user_data['awaiting_add_balance'] = False
            await update.message.reply_text(f"✅ تم إضافة ${amount} إلى {db['users'][target_id]['name']}")
            await context.bot.send_message(target_id, f"🎉 تم إضافة ${amount} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم: `آيدي|المبلغ`")
        return

    # ===== كتابة الآيدي =====
    if context.user_data.get('awaiting_game_id'):
        context.user_data['game_id'] = text
        context.user_data['action'] = 'confirmed'
        item = context.user_data.get('item')
        price = context.user_data.get('price')
        confirm_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("✔️ تأكيد الشراء", callback_data="confirm_order")]
        ])
        await update.message.reply_text(
            f"🎯 **تأكيد الطلب**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 المنتج: {item}\n"
            f"💰 السعر: ${price:.2f}\n"
            f"🆔 الآيدي: {text}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ اضغط زر التأكيد لإتمام العملية.",
            reply_markup=confirm_btn,
            parse_mode='Markdown'
        )
        return

    # ===== شحن الرصيد =====
    if context.user_data.get('awaiting_charge'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            currency = context.user_data.get('charge_currency', 'usd')
            if currency == 'syr':
                rate = db.get('exchange_rate', 14500)
                amount = amount / rate
            update_balance(user_id, amount)
            context.user_data['awaiting_charge'] = False
            await update.message.reply_text(f"✅ تم شحن ${amount:.2f} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!")
        return

    # ===== استرجاع الأموال =====
    if context.user_data.get('awaiting_refund'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            currency = context.user_data.get('refund_currency', 'usd')
            if currency == 'syr':
                rate = db.get('exchange_rate', 14500)
                amount = amount / rate
            balance = get_balance(user_id)
            if balance < amount:
                await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!")
                return
            update_balance(user_id, -amount)
            context.user_data['awaiting_refund'] = False
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                f"💰 **طلب استرجاع أموال**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 {update.effective_user.first_name}\n"
                f"🆔 {user_id}\n"
                f"💵 المبلغ: ${amount:.2f}"
            )
            await update.message.reply_text(f"✅ تم استرجاع ${amount:.2f} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!")
        return

    # ===== شحن رصيد الهاتف =====
    if context.user_data.get('awaiting_phone'):
        context.user_data['phone_number'] = text
        context.user_data['awaiting_phone'] = False
        context.user_data['awaiting_phone_amount'] = True
        await update.message.reply_text("✍️ اكتب المبلغ المراد شحنه بالليرة:")
        return

    if context.user_data.get('awaiting_phone_amount'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            rate = db.get('exchange_rate', 14500)
            usd_amount = amount / rate
            balance = get_balance(user_id)
            if balance < usd_amount:
                await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!")
                return
            update_balance(user_id, -usd_amount)
            phone = context.user_data.get('phone_number')
            card_type = context.user_data.get('card_type', 'MTN')
            context.user_data['awaiting_phone_amount'] = False
            await update.message.reply_text(f"✅ تم شحن {amount:,.0f} ل.س إلى {phone} ({card_type})")
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                f"📱 **طلب شحن هاتف**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 {update.effective_user.first_name}\n"
                f"📞 {phone}\n"
                f"📶 {card_type}\n"
                f"💰 {amount:,.0f} ل.س"
            )
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!")
        return

    # ===== إنشاء بوت =====
    if context.user_data.get('awaiting_bot_desc'):
        context.user_data['bot_desc'] = text
        context.user_data['awaiting_bot_desc'] = False
        context.user_data['awaiting_bot_contact'] = True
        await update.message.reply_text("✍️ أرسل رقم تواصلك أو Username:")
        return

    if context.user_data.get('awaiting_bot_contact'):
        context.user_data['bot_contact'] = text
        context.user_data['awaiting_bot_contact'] = False
        server_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 سيرفر قوي 24 ساعة", callback_data="srv#strong")],
            [InlineKeyboardButton("💤 سيرفر عادي 12-18 ساعة", callback_data="srv#normal")]
        ])
        await update.message.reply_text("🖥️ **اختر نوع السيرفر:**", reply_markup=server_btn)
        return

    # ===== طلب بوت (من الأدمن) =====
    if context.user_data.get('awaiting_bot_price'):
        target_id = context.user_data.get('bot_target_id')
        if target_id:
            await context.bot.send_message(target_id, f"💰 **السعر المتفق عليه:** {text}")
            await update.message.reply_text(f"✅ تم إرسال السعر إلى المستخدم {target_id}")
        context.user_data['awaiting_bot_price'] = False
        return

    if context.user_data.get('awaiting_bot_desc_admin'):
        target_id = context.user_data.get('bot_target_id')
        if target_id:
            await context.bot.send_message(target_id, f"📝 **وصف إضافي:** {text}")
            await update.message.reply_text(f"✅ تم إرسال الوصف إلى المستخدم {target_id}")
        context.user_data['awaiting_bot_desc_admin'] = False
        return

    if context.user_data.get('awaiting_bot_time'):
        target_id = context.user_data.get('bot_target_id')
        if target_id:
            await context.bot.send_message(target_id, f"⏰ **الوقت المتوقع:** {text}")
            await update.message.reply_text(f"✅ تم إرسال الوقت إلى المستخدم {target_id}")
        context.user_data['awaiting_bot_time'] = False
        return

    # ===== أي رسالة أخرى =====
    await update.message.reply_text("⚠️ لم أفهم طلبك، استخدم الأزرار من القائمة.")

# ==================== معالج الأزرار ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(update.effective_user.id)
    db = load_db()

    # ============================================================
    # ==================== أزرار الإدارة ========================
    # ============================================================
    if data.startswith("adm#"):
        action = data.split('#')[1]

        if action == "stats":
            total_users = len(db["users"])
            total_balance = sum(u.get("balance_usd", 0) for u in db["users"].values())
            total_orders = len(db.get("orders", []))
            total_bot_orders = len(db.get("bot_orders", []))
            await query.edit_message_text(
                f"📊 **الإحصائيات**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👥 المستخدمين: {total_users}\n"
                f"💰 إجمالي الرصيد: ${total_balance:.2f}\n"
                f"📦 الطلبات: {total_orders}\n"
                f"🤖 طلبات البوتات: {total_bot_orders}\n"
                f"📈 متوسط الرصيد: ${(total_balance / (total_users or 1)):.2f}",
                parse_mode='Markdown'
            )

        elif action == "broadcast":
            context.user_data['awaiting_broadcast'] = True
            await query.edit_message_text("✍️ اكتب الرسالة التي تريد إرسالها لجميع المستخدمين:")

        elif action == "wallet":
            await query.edit_message_text(
                "💰 **إدارة المحفظة**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "اختر الإجراء:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ إضافة رصيد", callback_data="adm#add_balance")],
                    [InlineKeyboardButton("📊 عرض الأرصدة", callback_data="adm#view_balances")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="adm#back")]
                ]),
                parse_mode='Markdown'
            )

        elif action == "add_balance":
            context.user_data['awaiting_add_balance'] = True
            await query.edit_message_text("✍️ اكتب: `آيدي_المستخدم|المبلغ`\nمثال: `8243108672|10`")

        elif action == "view_balances":
            users_list = "💰 **الأرصدة**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid, info in list(db["users"].items())[:20]:
                users_list += f"👤 {info.get('name', 'مجهول')} (${info.get('balance_usd', 0):.2f})\n"
            await query.edit_message_text(users_list, parse_mode='Markdown')

        elif action == "users":
            users_list = "👥 **المستخدمين**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid, info in list(db["users"].items())[:20]:
                users_list += f"{uid}. {info.get('name', 'مجهول')} - ${info.get('balance_usd', 0):.2f}\n"
            await query.edit_message_text(users_list, parse_mode='Markdown')

        elif action == "store":
            games = db["custom_store"]["games"]
            cards = db["custom_store"]["cards"]
            store_info = "🛒 **إدارة المتجر**\n━━━━━━━━━━━━━━━━━━━━\n"
            store_info += "🎮 **الألعاب:**\n"
            for name in games:
                store_info += f"  📂 {name} ({len(games[name])} منتج)\n"
            store_info += "\n🎟️ **البطاقات:**\n"
            for name in cards:
                store_info += f"  📂 {name} ({len(cards[name])} منتج)\n"
            await query.edit_message_text(store_info, parse_mode='Markdown')

        elif action == "phone":
            await query.edit_message_text(
                "📱 **إدارة شحن الهاتف**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "اختر الإجراء:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 عرض طلبات الشحن", callback_data="adm#view_phone_orders")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="adm#back")]
                ]),
                parse_mode='Markdown'
            )

        elif action == "bot_orders":
            bot_orders = db.get("bot_orders", [])
            if not bot_orders:
                await query.edit_message_text("🤖 لا توجد طلبات بوتات حالياً.")
            else:
                orders_list = "🤖 **طلبات البوتات**\n━━━━━━━━━━━━━━━━━━━━\n"
                for i, order in enumerate(bot_orders[:10], 1):
                    orders_list += f"{i}. {order.get('user_name', 'مجهول')} - {order.get('server', 'غير محدد')}\n"
                await query.edit_message_text(orders_list, parse_mode='Markdown')

        elif action == "settings":
            rate = db.get('exchange_rate', 14500)
            maintenance = "🛑 معطل" if db.get('bot_maintenance', False) else "✅ شغال"
            await query.edit_message_text(
                f"⚙️ **الإعدادات العامة**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📈 سعر الصرف: 1$ = {rate:,} ل.س\n"
                f"⚙️ حالة البوت: {maintenance}\n"
                f"📝 ملاحظات الأدمن: {db.get('admin_notes', 'لا توجد ملاحظات')}",
                parse_mode='Markdown'
            )

        elif action == "clean":
            db["orders"] = []
            db["bot_orders"] = []
            save_db(db)
            await query.edit_message_text("🧹 تم تنظيف جميع الطلبات والبيانات المؤقتة.")

        elif action == "backup":
            backup_data = json.dumps(db, indent=2, ensure_ascii=False)
            await query.edit_message_text("💾 تم إنشاء نسخة احتياطية من قاعدة البيانات.")
            await context.bot.send_document(
                chat_id=user_id,
                document=('database_backup.json', backup_data.encode('utf-8')),
                caption="📂 نسخة احتياطية من قاعدة البيانات"
            )

        elif action == "back":
            await query.edit_message_text("🛸 **لوحة التحكم الإدارية**", reply_markup=admin_panel, parse_mode='Markdown')

        return

    # ============================================================
    # ==================== أزرار المتجر ========================
    # ============================================================
    if data == "store#games":
        await query.edit_message_text("🎮 **اختر اللعبة:**", reply_markup=games_menu, parse_mode='Markdown')

    elif data == "store#cards":
        await query.edit_message_text("🎟️ **اختر البطاقة:**", reply_markup=cards_menu, parse_mode='Markdown')

    elif data == "store#phone":
        await query.edit_message_text("📱 **اختر شبكة الهاتف:**", reply_markup=phone_menu, parse_mode='Markdown')

    elif data == "store#back":
        await query.edit_message_text("🛍️ **اختر القسم:**", reply_markup=store_menu, parse_mode='Markdown')

    # ============================================================
    # ==================== أزرار الألعاب ========================
    # ============================================================
    elif data.startswith("game#"):
        game_name = data.split('#')[1]
        items = db["custom_store"]["games"].get(game_name, [])
        if not items:
            await query.edit_message_text("⚠️ لا توجد عروض!")
            return
        buttons = []
        for item in items:
            price = float(item.split('-')[1].replace('$', ''))
            buttons.append([InlineKeyboardButton(item, callback_data=f"buy#game#{game_name}#{item}#{price}")])
        buttons.append([InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="store#games")])
        buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text(f"🛒 **عروض {game_name}**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')

    # ============================================================
    # ==================== أزرار البطاقات =======================
    # ============================================================
    elif data.startswith("card#"):
        card_name = data.split('#')[1]
        full_name = f"🎟️ بطاقات {card_name}"
        items = db["custom_store"]["cards"].get(full_name, [])
        if not items:
            await query.edit_message_text("⚠️ لا توجد عروض!")
            return
        buttons = []
        for item in items:
            price = float(item.split('-')[1].replace('$', ''))
            buttons.append([InlineKeyboardButton(item, callback_data=f"buy#card#{card_name}#{item}#{price}")])
        buttons.append([InlineKeyboardButton("🔙 رجوع للبطاقات", callback_data="store#cards")])
        buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text(f"🛒 **عروض بطاقات {card_name}**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')

    # ============================================================
    # ==================== عملية الشراء ========================
    # ============================================================
    elif data.startswith("buy#"):
        parts = data.split('#')
        item_type = parts[1]
        name = parts[2]
        item = parts[3]
        price = float(parts[4])
        balance = get_balance(user_id)
        if balance < price:
            await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي!")
            return
        context.user_data['item_type'] = item_type
        context.user_data['name'] = name
        context.user_data['item'] = item
        context.user_data['price'] = price
        context.user_data['awaiting_game_id'] = True
        await query.edit_message_text("✍️ **أدخل الآيدي (ID) الخاص بك:**", parse_mode='Markdown')

    # ============================================================
    # ==================== تأكيد الشراء ========================
    # ============================================================
    elif data == "confirm_order":
        if not context.user_data.get('awaiting_game_id') and context.user_data.get('action') != 'confirmed':
            await query.edit_message_text("❌ لا يوجد طلب مؤكد!")
            return
        item = context.user_data.get('item')
        price = context.user_data.get('price')
        game_id = context.user_data.get('game_id')
        balance = get_balance(user_id)
        if balance < price:
            await query.edit_message_text(f"❌ رصيدك غير كافٍ!")
            return
        update_balance(user_id, -price)
        context.user_data['awaiting_game_id'] = False
        context.user_data['action'] = None
        await query.edit_message_text(
            f"✅ **تم الشراء بنجاح!**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 المنتج: {item}\n"
            f"💰 المبلغ: ${price:.2f}\n"
            f"🆔 الآيدي: {game_id}",
            parse_mode='Markdown'
        )
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🛒 **طلب شراء جديد**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 {update.effective_user.first_name}\n"
            f"🆔 {user_id}\n"
            f"🎁 {item}\n"
            f"💰 ${price:.2f}\n"
            f"🆔 الآيدي: {game_id}"
        )

    # ============================================================
    # ==================== شحن رصيد الهاتف ====================
    # ============================================================
    elif data.startswith("phone#"):
        card_type = data.split('#')[1]
        context.user_data['card_type'] = card_type.upper()
        context.user_data['awaiting_phone'] = True
        await query.edit_message_text(f"✍️ **أدخل رقم الهاتف**\nالرجاء كتابة رقم الهاتف المراد شحنه ({card_type.upper()}):", parse_mode='Markdown')

    # ============================================================
    # ==================== شحن الرصيد ========================
    # ============================================================
    elif data.startswith("charge#"):
        currency = data.split('#')[1]
        context.user_data['charge_currency'] = currency
        context.user_data['awaiting_charge'] = True
        await query.edit_message_text(f"✍️ **أدخل المبلغ**\nالرجاء كتابة المبلغ {currency if currency == 'usd' else 'بالليرة السورية'}:", parse_mode='Markdown')

    # ============================================================
    # ==================== استرجاع الأموال ====================
    # ============================================================
    elif data.startswith("refund#"):
        currency = data.split('#')[1]
        context.user_data['refund_currency'] = currency
        context.user_data['awaiting_refund'] = True
        await query.edit_message_text(f"✍️ **أدخل المبلغ**\nالرجاء كتابة المبلغ {currency if currency == 'usd' else 'بالليرة السورية'} المراد استرجاعه:", parse_mode='Markdown')

    # ============================================================
    # ==================== إنشاء بوت ==========================
    # ============================================================
    elif data == "bot_order#start":
        context.user_data['awaiting_bot_desc'] = True
        await query.edit_message_text(
            "🤖 **إنشاء بوت جديد**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✍️ اكتب مواصفات البوت الذي تريده بالتفصيل:",
            parse_mode='Markdown'
        )

    # ============================================================
    # ==================== اختيار سيرفر البوت =================
    # ============================================================
    elif data.startswith("srv#"):
        srv_type = data.split('#')[1]
        srv_name = "🔥 قوي ومحمي 24 ساعة" if srv_type == 'strong' else "💤 عادي 12-18 ساعة"
        desc = context.user_data.get('bot_desc', 'غير محدد')
        contact = context.user_data.get('bot_contact', 'غير محدد')
        await query.edit_message_text("🚀 جاري إرسال الطلب للإدارة...")
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🤖 **طلب إنشاء بوت جديد**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 الزبون: {update.effective_user.first_name}\n"
            f"🆔 المعرف: {user_id}\n"
            f"💬 التواصل: {contact}\n"
            f"📝 المواصفات: {desc}\n"
            f"🖥️ السيرفر: {srv_name}"
        )
        context.user_data['awaiting_bot_desc'] = False
        context.user_data['awaiting_bot_contact'] = False

    # ============================================================
    # ==================== أزرار طلب البوت (إدارة) ============
    # ============================================================
    elif data.startswith("bot#"):
        parts = data.split('#')
        action = parts[1]
        target_id = parts[2]
        context.user_data['bot_target_id'] = target_id

        if action == "price":
            context.user_data['awaiting_bot_price'] = True
            await query.edit_message_text(f"✍️ **أدخل السعر**\nالرجاء كتابة السعر للمستخدم {target_id}:")
        elif action == "desc":
            context.user_data['awaiting_bot_desc_admin'] = True
            await query.edit_message_text(f"✍️ **وصف إضافي**\nالرجاء كتابة وصف إضافي للمستخدم {target_id}:")
        elif action == "time":
            context.user_data['awaiting_bot_time'] = True
            await query.edit_message_text(f"✍️ **الوقت المتوقع**\nالرجاء كتابة الوقت المتوقع للمستخدم {target_id}:")
        elif action == "file":
            await query.edit_message_text(f"📤 **إرسال الملف**\nالرجاء إرسال ملف البوت للمستخدم {target_id}:")

    # ============================================================
    # ==================== العودة للقائمة الرئيسية ============
    # ============================================================
    elif data == "main_menu":
        await query.edit_message_text("🎯 **القائمة الرئيسية**\nاختر الخيار المناسب:", reply_markup=main_menu, parse_mode='Markdown')

    else:
        await query.edit_message_text("⚠️ هذا الزر غير مفعل حالياً.")

# ==================== تشغيل البوت ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("panel", panel_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_text))

    print("🚀 البوت شغال بالبايثون!")
    app.run_polling()

if __name__ == "__main__":
    main()
