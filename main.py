import telebot
from telebot import types
import os
import json

# ==========================================
# 1. الإعدادات والتهيئة
# ==========================================
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# التأكد من سلامة ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "settings.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f == "settings.json": json.dump({"notifications": True}, file)
            elif f.endswith(".json"): json.dump({}, file)
            else: file.write("")

# ==========================================
# 2. إدارة البيانات (مُصححة ومضمونة)
# ==========================================

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f: return [line.strip() for line in f if line.strip()]

def is_admin(user_id):
    admins = load_json("admins.json")
    admin_list = [str(a) for a in (admins if isinstance(admins, list) else [])]
    return user_id == OWNER_ID or str(user_id) in admin_list

# ==========================================
# 3. واجهة المستخدم (مطابقة للصور)
# ==========================================

def get_admin_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = load_json("settings.json")
    notif_btn = "إيقاف الإشعارات ❌" if settings.get("notifications", True) else "تفعيل الإشعارات ✅"
    
    markup.add(types.KeyboardButton("نشر في القناة 📢"), types.KeyboardButton("إضافة ملفات 📤"))
    markup.add(types.KeyboardButton("الإحصائيات 📊"), types.KeyboardButton(notif_btn))
    markup.add(types.KeyboardButton("تصفير الملفات 🗑️"), types.KeyboardButton("تنظيف البيانات 🧹"))
    
    if user_id == OWNER_ID: markup.add(types.KeyboardButton("إضافة أدمن ➕"))
    markup.add(types.KeyboardButton("إنهاء ✅"))
    return markup

def get_channel_markup(mid, interact_count=0, receive_count=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # تنسيق الزرين في سطر واحد
    markup.row(
        types.InlineKeyboardButton(f"استلم ({receive_count}) 📩", callback_data=f"rcv_{mid}"),
        types.InlineKeyboardButton(f"تفاعل ({interact_count}) ❤️", callback_data=f"hit_{mid}")
    )
    markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", url=f"https://t.me/{BOT_USERNAME}?start=activate"))
    return markup

# ==========================================
# 4. معالجة التفاعل ومنع التكرار (Callback)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid, mid, data = call.from_user.id, str(call.message.message_id), call.data
    users = get_list("users.txt")

    if str(uid) not in users:
        return bot.answer_callback_query(call.id, "⚠️ فعّل البوت أولاً (الزر بالأسفل)!", show_alert=True)

    act = load_json("activity.json")
    if mid not in act: act[mid] = {"h": [], "r": []}

    # تفاعل ❤️
    if "hit_" in data:
        if uid not in act[mid]["h"]:
            act[mid]["h"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            bot.edit_message_reply_markup(call.message.chat.id, int(mid), 
                reply_markup=get_channel_markup(mid, len(act[mid]["h"]), len(act[mid]["r"])))
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً!", show_alert=True)

    # استلام 📩
    elif "rcv_" in data:
        if uid not in act[mid]["r"]:
            act[mid]["r"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "📩 تفقد الخاص!")
            bot.edit_message_reply_markup(call.message.chat.id, int(mid), 
                reply_markup=get_channel_markup(mid, len(act[mid]["h"]), len(act[mid]["r"])))
            
            files = get_list("bot_files.txt")
            if files:
                bot.send_message(uid, f"📦 تم استلام {len(files)} ملفات:")
                for f in files:
                    try: bot.send_document(uid, f)
                    except: pass
            else: bot.send_message(uid, "⚠️ السجل فارغ حالياً.")
        else: bot.answer_callback_query(call.id, "⚠️ استلمت مسبقاً!", show_alert=True)

# ==========================================
# 5. أوامر الإدارة (مطابقة للوصف)
# ==========================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    users = get_list("users.txt")
    
    # إشعار دخول جديد للمطور
    if str(uid) not in users and "activate" not in message.text:
        settings = load_json("settings.json")
        if settings.get("notifications", True):
            uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
            noti = (f"👤 **دخول مستخدم جديد!**\n\nالاسم: {message.from_user.first_name}\nالآيدي: `{uid}`\nاليوزر: {uname}")
            try: bot.send_message(OWNER_ID, noti, parse_mode="Markdown")
            except: pass

    if "activate" in message.text:
        if str(uid) not in users:
            with open("users.txt", "a") as f: f.write(f"{uid}\n")
        bot.send_message(uid, "✅ تم تفعيل البوت!")
        return

    if is_admin(uid):
        bot.send_message(uid, "👑 لوحة تحكم الإدارة المصلحة:", reply_markup=get_admin_panel(uid))
    else:
        bot.send_message(uid, "👋 أهلاً بك! استخدم الأزرار في القناة.")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_process(message):
    uid, text = message.from_user.id, message.text
    
    if text == "نشر في القناة 📢":
        f_count = len(get_list("bot_files.txt"))
        msg_text = (f"⚡ **تم تجديد الكونفيجات!**\n\n📄 عدد الملفات المتاحة: {f_count}\n"
                    "🚀 سرعة عالية | ⏳ محدد المدة\n__________________________\n"
                    "📌 **طريقة الاستلام:**\n1️⃣ فعّل البوت (🤖)\n2️⃣ تفاعل (❤️)\n3️⃣ استلم (📩)\n__________________________")
        bot.send_message(CHANNEL_ID, msg_text, reply_markup=get_channel_markup("main"), parse_mode="Markdown")
        bot.send_message(uid, f"✅ تم النشر بنجاح. العدد: {f_count}")

    elif text == "إضافة ملفات 📤":
        msg = bot.send_message(uid, "📤 أرسل الملفات الآن.. ثم اضغط إنهاء ✅", 
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(msg, process_upload)

    elif "الإشعارات" in text:
        settings = load_json("settings.json")
        settings["notifications"] = not settings.get("notifications", True)
        save_json("settings.json", settings)
        bot.send_message(uid, "⚙️ تم تحديث الإعدادات.", reply_markup=get_admin_panel(uid))

    elif text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم المسح بنجاح.")

def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=get_admin_panel(message.from_user.id))
        return
    f_id = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if f_id:
        with open("bot_files.txt", "a") as f: f.write(f"{f_id}\n")
        bot.send_message(message.from_user.id, "📥 تم الاستلام.. أرسل المزيد أو اضغط إنهاء ✅")
    bot.register_next_step_handler(message, process_upload)

if __name__ == "__main__":
    bot.infinity_polling()
