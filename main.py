import telebot
from telebot import types
import os
import json
import time
import threading

# =======================================================
# 1. الإعدادات والتهيئة (CONFIGURATIONS)
# =======================================================
TOKEN = "8401184550:AAGAuRsvepOLeJKftFp46MAm6qvofbXA5dU" 
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

# تحسين الأداء للسيرفر (1GB RAM)
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=25)
file_lock = threading.Lock() # لمنع تضارب البيانات عند الضغط العالي

# أسماء ملفات النظام
DB_USERS = "users.txt"
DB_FILES = "bot_files.txt"
DB_ACTIVITY = "activity.json"
DB_SETTINGS = "settings.json"

def initialize_database():
    """التأكد من وجود الملفات وقواعد البيانات عند التشغيل"""
    files = [DB_USERS, DB_FILES, DB_ACTIVITY, DB_SETTINGS]
    for f in files:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file:
                if f == DB_SETTINGS:
                    json.dump({"notify": True, "custom_caption": "⚡ **تحديث جديد!**\n📂 الملفات: {count}"}, file)
                elif f.endswith(".json"):
                    json.dump({}, file)
                else:
                    file.write("")

initialize_database()

# =======================================================
# 2. دوال التعامل مع البيانات (DATA TOOLS)
# =======================================================

def load_json(filename):
    with file_lock:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}

def save_json(filename, data):
    with file_lock:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# =======================================================
# 3. لوحات التحكم (KEYBOARDS)
# =======================================================

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if user_id == OWNER_ID:
        btns = [
            "إضافة ملفات 📤", "نشر بالقناة 📣", 
            "تخصيص بوست 📝", "الإحصائيات 📊", 
            "تفعيل اشعار دخول ✅", "ايقاف اشعار دخول ❌",
            "تصفير الإحصائيات ⚠️", "حذف الملفات 🗑️",
            "الدعم الفني 🛠️", "إنهاء ✅"
        ]
    else:
        btns = ["الدعم الفني 🛠️", "معلومات البوت ℹ️", "إنهاء ✅"]
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def get_inline_buttons(i_count=0, r_count=0, msg_id=""):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.row(
        types.InlineKeyboardButton(f"استلم 📩 ({r_count})", url=f"https://t.me/{BOT_USERNAME}?start=get_{msg_id}"),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({i_count})", callback_data=f'int_{msg_id}')
    )
    return keyboard

# =======================================================
# 4. معالجة الرسائل (MESSAGE HANDLERS)
# =======================================================

@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    
    # تسجيل المستخدم الجديد
    users = get_list(DB_USERS)
    if str(uid) not in users:
        with open(DB_USERS, "a") as f: f.write(str(uid) + "\n")
        settings = load_json(DB_SETTINGS)
        if settings.get("notify", True):
            try: bot.send_message(OWNER_ID, f"👤 مستخدم جديد:\nالاسم: {message.from_user.first_name}\nID: `{uid}`")
            except: pass

    # منطق استلام الملفات (Deep Linking)
    if "get_" in message.text:
        handle_file_request(message)
        return

    welcome_text = "أهلاً بك مطور SELVA ZOLDEK 😈" if uid == OWNER_ID else "أهلاً بك في نظام الوحش ⚡"
    bot.send_message(uid, welcome_text, reply_markup=get_main_keyboard(uid))

def handle_file_request(message):
    uid = message.from_user.id
    msg_id = message.text.split("_")[1]
    activity = load_json(DB_ACTIVITY)
    
    # شرط التفاعل أولاً
    if msg_id not in activity or str(uid) not in activity[msg_id].get("u_i", []):
        bot.send_message(uid, "⚠️ يجب أن تتفاعل بـ ❤️ تحت المنشور في القناة أولاً!")
        return
    
    files = get_list(DB_FILES)
    if not files:
        bot.send_message(uid, "❌ لا توجد ملفات حالياً.")
        return

    bot.send_message(uid, "✅ تم التحقق.. جاري إرسال الملفات:")
    for line in files:
        try:
            if "|" in line:
                fid, caption = line.split("|", 1)
                bot.send_document(uid, fid, caption=f"📄 **وصف الملف:**\n{caption}")
            else:
                bot.send_document(uid, line)
        except: pass
    
    # تحديث عداد الاستلام
    if str(uid) not in activity[msg_id].get("u_r", []):
        activity[msg_id].setdefault("u_r", []).append(str(uid))
        activity[msg_id]["r"] = len(activity[msg_id]["u_r"])
        save_json(DB_ACTIVITY, activity)
        try: bot.edit_message_reply_markup(CHANNEL_ID, int(msg_id), 
                                           reply_markup=get_inline_buttons(activity[msg_id]["i"], activity[msg_id]["r"], msg_id))
        except: pass

