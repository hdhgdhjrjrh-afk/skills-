import telebot
from telebot import types
import os
import json
import time
import threading

# ==========================================
# 1. الإعدادات الأساسية (تأكد من تغيير التوكن للأمان)
# ==========================================
TOKEN = "8401184550:AAGAuRsvepOLeJKftFp46MAm6qvofbXA5dU" 
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# التأكد من ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "subs.json", "settings.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f == "settings.json": json.dump({"notify": True}, file)
            elif f.endswith(".json"): json.dump({}, file)
            else: file.write("")

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

# ==========================================
# 2. لوحات التحكم (Panel)
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
        if "إضافة" in perms: btns.append("إضافة ملفات 📤")
        if "نشر" in perms: btns.append("نشر بالقناة 📣")
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
    return keyboard

# ==========================================
# 3. الأوامر البرمجية
# ==========================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    uname = message.from_user.first_name
    
    # تسجيل المستخدم الجديد
    users = get_list("users.txt")
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(str(uid) + "\n")
        settings = load_json("settings.json")
        if settings.get("notify", True):
            try: bot.send_message(OWNER_ID, f"👤 مستخدم جديد دخل البوت:\nالاسم: {uname}\nالأيدي: `{uid}`", parse_mode="Markdown")
            except: pass

    # معالجة طلب الملفات (عند الضغط على "استلم" في القناة)
    if "get_" in message.text:
        mid = message.text.split("_")[1]
        data = load_json("activity.json")
        if mid not in data or str(uid) not in data[mid].get("u_interact", []):
            bot.send_message(uid, "⚠️ تفاعل بـ (❤️) على المنشور في القناة أولاً لتفعيل الرابط!")
            return
        
        files = get_list("bot_files.txt")
        if not files:
            bot.send_message(uid, "❌ لا توجد ملفات متوفرة حالياً.")
            return

        bot.send_message(uid, "🚀 جاري إرسال الملفات إليك...")
        for f_id in files:
            try: bot.send_document(uid, f_id)
            except: pass
        
        # تحديث عداد الاستلام
        if str(uid) not in data[mid].get("u_receive", []):
            data[mid].setdefault("u_receive", []).append(str(uid))
            data[mid]["r"] = len(data[mid]["u_receive"])
            save_json("activity.json", data)
        return

    # الترحيب بالمطور أو المستخدم العادي
    if uid == OWNER_ID:
        bot.send_message(uid, "مرحبا ايها مطور 😈SELVA ZOLDEK 😈مرحبا في نظام الوحش النظام جاهز للخدمة", reply_markup=get_panel(uid))
    else:
        bot.send_message(uid, f"أهلاً بك {uname} في نظام توزيع Uchiha ⚡", reply_markup=get_panel(uid))

# ==========================================
# 4. معالجة الأزرار والمهام
# ==========================================
@bot.message_handler(func=lambda m: True)
def handle_all_btns(message):
    uid = message.from_user.id
    text = message.text
    admins = load_json("admins.json")
    
    if uid == OWNER_ID: perms = ["نشر", "إضافة", "إذاعة", "إحصائيات", "حذف", "إدارة"]
    elif str(uid) in admins: perms = admins[str(uid)]
    else: return

    # 📊 الإحصائيات
    if text == "الإحصائيات 📊" and "إحصائيات" in perms:
        u_count = len(get_list("users.txt"))
        f_count = len(get_list("bot_files.txt"))
        activity = load_json("activity.json")
        total_interact = sum(v.get('i', 0) for v in activity.values())
        
        msg = f"📊 **إحصائيات النظام:**\n\n👤 المستخدمين: {u_count}\n📂 الملفات: {f_count}\n❤️ إجمالي التفاعلات: {total_interact}"
        bot.send_message(uid, msg, parse_mode="Markdown")

    # 🔔 إشعارات الدخول
    elif text == "تفعيل اشعار دخول ✅" and uid == OWNER_ID:
        save_json("settings.json", {"notify": True})
        bot.send_message(uid, "✅ تم تفعيل إشعارات الدخول بنجاح.")

    elif text == "ايقاف اشعار دخول ❌" and uid == OWNER_ID:
        save_json("settings.json", {"notify": False})
        bot.send_message(uid, "❌ تم إيقاف إشعارات الدخول.")

    # 📣 النشر بالقناة
    elif text == "نشر بالقناة 📣" and "نشر" in perms:
        sent = bot.send_message(CHANNEL_ID, "🔄 جاري النشر...")
        mid = str(sent.message_id)
        f_count = len(get_list("bot_files.txt"))
        msg_text = f"⚡ **تم تحديث الملفات بنجاح!**\n\n📂 عدد الملفات: {f_count}\n⚠️ تفاعل بـ ❤️ ثم اضغط استلم."
        bot.edit_message_text(msg_text, CHANNEL_ID, sent.message_id, reply_markup=create_inline_keyboard(0,0,mid), parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر في القناة.")

    # 📤 إضافة ملفات
    elif text == "إضافة ملفات 📤" and "إضافة" in perms:
        bot.send_message(uid, "📥 أرسل الملفات الآن، ثم اضغط (إنهاء ✅)", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, upload_worker)

    # 🗑️ حذف الملفات
    elif text == "حذف الملفات 🗑️" and "حذف" in perms:
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم تصفير سجل الملفات.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🏠 القائمة الرئيسية.", reply_markup=get_panel(uid))

def upload_worker(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم حفظ الملفات.", reply_markup=get_panel(message.from_user.id))
        return
    fid = message.document.file_id if message.document else (message.photo[-1].file_id if message.photo else None)
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 تم الاستلام.. أرسل التالي أو اضغط إنهاء.")
    bot.register_next_step_handler(message, upload_worker)

# ==========================================
# 5. التفاعل (Callback)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("interact_"))
def callback_handler(call):
    mid = call.data.split("_")[1]
    uid = call.from_user.id
    data = load_json("activity.json")
    
    if mid not in data: data[mid] = {"i": 0, "r": 0, "u_interact": [], "u_receive": []}
    
    if str(uid) not in data[mid]["u_interact"]:
        data[mid]["i"] += 1
        data[mid]["u_interact"].append(str(uid))
        save_json("activity.json", data)
        bot.answer_callback_query(call.id, "❤️ تم تسجيل تفاعلك! يمكنك الاستلام الآن.")
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, 
                                         reply_markup=create_inline_keyboard(data[mid]["i"], data[mid]["r"], mid))
        except: pass
    else:
        bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت بالفعل على هذا المنشور.", show_alert=True)

# تشغيل
print("-" * 30)
print("😈 SYSTEM SELVA IS READY")
print("-" * 30)
bot.infinity_polling()

