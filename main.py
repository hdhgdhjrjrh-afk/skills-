import telebot
from telebot import types
import os
import json
import time
import threading

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = "8401184550:AAGAuRsvepOLeJKftFp46MAm6qvofbXA5dU" 
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "subs.json", "settings.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): 
                # إعدادات افتراضية للإشعارات
                json.dump({"notify": True} if f == "settings.json" else ([] if f == "subs.json" else {}), file)
            else: file.write("")

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

# ==========================================
# 2. لوحات التحكم
# ==========================================
def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if user_id == OWNER_ID:
        btns = ["إضافة ملفات 📤", "نشر بالقناة 📣", "إدارة الإشتراك 📢", 
                "تفعيل اشعار دخول ✅", "ايقاف اشعار دخول ❌",
                "إذاعة للمشتركين 👥", "إدارة المشرفين 👮‍♂️", "الإحصائيات 📊", "حذف الملفات 🗑️", "إنهاء ✅"]
    else:
        admins = load_json("admins.json")
        perms = admins.get(str(user_id), [])
        btns = []
        if "نشر" in perms: btns.append("نشر بالقناة 📣")
        if "إضافة" in perms: btns.append("إضافة ملفات 📤")
        if "إذاعة" in perms: btns.append("إذاعة للمشتركين 👥")
        if "إحصائيات" in perms: btns.append("الإحصائيات 📊")
        if "حذف" in perms: btns.append("حذف الملفات 🗑️")
        btns.append("إنهاء ✅")
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def create_inline_keyboard(interact_count=0, receive_count=0, msg_id=""):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.row(
        types.InlineKeyboardButton(f"استلم 📩 ({receive_count})", url=f"https://t.me/{BOT_USERNAME}?start=get_{msg_id}"),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f'interact_{msg_id}')
    )
    subs = load_json("subs.json")
    for ch in subs:
        url = f"https://t.me/{ch.replace('@','')}" if ch.startswith("@") else ch
        keyboard.add(types.InlineKeyboardButton("اشترك هنا ✅", url=url))
    return keyboard

# ==========================================
# 3. معالجة الأوامر (Start)
# ==========================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    uname = message.from_user.first_name
    u_username = f"@{message.from_user.username}" if message.from_user.username else "بدون معرف"
    
    # تفقد المستخدم الجديد
    users_list = get_list("users.txt")
    if str(uid) not in users_list:
        with open("users.txt", "a", encoding="utf-8") as f: f.write(str(uid) + "\n")
        
        # إشعار دخول للمطور
        settings = load_json("settings.json")
        if settings.get("notify", True):
            try:
                bot.send_message(OWNER_ID, f"👤 **مستخدم جديد دخل البوت!**\n\nالاسم: {uname}\nالمعرف: {u_username}\nالأيدي: `{uid}`", parse_mode="Markdown")
            except: pass

    # رسالة الترحيب للمطور
    if uid == OWNER_ID:
        welcome_msg = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈مرحبا في نظام الوحش النظام جاهز للخدمة"
        bot.send_message(uid, welcome_msg, reply_markup=get_panel(uid))
        return

    # إذا كان المستخدم يطلب ملفات
    if "get_" in message.text:
        # (نفس منطق استلام الملفات السابق...)
        mid = message.text.split("_")[1]
        data = load_json("activity.json")
        if mid not in data or str(uid) not in data[mid].get("u_interact", []):
            bot.send_message(uid, "⚠️ يجب عليك التفاعل بـ (❤️) على المنشور في القناة أولاً!")
            return
        files = get_list("bot_files.txt")
        bot.send_message(uid, "🚀 جاري إرسال الملفات...")
        for f in files:
            try: bot.send_document(uid, f)
            except: pass
        return

    bot.send_message(uid, f"أهلاً بك {uname} في بوت توزيع الكونفيجات ⚡", reply_markup=get_panel(uid))

# ==========================================
# 4. معالجة الأزرار والوظائف
# ==========================================
@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    uid = message.from_user.id
    text = message.text
    settings = load_json("settings.json")

    # إشعارات الدخول (للمطور فقط)
    if uid == OWNER_ID:
        if text == "تفعيل اشعار دخول ✅":
            settings["notify"] = True
            save_json("settings.json", settings)
            bot.send_message(uid, "✅ تم تفعيل إشعارات الدخول.")
            return
        elif text == "ايقاف اشعار دخول ❌":
            settings["notify"] = False
            save_json("settings.json", settings)
            bot.send_message(uid, "❌ تم إيقاف إشعارات الدخول.")
            return

    # التحقق من الصلاحيات للمهام الأخرى
    admins = load_json("admins.json")
    if uid == OWNER_ID: perms = ["نشر", "إضافة", "إذاعة", "إحصائيات", "حذف"]
    elif str(uid) in admins: perms = admins[str(uid)]
    else: return

    if text == "نشر بالقناة 📣" and "نشر" in perms:
        sent_msg = bot.send_message(CHANNEL_ID, "🔄 جاري النشر...")
        mid = str(sent_msg.message_id)
        f_count = len(get_list("bot_files.txt"))
        msg_text = f"⚡ **تحديث جديد للكونفيجات!**\n\n📂 الملفات: {f_count}\n❤️ تفاعل لتفعيل رابط الاستلام."
        bot.edit_message_text(msg_text, CHANNEL_ID, sent_msg.message_id, 
                              reply_markup=create_inline_keyboard(0, 0, mid), parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر.")

    elif text == "إضافة ملفات 📤" and "إضافة" in perms:
        bot.send_message(uid, "📥 أرسل الملفات الآن، ثم اضغط (إنهاء ✅)", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_batch_upload)

    elif text == "الإحصائيات 📊" and "إحصائيات" in perms:
        u_count = len(get_list("users.txt"))
        f_count = len(get_list("bot_files.txt"))
        bot.send_message(uid, f"📊 **إحصائيات النظام:**\n\n👤 المستخدمين: {u_count}\n📂 الملفات: {f_count}")

    elif text == "حذف الملفات 🗑️" and "حذف" in perms:
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم تصفير سجل الملفات.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🏠 القائمة الرئيسية", reply_markup=get_panel(uid))

# دالة رفع الملفات
def process_batch_upload(message):
    global pending_files
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=get_panel(message.from_user.id))
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        with open("bot_files.txt", "a") as f: f.write(f"{fid}\n")
        bot.send_message(message.from_user.id, "📥 استلمت الملف.. أرسل غيره أو اضغط إنهاء.")
    bot.register_next_step_handler(message, process_batch_upload)

# ==========================================
# 5. التفاعل Callback
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("interact_"))
def handle_interaction(call):
    mid = call.data.split("_")[1]
    uid = call.from_user.id
    data = load_json("activity.json")
    
    if mid not in data: data[mid] = {"i": 0, "r": 0, "u_interact": [], "u_receive": []}
    
    if str(uid) not in data[mid]["u_interact"]:
        data[mid]["i"] += 1
        data[mid]["u_interact"].append(str(uid))
        save_json("activity.json", data)
        bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, 
                                     reply_markup=create_inline_keyboard(data[mid]["i"], data[mid]["r"], mid))
    else:
        bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً.")

# تشغيل البوت
print("😈 SYSTEM SELVA IS READY")
bot.infinity_polling()

