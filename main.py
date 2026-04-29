import telebot
from telebot import types
import os
import json
import time

# --- 1. الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "ban_list.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump({} if "activity" in f else [], file)
            else: file.write("")

# --- 2. دالات المساعدة ---
def load_data(filename, default_type=dict):
    try:
        with open(filename, "r", encoding="utf-8") as f: 
            content = f.read()
            return json.loads(content) if content else default_type()
    except: return default_type()

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return True

# --- 3. لوحة التحكم (تمت إضافة الأزرار الجديدة) ---
def get_admin_panel():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        "نشر تلقائي 📣", "إضافة ملفات 📤", 
        "إذاعة للمستخدمين 👥", "إذاعة للقناة 📢", 
        "الإحصائيات 📊", "نسخة احتياطية 📥", 
        "تصفير الملفات 🗑️", "إنهاء ✅"
    ]
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def channel_markup(mid, interact_count=0):
    markup = types.InlineKeyboardMarkup()
    url = f"https://t.me/{BOT_USERNAME}?start=get_{mid}"
    markup.row(
        types.InlineKeyboardButton(f"استلم 📩", url=url),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f"hit_{mid}")
    )
    return markup

# --- 4. معالجة الأوامر ---
@bot.message_handler(commands=['start', 'admin'])
def start_logic(message):
    uid = message.from_user.id
    if str(uid) not in get_list("users.txt"):
        with open("users.txt", "a") as f: f.write(str(uid) + "\n")

    if message.text and "get_" in message.text:
        if not is_subscribed(uid):
            bot.send_message(uid, f"⚠️ يجب الاشتراك في القناة أولاً:\n{CHANNEL_ID}")
            return
        mid = message.text.split("_")[1]
        act = load_data("activity.json")
        if mid in act and str(uid) in act[mid].get("u_interact", []):
            files = get_list("bot_files.txt")
            if files:
                bot.send_message(uid, "✅ تفضل ملفاتك:")
                for fid in files: bot.send_document(uid, fid)
            else: bot.send_message(uid, "❌ لا توجد ملفات حالياً.")
        else: bot.send_message(uid, "⚠️ تفاعل ❤️ أولاً في القناة!")
        return

    if uid == OWNER_ID:
        bot.send_message(uid, "👑 أهلاً بك يا مدير.. تم تحديث لوحة التحكم بالخيارات الجديدة:", reply_markup=get_admin_panel())
    else:
        bot.send_message(uid, f"👋 أهلاً بك في البوت.\nتابع القناة {CHANNEL_ID} للحصول على ملفاتك.")

# --- 5. وظائف الإدارة (إذاعة القناة والمستخدمين) ---
@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID)
def admin_handler(message):
    uid, text = message.from_user.id, message.text

    if text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **تم تحديث الملفات!**\n📂 العدد: `{f_count}`\n⚠️ تفاعل ❤️ للاستلام.", parse_mode="Markdown")
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=channel_markup(str(msg.message_id)))
        bot.send_message(uid, "✅ تم النشر.")

    elif text == "إضافة ملفات 📤":
        bot.send_message(uid, "📥 أرسل الملفات، ثم اضغط **إنهاء ✅**", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_upload)

    elif text == "إذاعة للمستخدمين 👥":
        msg = bot.send_message(uid, "👥 أرسل الرسالة التي تريد إذاعتها لجميع **مستخدمي البوت**:")
        bot.register_next_step_handler(msg, lambda m: start_broadcast(m, "users"))

    elif text == "إذاعة للقناة 📢":
        msg = bot.send_message(uid, "📢 أرسل الرسالة التي تريد نشرها في **القناة** مباشرة:")
        bot.register_next_step_handler(msg, lambda m: start_broadcast(m, "channel"))

    elif text == "الإحصائيات 📊":
        u_count = len(get_list("users.txt"))
        f_count = len(get_list("bot_files.txt"))
        bot.send_message(uid, f"📊 **إحصائيات:**\n👤 مستخدمين: `{u_count}`\n📂 ملفات: `{f_count}`", parse_mode="Markdown")

    elif text == "نسخة احتياطية 📥":
        for f in ["users.txt", "bot_files.txt"]:
            if os.path.exists(f):
                with open(f, "rb") as doc: bot.send_document(uid, doc)

    elif text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم التصفير.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🛑 تم الخروج.", reply_markup=types.ReplyKeyboardRemove())

def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=get_admin_panel())
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 استلمت..")
    bot.register_next_step_handler(message, process_upload)

def start_broadcast(message, target):
    if target == "channel":
        try:
            bot.copy_message(CHANNEL_ID, message.chat.id, message.message_id)
            bot.send_message(OWNER_ID, "✅ تم نشر الرسالة في القناة بنجاح.")
        except Exception as e:
            bot.send_message(OWNER_ID, f"❌ فشل النشر في القناة: {e}")
    else:
        users = get_list("users.txt")
        bot.send_message(OWNER_ID, f"⏳ جاري الإذاعة لـ {len(users)} مستخدم...")
        success = 0
        for u in users:
            try:
                bot.copy_message(u, message.chat.id, message.message_id)
                success += 1
                time.sleep(0.05)
            except: continue
        bot.send_message(OWNER_ID, f"✅ اكتملت الإذاعة لـ {success} مستخدم.")

# --- 6. التفاعل والتشغيل ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.from_user.id)
    if call.data.startswith("hit_"):
        mid = call.data.split("_")[1]
        act = load_data("activity.json")
        if mid not in act: act[mid] = {"u_interact": [], "u_receive": []}
        if uid not in act[mid]["u_interact"]:
            act[mid]["u_interact"].append(uid)
            save_data("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً!")
            bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=channel_markup(mid, len(act[mid]["u_interact"])))
        else: bot.answer_callback_query(call.id, "⚠️ متفاعل مسبقاً!", show_alert=True)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Bot is running...")
    bot.polling(none_stop=True, interval=0, timeout=25)

