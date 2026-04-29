import telebot
from telebot import types
import os
import json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# --- نظام إدارة البيانات (مُعالج للأخطاء) ---
def get_data(file):
    if not os.path.exists(file):
        if file.endswith(".json"): return {}
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return {} if file.endswith(".json") else []
            return json.loads(content) if file.endswith(".json") else content.splitlines()
    except: return {} if file.endswith(".json") else []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        if file.endswith(".json"): json.dump(data, f, indent=4, ensure_ascii=False)
        else: f.write("\n".join(map(str, data)) + "\n")

# --- التحقق من الأدمن ---
def is_admin(uid):
    if int(uid) == OWNER_ID: return True
    admins = get_data("admins.json")
    return str(uid) in map(str, admins) if isinstance(admins, list) else False

# --- لوحة التحكم (مطابقة للصورة) ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = get_data("settings.json")
    if not settings: settings = {"notifications": True}
    notif = "إيقاف الإشعارات ❌" if settings.get("notifications") else "تفعيل الإشعارات ✅"
    
    markup.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    markup.row("إذاعة للمستخدمين 👥", "الإحصائيات 📊")
    markup.row(notif, "تنظيف البيانات 🧹")
    markup.row("تصفير الملفات 🗑️", "إنهاء ✅")
    markup.add("إضافة أدمن ➕")
    return markup

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    users = get_data("users.txt")
    
    if str(uid) not in map(str, users):
        if "activate" in (message.text or ""):
            users.append(str(uid))
            save_data("users.txt", users)
            bot.send_message(uid, "✅ تم تفعيل اشتراكك!")
        else:
            settings = get_data("settings.json")
            if settings.get("notifications", True):
                uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
                bot.send_message(OWNER_ID, f"👤 دخول مستخدم جديد!\nالاسم: {message.from_user.first_name}\nالآيدي: {uid}\nاليوزر: {uname}")

    if is_admin(uid):
        bot.send_message(uid, "👑 أهلاً بك في لوحة التحكم:", reply_markup=admin_keyboard())
    else:
        bot.send_message(uid, "👋 أهلاً بك! يمكنك الاستلام من القناة.")

# --- منطق الأزرار (الإصلاح الجذري) ---
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_buttons(message):
    uid, text = message.from_user.id, message.text

    if text == "نشر تلقائي 📣":
        count = len(get_data("bot_files.txt"))
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(types.InlineKeyboardButton("استلم 📩", callback_data="rcv"), 
                   types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit"))
        markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", url=f"https://t.me/{BOT_USERNAME}?start=activate"))
        bot.send_message(CHANNEL_ID, f"⚡ **تحديث جديد!**\n\n📄 عدد الملفات المتاحة: {count}\n🚀 سرعة عالية جداً", reply_markup=markup)
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    elif text == "الإحصائيات 📊":
        users = len(get_data("users.txt"))
        act = get_data("activity.json")
        hits = sum(len(v.get("h", [])) for v in act.values()) if isinstance(act, dict) else 0
        rcvs = sum(len(v.get("r", [])) for v in act.values()) if isinstance(act, dict) else 0
        bot.send_message(uid, f"📊 **الإحصائيات:**\n👥 مستخدمين: {users}\n❤️ تفاعلات: {hits}\n📩 استلام: {rcvs}")

    elif text == "تنظيف البيانات 🧹":
        save_data("activity.json", {})
        bot.send_message(uid, "🧹 تم تنظيف بيانات التفاعلات والاستلام.")

    elif text == "تصفير الملفات 🗑️":
        save_data("bot_files.txt", [])
        bot.send_message(uid, "🗑️ تم مسح جميع الملفات المرفوعة.")

    elif text == "إذاعة للمستخدمين 👥":
        msg = bot.send_message(uid, "📣 أرسل رسالة الإذاعة (نص أو صورة):")
        bot.register_next_step_handler(msg, perform_broadcast)

    elif text == "إضافة أدمن ➕":
        msg = bot.send_message(uid, "🆔 أرسل آيدي الشخص لرفعه أدمن:")
        bot.register_next_step_handler(msg, perform_add_admin)

    elif "الإشعارات" in text:
        s = get_data("settings.json")
        s["notifications"] = not s.get("notifications", True)
        save_data("settings.json", s)
        bot.send_message(uid, "⚙️ تم تحديث إعدادات الإشعارات.", reply_markup=admin_keyboard())

    elif text == "إنهاء ✅":
        bot.send_message(uid, "✅ تم إغلاق اللوحة.", reply_markup=types.ReplyKeyboardRemove())

# --- دوال العمليات (التي كانت لا تعمل) ---
def perform_broadcast(message):
    users = get_data("users.txt")
    count = 0
    for u in users:
        try:
            bot.copy_message(u, message.chat.id, message.message_id)
            count += 1
        except: pass
    bot.send_message(message.from_user.id, f"✅ تم الإرسال إلى {count} مستخدم.")

def perform_add_admin(message):
    if message.text.isdigit():
        admins = get_data("admins.json")
        if not isinstance(admins, list): admins = []
        admins.append(message.text)
        save_data("admins.json", list(set(admins)))
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن بنجاح.")
    else:
        bot.send_message(message.from_user.id, "❌ خطأ! أرسل آيدي أرقام فقط.")

if __name__ == "__main__":
    bot.infinity_polling()

