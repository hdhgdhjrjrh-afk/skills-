import telebot
from telebot import types
import os, json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
MAX_USERS = 15

bot = telebot.TeleBot(TOKEN)

# --- نظام الملفات (ضمان الإنشاء) ---
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

# --- دالة فحص الاشتراك الإجباري ---
def is_subscribed(uid):
    conf = json.load(open("settings.json"))
    try:
        status = bot.get_chat_member(conf["channel_id"], uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- لوحة التحكم الرئيسية ---
def main_admin_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = json.load(open("settings.json"))
    n_status = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    kb.row("إرسال إذاعة 📣", "الإحصائيات 📊")
    kb.row("إضافة اشتراك 🔗", n_status)
    kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    kb.row("إضافة أدمن ➕", "إنهاء ✅")
    return kb

# --- معالجة أمر البداية /start ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    conf = json.load(open("settings.json"))
    
    # 1. التحقق من الاشتراك الإجباري أولاً
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اضغط هنا للاشتراك 📢", url=conf["sub_link"]))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="verify_sub"))
        return bot.send_message(uid, f"⚠️ عذراً، يجب الاشتراك في القناة {conf['channel_id']} أولاً!", reply_markup=mk)

    # 2. إذا كان أدمن تظهر له اللوحة فوراً
    admins = json.load(open("admins.json"))
    if uid == OWNER_ID or str(uid) in map(str, admins):
        return bot.send_message(uid, "👑 أهلاً بك في لوحة الإدارة:", reply_markup=main_admin_kb())

    # 3. تسجيل المستخدم العادي مع فحص الحد (15)
    with open("users.txt", "r") as f: users = f.read().splitlines()
    
    if str(uid) not in users:
        if len(users) >= MAX_USERS:
            return bot.send_message(uid, "❌ نعتذر، البوت وصل للحد الأقصى من المستخدمين (15/15).")
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        
        # إرسال إشعار للمالك
        if conf.get("notifications"):
            bot.send_message(OWNER_ID, f"🔔 عضو جديد سجل:\nالاسم: {message.from_user.first_name}\nالآيدي: {uid}")

    bot.send_message(uid, "✅ تم تفعيل البوت بنجاح!")

# --- معالجة الأزرار (Admin Logic) ---
@bot.message_handler(func=lambda m: True)
def admin_buttons(message):
    uid, text = message.from_user.id, message.text
    admins = json.load(open("admins.json"))
    if not (uid == OWNER_ID or str(uid) in map(str, admins)): return

    if text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        act = json.load(open("activity.json"))
        h = sum(len(v.get("h", [])) for v in act.values())
        r = sum(len(v.get("r", [])) for v in act.values())
        bot.send_message(uid, f"📊 **إحصائيات البوت:**\n\n👥 مستخدمين: {u_count} / {MAX_USERS}\n❤️ تفاعلات: {h}\n📩 استلام: {r}")

    elif text == "تنظيف البيانات 🧹":
        with open("activity.json", "w") as f: f.write("{}")
        bot.send_message(uid, "🧹 تم تصفير عدادات القناة (تفاعل/استلام).")

    elif text == "تصفير الملفات 🗑️":
        with open("bot_files.txt", "w") as f: f.write("")
        bot.send_message(uid, "🗑️ تم حذف جميع ملفات البوت.")

    elif text == "إضافة أدمن ➕":
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, save_admin)

    elif text == "إضافة اشتراك 🔗":
        m = bot.send_message(uid, "🔗 أرسل رابط القناة الجديد (مثل: https://t.me/...)")
        bot.register_next_step_handler(m, save_sub)

# --- توابع الحفظ ---
def save_admin(message):
    if message.text.isdigit():
        ad = json.load(open("admins.json"))
        ad.append(message.text)
        with open("admins.json", "w") as f: json.dump(list(set(ad)), f)
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن.")
    else: bot.send_message(message.from_user.id, "❌ آيدي خاطئ.")

def save_sub(message):
    if "t.me/" in message.text:
        conf = json.load(open("settings.json"))
        conf["sub_link"] = message.text
        conf["channel_id"] = "@" + message.text.split("t.me/")[1].split("/")[0]
        with open("settings.json", "w") as f: json.dump(conf, f)
        bot.send_message(message.from_user.id, "✅ تم تحديث رابط الاشتراك.")
    else: bot.send_message(message.from_user.id, "❌ رابط غير صالح.")

# --- زر التحقق من الاشتراك ---
@bot.callback_query_handler(func=lambda call: call.data == "verify_sub")
def verify(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_cmd(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد في القناة!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()

