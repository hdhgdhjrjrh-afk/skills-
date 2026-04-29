import telebot
from telebot import types
import os, json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام قاعدة البيانات المصغر ---
def init_db():
    files = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "[]", 
        "activity.json": "{}",
        "settings.json": json.dumps({"notifications": True, "channel_id": "@Uchiha75", "sub_link": "https://t.me/Uchiha75"})
    }
    for f, c in files.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file: file.write(c)

init_db()

def get_conf():
    with open("settings.json", "r", encoding="utf-8") as f: return json.load(f)

def save_conf(conf):
    with open("settings.json", "w", encoding="utf-8") as f: json.dump(conf, f, indent=4)

def is_admin(uid):
    admins = json.load(open("admins.json"))
    return int(uid) == OWNER_ID or str(uid) in map(str, admins)

def is_subscribed(uid):
    conf = get_conf()
    try:
        status = bot.get_chat_member(conf["channel_id"], uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- الكيبوردات (الواجهة) ---
def main_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_conf()
    n_status = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    kb.row("إرسال إذاعة 📣", "الإحصائيات 📊")
    kb.row("إضافة اشتراك 🔗", n_status)
    kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    kb.row("إضافة أدمن ➕", "إنهاء ✅")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
    return kb

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    conf = get_conf()
    
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك هنا أولاً 📢", url=conf["sub_link"]))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="verify_sub"))
        return bot.send_message(uid, "⚠️ عذراً، يجب الاشتراك في القناة أولاً لاستخدام البوت!", reply_markup=mk)

    if is_admin(uid):
        return bot.send_message(uid, "👑 مرحباً بك في لوحة الإدارة:", reply_markup=main_kb())

    # تسجيل المستخدم (بدون حد)
    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        if conf.get("notifications"):
            bot.send_message(OWNER_ID, f"🔔 مستخدم جديد سجل:\nالاسم: {message.from_user.first_name}\nالآيدي: {uid}")

    bot.send_message(uid, "✅ تم تفعيل البوت بنجاح!")

# --- معالجة أزرار الأدمن ---
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def handle_admin(message):
    uid, text = message.from_user.id, message.text

    if text == "إرسال إذاعة 📣":
        bot.send_message(uid, "🎯 اختر نوع الإذاعة:", reply_markup=broadcast_kb())

    elif text == "إذاعة قناة 📢":
        m = bot.send_message(uid, "📢 أرسل الرسالة لنشرها في القناة:")
        bot.register_next_step_handler(m, lambda msg: start_broadcast(msg, "channel"))

    elif text == "إذاعة مستخدمين 👥":
        m = bot.send_message(uid, "👥 أرسل الرسالة لإرسالها للمستخدمين:")
        bot.register_next_step_handler(m, lambda msg: start_broadcast(msg, "users"))

    elif text == "إذاعة الجميع 🌐":
        m = bot.send_message(uid, "🌐 أرسل رسالة للجميع (قناة + خاص):")
        bot.register_next_step_handler(m, lambda msg: start_broadcast(msg, "all"))

    elif text == "رجوع 🔙":
        bot.send_message(uid, "🔙 العودة للرئيسية:", reply_markup=main_kb())

    elif "الإشعارات" in text:
        conf = get_conf()
        conf["notifications"] = not conf.get("notifications")
        save_conf(conf)
        status = "تفعيل" if conf["notifications"] else "إيقاف"
        bot.send_message(uid, f"⚙️ تم {status} الإشعارات بنجاح.", reply_markup=main_kb())

    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        act = json.load(open("activity.json"))
        h = sum(len(v.get("h", [])) for v in act.values())
        r = sum(len(v.get("r", [])) for v in act.values())
        bot.send_message(uid, f"📊 **الإحصائيات:**\n👥 مستخدمين: {u_count}\n❤️ تفاعلات: {h}\n📩 استلام: {r}")

    elif text == "تنظيف البيانات 🧹":
        with open("activity.json", "w") as f: f.write("{}")
        bot.send_message(uid, "🧹 تم تنظيف سجل التفاعلات.")

    elif text == "تصفير الملفات 🗑️":
        with open("bot_files.txt", "w") as f: f.write("")
        bot.send_message(uid, "🗑️ تم حذف جميع الملفات.")

    elif text == "إضافة أدمن ➕":
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, save_admin)

    elif text == "إضافة اشتراك 🔗":
        m = bot.send_message(uid, "🔗 أرسل رابط القناة الجديد:")
        bot.register_next_step_handler(m, save_sub)

# --- توابع التنفيذ (Logic) ---
def start_broadcast(message, mode):
    conf = get_conf()
    with open("users.txt", "r") as f: users = f.read().splitlines()
    sent = 0
    if mode in ["channel", "all"]:
        try: bot.copy_message(conf["channel_id"], message.chat.id, message.message_id); sent += 1
        except: pass
    if mode in ["users", "all"]:
        for u in users:
            try: bot.copy_message(u, message.chat.id, message.message_id); sent += 1
            except: pass
    bot.send_message(message.from_user.id, f"✅ تمت الإذاعة لـ {sent} وجهة.", reply_markup=main_kb())

def save_admin(message):
    if message.text.isdigit():
        ad = json.load(open("admins.json"))
        ad.append(message.text)
        with open("admins.json", "w") as f: json.dump(list(set(ad)), f)
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن.", reply_markup=main_kb())
    else: bot.send_message(message.from_user.id, "❌ خطأ في الآيدي.")

def save_sub(message):
    if "t.me/" in message.text:
        conf = get_conf()
        conf["sub_link"] = message.text
        conf["channel_id"] = "@" + message.text.split("t.me/")[1].split("/")[0]
        save_conf(conf)
        bot.send_message(message.from_user.id, "✅ تم تحديث الاشتراك.", reply_markup=main_kb())
    else: bot.send_message(message.from_user.id, "❌ رابط خاطئ.")

@bot.callback_query_handler(func=lambda call: call.data == "verify_sub")
def verify(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_cmd(call.message)
    else: bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()

