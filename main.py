import telebot
from telebot import types
import os
import json

# --- 1. الإعدادات ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# --- 2. نظام البيانات المصلح ---
def get_data(file):
    if not os.path.exists(file):
        if file.endswith(".json"): return [] if "admins" in file else {}
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            if file.endswith(".json"): return json.load(f)
            return [line.strip() for line in f if line.strip()]
    except: return [] if file.endswith(".json") else []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        if file.endswith(".json"): json.dump(data, f, indent=4)
        else:
            if isinstance(data, list): f.write("\n".join(map(str, data)) + "\n")
            else: f.write(str(data))

# تجهيز الملفات عند التشغيل
for f in ["users.txt", "bot_files.txt", "admins.json", "activity.json", "settings.json"]:
    if not os.path.exists(f):
        if f == "settings.json": save_data(f, {"notifications": True})
        elif f.endswith(".json"): save_data(f, [] if "admins" in f else {})
        else: save_data(f, "")

# --- 3. التحقق من الأدمن ---
def is_admin(user_id):
    if user_id == OWNER_ID: return True
    admins = get_data("admins.json")
    return str(user_id) in map(str, admins)

# --- 4. لوحات التحكم ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = get_data("settings.json")
    notif = "إيقاف الإشعارات ❌" if settings.get("notifications") else "تفعيل الإشعارات ✅"
    
    markup.add("نشر في القناة 📢", "إضافة ملفات 📤")
    markup.add("الإحصائيات 📊", notif)
    markup.add("إضافة أدمن ➕", "تصفير الملفات 🗑️")
    markup.add("إنهاء ✅")
    return markup

# --- 5. معالجة الرسائل ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    users = get_data("users.txt")
    
    # منطق الاشتراك والتفعيل
    if str(uid) not in map(str, users):
        if "activate" in (message.text or ""):
            users.append(str(uid))
            save_data("users.txt", users)
            bot.send_message(uid, "✅ تم تفعيل اشتراكك بنجاح!")
        else:
            # إشعار دخول مستخدم جديد
            settings = get_data("settings.json")
            if settings.get("notifications"):
                uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
                bot.send_message(OWNER_ID, f"👤 دخول مستخدم جديد:\nالاسم: {message.from_user.first_name}\nالآيدي: `{uid}`\nاليوزر: {uname}")

    if is_admin(uid):
        bot.send_message(uid, "👑 أهلاً بك في لوحة التحكم الكاملة:", reply_markup=admin_keyboard())
    else:
        bot.send_message(uid, "👋 أهلاً بك! يمكنك الاستلام من القناة مباشرة.")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_logic(message):
    uid, text = message.from_user.id, message.text

    if text == "نشر في القناة 📢":
        count = len(get_data("bot_files.txt"))
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("استلم 📩", callback_data="rcv"), 
                   types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit"))
        markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", url=f"https://t.me/{BOT_USERNAME}?start=activate"))
        
        caption = f"⚡ **تحديث جديد!**\n\n📄 عدد الملفات: {count}\n🚀 سرعة عالية | ⏳ محدد المدة"
        bot.send_message(CHANNEL_ID, caption, reply_markup=markup, parse_mode="Markdown")

    elif text == "إضافة أدمن ➕":
        msg = bot.send_message(uid, "🆔 أرسل آيدي الشخص المراد رفعه أدمن:")
        bot.register_next_step_handler(msg, save_admin)

    elif text == "الإحصائيات 📊":
        users_count = len(get_data("users.txt"))
        files_count = len(get_data("bot_files.txt"))
        bot.send_message(uid, f"📊 **إحصائيات البوت:**\n\n👥 عدد المشتركين: {users_count}\n📂 عدد الملفات: {files_count}")

    elif "الإشعارات" in text:
        settings = get_data("settings.json")
        settings["notifications"] = not settings["notifications"]
        save_data("settings.json", settings)
        bot.send_message(uid, "⚙️ تم تحديث الحالة!", reply_markup=admin_keyboard())

    elif text == "إضافة ملفات 📤":
        msg = bot.send_message(uid, "📤 أرسل الملفات الآن، ثم اضغط إنهاء ✅", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(msg, upload_files)

def save_admin(message):
    if message.text.isdigit():
        admins = get_data("admins.json")
        admins.append(message.text)
        save_data("admins.json", list(set(admins)))
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن بنجاح!", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.from_user.id, "❌ خطأ! أرسل آيدي أرقام فقط.")

def upload_files(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=admin_keyboard())
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        files = get_data("bot_files.txt")
        files.append(fid)
        save_data("bot_files.txt", files)
        bot.send_message(message.from_user.id, "📥 تم الاستلام!")
    bot.register_next_step_handler(message, upload_files)

# --- 6. الأزرار الشفافة ---
@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    uid = str(call.from_user.id)
    if uid not in get_data("users.txt"):
        return bot.answer_callback_query(call.id, "⚠️ يجب تفعيل البوت أولاً!", show_alert=True)
    
    if call.data == "hit":
        bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
    elif call.data == "rcv":
        files = get_data("bot_files.txt")
        for f in files: bot.send_document(call.from_user.id, f)
        bot.answer_callback_query(call.id, "📩 تم الإرسال للخاص.")

if __name__ == "__main__":
    bot.infinity_polling()

