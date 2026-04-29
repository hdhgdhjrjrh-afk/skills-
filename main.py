import telebot
from telebot import types
import os
import json

# ================= الإعدادات =================
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" # يجب أن يكون البوت أدمن هنا
BOT_USERNAME = "gudurjbot"
MAX_USERS = 15
# ============================================

bot = telebot.TeleBot(TOKEN)

# --- وظائف البيانات ---
def get_data(file):
    if not os.path.exists(file): return {} if file.endswith(".json") else []
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

# --- فحص الإشتراك الإجباري ---
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- لوحة التحكم ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    s = get_data("settings.json")
    notif_status = "إيقاف الإشعارات ❌" if s.get("notifications", True) else "تفعيل الإشعارات ✅"
    
    markup.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    markup.row("إذاعة للمستخدمين 👥", "إذاعة قناة 📢")
    markup.row("الإحصائيات 📊", notif_status)
    markup.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    markup.row("إضافة أدمن ➕", "إنهاء ✅")
    return markup

# --- رسالة البداية والاشتراك ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
    # 1. فحص الإشتراك الإجباري (زر الإشتراك)
    if not is_subscribed(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("إشترك في القناة أولاً 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        markup.add(types.InlineKeyboardButton("تحقق من الإشتراك ✅", callback_data="check"))
        return bot.send_message(uid, "⚠️ عذراً، يجب عليك الإشتراك في القناة لإستخدام البوت.", reply_markup=markup)

    # 2. فحص حد الـ 15 مستخدم
    users = get_data("users.txt")
    if str(uid) not in map(str, users):
        if len(users) >= MAX_USERS:
            return bot.send_message(uid, f"❌ نعتذر، وصل البوت للحد الأقصى ({MAX_USERS} مستخدم).")
        users.append(str(uid))
        save_data("users.txt", users)
        
        # الإشعارات (إرسال للمالك عند دخول شخص جديد)
        s = get_data("settings.json")
        if s.get("notifications", True):
            bot.send_message(OWNER_ID, f"🔔 مستخدم جديد سجل في البوت:\nالاسم: {message.from_user.first_name}\nالآيدي: {uid}")

    # 3. توجيه الأدمن أو المستخدم
    admins = get_data("admins.json")
    if uid == OWNER_ID or str(uid) in map(str, admins):
        bot.send_message(uid, "👑 أهلاً بك في لوحة التحكم:", reply_markup=admin_keyboard())
    else:
        bot.send_message(uid, "👋 أهلاً بك! يمكنك الآن إستلام الملفات من القناة.")

# --- تنفيذ مهام الأزرار ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    uid, text = message.from_user.id, message.text
    admins = get_data("admins.json")
    if not (uid == OWNER_ID or str(uid) in map(str, admins)): return

    if text == "الإحصائيات 📊":
        users = len(get_data("users.txt"))
        act = get_data("activity.json")
        h = sum(len(v.get("h", [])) for v in act.values()) if isinstance(act, dict) else 0
        r = sum(len(v.get("r", [])) for v in act.values()) if isinstance(act, dict) else 0
        bot.send_message(uid, f"📊 **الإحصائيات:**\n\n👤 المشتركين: {users}/{MAX_USERS}\n❤️ التفاعلات: {h}\n📩 الإستلام: {r}")

    elif text == "تنظيف البيانات 🧹":
        save_data("activity.json", {})
        bot.send_message(uid, "✅ تم تنظيف سجل التفاعلات والإستلام بنجاح.")

    elif "الإشعارات" in text:
        s = get_data("settings.json")
        s["notifications"] = not s.get("notifications", True)
        save_data("settings.json", s)
        bot.send_message(uid, "⚙️ تم تحديث حالة الإشعارات.", reply_markup=admin_keyboard())

    elif text == "إذاعة قناة 📢":
        msg = bot.send_message(uid, "📢 أرسل الرسالة لنشرها في القناة مباشرة:")
        bot.register_next_step_handler(msg, lambda m: bot.copy_message(CHANNEL_ID, m.chat.id, m.message_id))

    elif text == "إضافة أدمن ➕":
        msg = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(msg, add_admin_logic)

    elif text == "تصفير الملفات 🗑️":
        save_data("bot_files.txt", [])
        bot.send_message(uid, "🗑️ تم تصفير قائمة الملفات.")

def add_admin_logic(message):
    if message.text.isdigit():
        ad = get_data("admins.json")
        if not isinstance(ad, list): ad = []
        ad.append(message.text)
        save_data("admins.json", list(set(ad)))
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن بنجاح.")

# --- معالجة زر التحقق ---
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()

