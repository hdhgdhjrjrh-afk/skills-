import telebot
from telebot import types
import os, json

# --- الإعدادات ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"
MAX_USERS = 15

bot = telebot.TeleBot(TOKEN)

# --- نظام البيانات ---
def init_files():
    files = {"users.txt": "", "bot_files.txt": "", "admins.json": "[]", "settings.json": '{"notifications": true}', "activity.json": "{}"}
    for file, content in files.items():
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f: f.write(content)

init_files()

def load_json(file):
    with open(file, "r", encoding="utf-8") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(file):
    with open(file, "r", encoding="utf-8") as f: return [line.strip() for line in f if line.strip()]

def save_list(file, data):
    with open(file, "w", encoding="utf-8") as f: f.write("\n".join(map(str, data)))

# --- التحقق ---
def is_admin(uid):
    admins = load_json("admins.json")
    return int(uid) == OWNER_ID or str(uid) in map(str, admins)

def is_subscribed(uid):
    try:
        status = bot.get_chat_member(CHANNEL_ID, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- لوحات التحكم ---
def admin_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    set_db = load_json("settings.json")
    notif_text = "إيقاف الإشعارات ❌" if set_db.get("notifications") else "تفعيل الإشعارات ✅"
    kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    kb.row("إرسال إذاعة 📣", "الإحصائيات 📊") # الزر الجديد الموحد
    kb.row(notif_text, "تنظيف البيانات 🧹")
    kb.row("تصفير الملفات 🗑️", "إضافة أدمن ➕")
    kb.row("إنهاء ✅")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
    return kb

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub"))
        return bot.send_message(uid, "⚠️ اشترك أولاً لتشغيل البوت!", reply_markup=mk)

    if is_admin(uid):
        return bot.send_message(uid, "👑 لوحة التحكم:", reply_markup=admin_kb())

    users = get_list("users.txt")
    if str(uid) not in users:
        if len(users) >= MAX_USERS: return bot.send_message(uid, "❌ اكتمل الحد الأقصى.")
        users.append(str(uid)); save_list("users.txt", users)
    bot.send_message(uid, "👋 أهلاً بك!")

# --- منطق الأزرار ---
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def handle_admin(message):
    uid, text = message.from_user.id, message.text

    if text == "إرسال إذاعة 📣":
        bot.send_message(uid, "🎯 اختر نوع الإذاعة:", reply_markup=broadcast_kb())

    elif text == "رجوع 🔙":
        bot.send_message(uid, "🔙 العودة للرئيسية:", reply_markup=admin_kb())

    elif text == "الإحصائيات 📊":
        u = len(get_list("users.txt"))
        act = load_json("activity.json")
        h = sum(len(v.get("h", [])) for v in act.values())
        r = sum(len(v.get("r", [])) for v in act.values())
        bot.send_message(uid, f"📊 **الإحصائيات:**\n👤 مشتركين: {u}/{MAX_USERS}\n❤️ تفاعلات: {h}\n📩 استلام: {r}")

    elif text == "إذاعة قناة 📢":
        m = bot.send_message(uid, "📢 أرسل الرسالة لنشرها في القناة:")
        bot.register_next_step_handler(m, lambda msg: bot.copy_message(CHANNEL_ID, msg.chat.id, msg.message_id))

    elif text == "إذاعة مستخدمين 👥":
        m = bot.send_message(uid, "👥 أرسل الرسالة لإذاعتها للمشتركين فقط:")
        bot.register_next_step_handler(m, lambda msg: broadcast_action(msg, "users"))

    elif text == "إذاعة الجميع 🌐":
        m = bot.send_message(uid, "🌐 أرسل رسالة لنشرها في القناة وللمستخدمين معاً:")
        bot.register_next_step_handler(m, lambda msg: broadcast_action(msg, "all"))

    # بقية الأزرار (تنظيف، إضافة أدمن، إلخ...)
    elif text == "تنظيف البيانات 🧹":
        save_json("activity.json", {}); bot.send_message(uid, "✅ تم التنظيف.")

def broadcast_action(message, mode):
    users = get_list("users.txt")
    sent = 0
    if mode == "all":
        try: bot.copy_message(CHANNEL_ID, message.chat.id, message.message_id)
        except: pass
    
    for u in users:
        try: bot.copy_message(u, message.chat.id, message.message_id); sent += 1
        except: pass
    bot.send_message(message.from_user.id, f"✅ تم الإرسال بنجاح إلى {sent} مستخدم.", reply_markup=admin_kb())

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else: bot.answer_callback_query(call.id, "❌ لم تشترك!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()