# =======================================================
# 5. منطق الأزرار والوظائف (ADMIN LOGIC)
# =======================================================

@bot.message_handler(func=lambda m: True)
def main_logic(message):
    uid, text = message.from_user.id, message.text
    if uid != OWNER_ID: return

    if text == "الإحصائيات 📊":
        u_count = len(get_list(DB_USERS))
        f_count = len(get_list(DB_FILES))
        act = load_json(DB_ACTIVITY)
        total_int = sum(v.get('i', 0) for v in act.values())
        msg = f"📊 **إحصائيات النظام:**\n\n👥 مستخدمين: {u_count}\n📂 ملفات: {f_count}\n❤️ تفاعلات: {total_int}"
        bot.send_message(uid, msg)

    elif text == "تخصيص بوست 📝":
        bot.send_message(uid, "📝 أرسل الوصف الجديد (استخدم {count} لعدد الملفات):")
        bot.register_next_step_handler(message, set_custom_caption)

    elif text == "نشر بالقناة 📣":
        handle_channel_post(uid)

    elif text == "إضافة ملفات 📤":
        bot.send_message(uid, "📥 أرسل الملف الآن:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, upload_process)

    elif text in ["تفعيل اشعار دخول ✅", "ايقاف اشعار دخول ❌"]:
        status = "تفعيل" in text
        settings = load_json(DB_SETTINGS)
        settings["notify"] = status
        save_json(DB_SETTINGS, settings)
        bot.send_message(uid, f"✅ تم {'تفعيل' if status else 'إيقاف'} الإشعارات.")

    elif text == "تصفير الإحصائيات ⚠️":
        save_json(DB_ACTIVITY, {})
        bot.send_message(uid, "✅ تم تصفير كافة الإحصائيات.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🏠 العودة للقائمة الرئيسية.", reply_markup=get_main_keyboard(uid))

# --- وظائف مساعدة للنظام ---

def set_custom_caption(message):
    settings = load_json(DB_SETTINGS)
    settings["custom_caption"] = message.text
    save_json(DB_SETTINGS, settings)
    bot.send_message(message.from_user.id, "✅ تم حفظ وصف القناة الجديد.")

def handle_channel_post(uid):
    sent = bot.send_message(CHANNEL_ID, "🔄 جاري التحضير...")
    mid = str(sent.message_id)
    files = get_list(DB_FILES)
    settings = load_json(DB_SETTINGS)
    caption = settings.get("custom_caption", "⚡ تحديث جديد!").replace("{count}", str(len(files)))
    bot.edit_message_text(caption, CHANNEL_ID, sent.message_id, reply_markup=get_inline_buttons(0, 0, mid))
    bot.send_message(uid, "✅ تم النشر في القناة بنجاح.")

def upload_process(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ انتهت عملية الرفع.", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    fid = message.document.file_id if message.document else (message.photo[-1].file_id if message.photo else None)
    if fid:
        bot.send_message(message.from_user.id, "📝 الآن أرسل وصفاً للملف:")
        bot.register_next_step_handler(message, lambda m: finalize_upload(m, fid))
    else:
        bot.send_message(message.from_user.id, "⚠️ أرسل ملفاً أو اضغط إنهاء.")
        bot.register_next_step_handler(message, upload_process)

def finalize_upload(message, fid):
    caption = message.text if message.text else "بدون وصف"
    with open(DB_FILES, "a", encoding="utf-8") as f:
        f.write(f"{fid}|{caption}\n")
    bot.send_message(message.from_user.id, "✅ تم الحفظ. أرسل الملف التالي أو 'إنهاء ✅'")
    bot.register_next_step_handler(message, upload_process)

# =======================================================
# 6. معالجة الضغطات (CALLBACKS)
# =======================================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid, data = str(call.from_user.id), call.data
    if data.startswith("int_"):
        mid = data.split("_")[1]
        act = load_json(DB_ACTIVITY)
        
        if mid not in act: act[mid] = {"i": 0, "r": 0, "u_i": [], "u_r": []}
        if uid not in act[mid]["u_i"]:
            act[mid]["i"] += 1
            act[mid]["u_i"].append(uid)
            save_json(DB_ACTIVITY, act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            try: bot.edit_message_reply_markup(CHANNEL_ID, int(mid), 
                                               reply_markup=get_inline_buttons(act[mid]["i"], act[mid]["r"], mid))
            except: pass
        else:
            bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت بالفعل!")

# =======================================================
# 7. التشغيل النهائي
# =======================================================

if __name__ == "__main__":
    print("😈 THE BEAST SYSTEM v3.5 IS ONLINE")
    print("💎 OWNER: SELVA ZOLDEK")
    print("🚀 MODE: HIGH TRAFFIC (1GB RAM OPTIMIZED)")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

