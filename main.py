import telebot
from telebot import types
import os
import json
import time

# --- 1. الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
BOT_USERNAME = "gudurjbot"
CHANNEL_ID = "@Uchiha75"

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "subs.json", "admins.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump([] if f in ["subs.json", "admins.json"] else {}, file)
            else: file.write("")

# --- 2. دالات المساعدة ---
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)
    except: return [] if "subs" in filename or "admins" in filename else {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def is_admin(user_id):
    admins = load_json("admins.json")
    return user_id == OWNER_ID or user_id in admins

def is_subscribed(user_id):
    subs = load_json("subs.json")
    if not subs: return True
    for ch in subs:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status in ['left', 'kicked']: return False
        except: continue 
    return True

# --- 3. لوحة التحكم ---
def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        "نشر تلقائي 📣", "إضافة ملفات 📤", 
        "إذاعة للمستخدمين 👥", "إذاعة للقناة 📢", 
        "إدارة الاشتراك 📢", "الإحصائيات 📊"
    ]
    if user_id == OWNER_ID:
        btns.append("إضافة أدمن ➕")
    
    btns.extend(["نسخة احتياطية 📥", "تصفير الملفات 🗑️", "إنهاء ✅"])
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def channel_markup(mid, interact_count=0):
    markup = types.InlineKeyboardMarkup()
    url = f"https://t.me/{BOT_USERNAME}?start=get_{mid}"
    markup.row(
        types.InlineKeyboardButton(f"استلم 📩", url=url),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f"hit_{mid}")
    )
    subs = load_json("subs.json")
    for ch in subs:
        markup.add(types.InlineKeyboardButton("اشترك هنا ✅", url=f"https://t.me/{ch.replace('@','')}"))
    return markup

# --- 4. الأوامر الأساسية ---
@bot.message_handler(commands=['start', 'admin'])
def start_cmd(message):
    uid = message.from_user.id
    if str(uid) not in get_list("users.txt"):
        with open("users.txt", "a") as f: f.write(str(uid) + "\n")

    if message.text and "get_" in message.text:
        if not is_subscribed(uid):
            bot.send_message(uid, "⚠️ عذراً، يجب عليك الاشتراك في القنوات أولاً!")
            return
        
        mid = message.text.split("_")[1]
        act = load_json("activity.json")
        
        # تسجيل أن المستخدم استلم الملفات
        if mid in act:
            if str(uid) not in act[mid].get("u_receive", []):
                act[mid].setdefault("u_receive", []).append(str(uid))
                save_json("activity.json", act)

        bot.send_message(uid, "✅ تم التحقق.. جاري إرسال ملفاتك.")
        files = get_list("bot_files.txt")
        for f in files: bot.send_document(uid, f)
        return

    if is_admin(uid):
        bot.send_message(uid, "👑 مرحباً بك في لوحة الإدارة:", reply_markup=get_panel(uid))
    else:
        bot.send_message(uid, "👋 أهلاً بك في البوت. اشترك في القناة ليصلك كل جديد.")

# --- 5. وظائف الإحصائيات والأدمن ---
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_handler(message):
    uid, text = message.from_user.id, message.text

    if text == "الإحصائيات 📊":
        act = load_json("activity.json")
        total_interact = 0
        total_receive = 0
        # حساب المجموع الكلي من جميع المنشورات
        for mid in act:
            total_interact += len(act[mid].get("u_interact", []))
            total_receive += len(act[mid].get("u_receive", []))
            
        msg = (f"📊 **إحصائيات البوت الكلية:**\n\n"
               f"👥 عدد المشتركين: `{len(get_list('users.txt'))}`\n"
               f"📂 عدد الملفات: `{len(get_list('bot_files.txt'))}`\n"
               f"❤️ إجمالي المتفاعلين: `{total_interact}`\n"
               f"📩 إجمالي المستلمين: `{total_receive}`")
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif text == "إضافة أدمن ➕" and uid == OWNER_ID:
        msg = bot.send_message(uid, "👤 أرسل (ID) الشخص الذي تريد تعيينه كأدمن:")
        bot.register_next_step_handler(msg, save_admin)

    elif text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **تم تحديث الملفات!**\n📂 العدد: `{f_count}`\n⚠️ تفاعل ❤️ للاستلام.", parse_mode="Markdown")
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=channel_markup(str(msg.message_id)))
        bot.send_message(uid, "✅ تم النشر.")

    elif text == "إضافة ملفات 📤":
        bot.send_message(uid, "📥 أرسل الملفات ثم اضغط **إنهاء ✅**", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_upload)

    elif text == "إدارة الاشتراك 📢":
        subs = load_json("subs.json")
        list_txt = "\n".join([f"{i+1}- {ch}" for i, ch in enumerate(subs)])
        bot.send_message(uid, f"📢 القنوات:\n{list_txt if subs else 'لا توجد'}\n\nأرسل المعرف للإضافة أو الرقم للحذف.")
        bot.register_next_step_handler(message, process_sub_update)

    elif text == "إنهاء ✅":
        bot.send_message(uid, "👋 تم إغلاق القائمة.", reply_markup=types.ReplyKeyboardRemove())

# --- 6. دالات المعالجة الفرعية ---
def save_admin(message):
    if message.text.isdigit():
        admins = load_json("admins.json")
        new_admin = int(message.text)
        if new_admin not in admins:
            admins.append(new_admin)
            save_json("admins.json", admins)
            bot.send_message(OWNER_ID, "✅ تم إضافة الأدمن بنجاح.")
        else:
            bot.send_message(OWNER_ID, "❌ هذا الشخص أدمن بالفعل.")
    else:
        bot.send_message(OWNER_ID, "❌ أرسل ID صحيح (أرقام فقط).")

def process_sub_update(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "🛑 تم الحفظ.", reply_markup=get_panel(message.from_user.id))
        return
    subs = load_json("subs.json")
    if message.text.startswith("@"):
        subs.append(message.text.strip())
        save_json("subs.json", list(set(subs)))
        bot.send_message(message.from_user.id, "✅ تمت الإضافة.")
    bot.register_next_step_handler(message, process_sub_update)

def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=get_panel(message.from_user.id))
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 استلمت..")
    bot.register_next_step_handler(message, process_upload)

# --- 7. التشغيل ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.from_user.id)
    if call.data.startswith("hit_"):
        mid = call.data.split("_")[1]
        act = load_json("activity.json")
        if mid not in act: act[mid] = {"u_interact": [], "u_receive": []}
        if uid not in act[mid]["u_interact"]:
            act[mid]["u_interact"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً!")
            bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=channel_markup(mid, len(act[mid]["u_interact"])))

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 البوت يعمل الآن..")
    bot.polling(none_stop=True)
