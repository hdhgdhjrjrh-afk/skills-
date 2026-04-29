import telebot
from telebot import types
import os, json

# --- الإعدادات الثابتة ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
BOT_USERNAME = "gudurjbot"
MAX_USERS = 15

bot = telebot.TeleBot(TOKEN)

# --- نظام الملفات المصلح ---
def init_files():
    files = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "[]", 
        "activity.json": "{}",
        "settings.json": json.dumps({"notifications": True, "channel_id": "@Uchiha75", "sub_link": "https://t.me/Uchiha75"})
    }
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

# --- فحص الصلاحيات والاشتراك ---
def is_admin(uid):
    admins = load_json("admins.json")
    return int(uid) == OWNER_ID or str(uid) in map(str, admins)

def is_subscribed(uid):
    conf = load_json("settings.json")
    try:
        status = bot.get_chat_member(conf["channel_id"], uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- لوحات التحكم ---
def admin_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    set_db = load_json("settings.json")
    notif_text = "إيقاف الإشعارات ❌" if set_db.get("notifications") else "تفعيل الإشعارات ✅"
    kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    kb.row("إرسال إذاعة 📣", "الإحصائيات 📊")
    kb.row("إضافة اشتراك 🔗", notif_text)
    kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    kb.row("إضافة أدمن ➕", "إنهاء ✅")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
    return kb

# --- معالجة الرسائل ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    conf = load_json("settings.json")
    
    # 1. الاشتراك الإجباري
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك هنا أولاً 📢", url=conf["sub_link"]))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub"))
        return bot.send_message(uid, "⚠️ يجب أن تشترك في القناة أولاً!", reply_markup=mk)

    # 2. لوحة الأدمن (الأولوية للمالك)
    if is_admin(uid):
        return bot.send_message(uid, "👑 مرحباً بك في لوحة الإدارة:", reply_markup=admin_kb())

    # 3. تسجيل المستخدمين العاديين مع الحد (15)
    users = get_list("users.txt")
    if str(uid) not in users:
        if len(users) >= MAX_USERS:
            return bot.send_message(uid, "❌ نعتذر، وصل البوت للحد الأقصى من المشتركين.")
        users.append(str(uid))
        save_list("users.txt", users)
        
        # الإشعارات للمالك
        if conf.get("notifications"):
            bot.send_message(OWNER_ID, f"🔔 مستخدم جديد سجل الآن:\nالاسم: {message.from_user.first_name}\nالآيدي: {uid}")

    bot.send_message(uid, "👋 أهلاً بك! تم تفعيل اشتراكك في البوت.")

# --- منطق أزرار الأدمن ---
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def handle_admin(message):
    uid, text = message.from_user.id, message.text
    conf = load_json("settings.json")

    if text == "الإحصائيات 📊":
        u_list = get_list("users.txt")
        act = load_json("activity.json")
        h = sum(len(v.get("h", [])) for v in act.values())
        r = sum(len(v.get("r", [])) for v in act.values())
        bot.send_message(uid, f"📊 **الإحصائيات الحقيقية:**\n\n👥 المشتركين: {len(u_list)}/{MAX_USERS}\n❤️ التفاعلات: {h}\n📩 الاستلام: {r}")

    elif text == "تنظيف البيانات 🧹":
        save_json("activity.json", {})
        bot.send_message(uid, "✅ تم تنظيف سجل التفاعلات بالكامل.")

    elif text == "تصفير الملفات 🗑️":
        save_list("bot_files.txt", [])
        bot.send_message(uid, "✅ تم تصفير جميع الملفات المرفوعة.")

    elif "الإشعارات" in text:
        conf["notifications"] = not conf.get("notifications", True)
        save_json("settings.json", conf)
        bot.send_message(uid, "⚙️ تم تغيير حالة الإشعارات.", reply_markup=admin_kb())

    elif text == "إضافة أدمن ➕":
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد (أرقام فقط):")
        bot.register_next_step_handler(m, save_admin_final)

    elif text == "إرسال إذاعة 📣":
        bot.send_message(uid, "🎯 اختر نوع الإذاعة:", reply_markup=broadcast_kb())

    # (بقية الدوال مثل إذاعة قناة/مستخدمين تبقى كما هي في الكود السابق)

def save_admin_final(message):
    if message.text.isdigit():
        ad = load_json("admins.json")
        ad.append(message.text)
        save_json("admins.json", list(set(ad)))
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن بنجاح.")
    else:
        bot.send_message(message.from_user.id, "❌ خطأ في الآيدي.")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ مازلت غير مشترك!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()

