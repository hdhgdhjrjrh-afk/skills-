import telebot
from telebot import types
import os, json

# --- الإعدادات (تأكد من كتابة الآيدي الخاص بك بدقة) ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"
MAX_USERS = 15

bot = telebot.TeleBot(TOKEN)

# --- التأكد من وجود الملفات عند التشغيل لضمان عدم ظهور اللوحة فارغة ---
def init_files():
    files = {
        "users.txt": "",
        "bot_files.txt": "",
        "admins.json": "[]",
        "settings.json": '{"notifications": true}',
        "activity.json": "{}"
    }
    for file, content in files.items():
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)

init_files()

# --- دوال البيانات ---
def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(file):
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_list(file, data):
    with open(file, "w", encoding="utf-8") as f:
        f.write("\n".join(map(str, data)))

# --- فحص الصلاحيات ---
def is_admin(uid):
    # التحقق من المالك أو قائمة الأدمن
    admins = load_json("admins.json")
    return int(uid) == OWNER_ID or str(uid) in map(str, admins)

def is_subscribed(uid):
    try:
        status = bot.get_chat_member(CHANNEL_ID, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- لوحة التحكم الكاملة (الأزرار) ---
def admin_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # جلب حالة الإشعارات
    set_db = load_json("settings.json")
    notif_text = "إيقاف الإشعارات ❌" if set_db.get("notifications") else "تفعيل الإشعارات ✅"
    
    # إضافة الأزرار بنفس ترتيب الصورة
    kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    kb.row("إذاعة للمستخدمين 👥", "إذاعة قناة 📢")
    kb.row("الإحصائيات 📊", notif_text)
    kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    kb.row("إضافة أدمن ➕", "إنهاء ✅")
    return kb

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
    # 1. الاشتراك الإجباري
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub"))
        return bot.send_message(uid, "⚠️ عذراً، يجب أن تشترك في القناة أولاً لاستخدام البوت!", reply_markup=mk)

    # 2. التحقق من المالك/الأدمن لإظهار اللوحة
    if is_admin(uid):
        return bot.send_message(uid, "👑 أهلاً بك يا سيدي المطور في لوحة التحكم:", reply_markup=admin_kb())

    # 3. تسجيل المستخدم العادي (حد الـ 15)
    users = get_list("users.txt")
    if str(uid) not in users:
        if len(users) >= MAX_USERS:
            return bot.send_message(uid, f"❌ نعتذر، وصل البوت للحد الأقصى ({MAX_USERS} مستخدم).")
        users.append(str(uid))
        save_list("users.txt", users)
        
        # إشعار المالك
        set_db = load_json("settings.json")
        if set_db.get("notifications"):
            bot.send_message(OWNER_ID, f"🔔 مستخدم جديد دخل البوت!\nالاسم: {message.from_user.first_name}\nالآيدي: {uid}")

    bot.send_message(uid, "👋 أهلاً بك! يمكنك الآن استخدام البوت والاستلام من القناة.")

# --- منطق الأزرار (Admin Logic) ---
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_buttons(message):
    uid, text = message.from_user.id, message.text

    if text == "الإحصائيات 📊":
        u = len(get_list("users.txt"))
        act = load_json("activity.json")
        h = sum(len(v.get("h", [])) for v in act.values())
        r = sum(len(v.get("r", [])) for v in act.values())
        bot.send_message(uid, f"📊 **إحصائيات البوت:**\n\n👥 المشتركين: {u}/{MAX_USERS}\n❤️ التفاعلات: {h}\n📩 الاستلام: {r}")

    elif "الإشعارات" in text:
        db = load_json("settings.json")
        db["notifications"] = not db["notifications"]
        save_json("settings.json", db)
        bot.send_message(uid, "⚙️ تم تحديث الإعدادات!", reply_markup=admin_kb())

    elif text == "تنظيف البيانات 🧹":
        save_json("activity.json", {})
        bot.send_message(uid, "🧹 تم تنظيف سجل التفاعلات بنجاح.")

    elif text == "تصفير الملفات 🗑️":
        save_list("bot_files.txt", [])
        bot.send_message(uid, "🗑️ تم مسح جميع الملفات المرفوعة.")

    elif text == "إذاعة قناة 📢":
        m = bot.send_message(uid, "📢 أرسل ما تريد نشره في القناة الآن:")
        bot.register_next_step_handler(m, lambda msg: bot.copy_message(CHANNEL_ID, msg.chat.id, msg.message_id))

    elif text == "إضافة أدمن ➕":
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, save_admin_process)

def save_admin_process(message):
    if message.text.isdigit():
        ad = load_json("admins.json")
        ad.append(message.text)
        save_json("admins.json", list(set(ad)))
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن بنجاح.")
    else:
        bot.send_message(message.from_user.id, "❌ خطأ! الآيدي يجب أن يكون أرقاماً.")

# --- التعامل مع أزرار القناة وزر التحقق ---
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    uid = call.from_user.id
    if call.data == "check_sub":
        if is_subscribed(uid):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد!", show_alert=True)

if __name__ == "__main__":
    print("البوت يعمل الآن بدون أخطاء...")
    bot.infinity_polling()

