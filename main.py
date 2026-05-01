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

# تحسين الأداء للسيرفر (1GB RAM) وتفعيل تعدد المهام
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=30)
file_lock = threading.Lock() # لمنع تضارب البيانات عند ضغط المستخدمين

# أسماء ملفات النظام
DB_USERS = "users.txt"
DB_FILES = "bot_files.txt"
DB_ACTIVITY = "activity.json"
DB_SETTINGS = "settings.json"
DB_ADMINS = "admins.json"
DB_SUBS = "subs.json"

def initialize_database():
    """إنشاء ملفات النظام إذا لم تكن موجودة"""
    files = [DB_USERS, DB_FILES, DB_ACTIVITY, DB_SETTINGS, DB_ADMINS, DB_SUBS]
    for f in files:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file:
                if f == DB_SETTINGS:
                    json.dump({"notify": True, "custom_caption": "⚡ **تحديث جديد!**\n📂 الملفات: {count}"}, file)
                elif f == DB_SUBS: json.dump([], file)
                elif f.endswith(".json"): json.dump({}, file)
                else: file.write("")

initialize_database()
temp_admin_perms = {} # مخزن مؤقت للصلاحيات

# =======================================================
# 2. دوال التعامل مع البيانات بأمان (DATA TOOLS)
# =======================================================

def load_json(filename):
    with file_lock:
        try:
            with open(filename, "r", encoding="utf-8") as f: return json.load(f)
        except: return [] if "subs" in filename else {}

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
            "إضافة ملفات 📤", "نشر بالقناة 📣", "تخصيص بوست 📝",
            "إدارة الإشتراك 📢", "تفعيل اشعار دخول ✅", "ايقاف اشعار دخول ❌",
            "إذاعة للمشتركين 👥", "إدارة المشرفين 👮‍♂️", "الإحصائيات 📊", 
            "تصفير الإحصائيات ⚠️", "حذف الملفات 🗑️", "إنهاء ✅"
        ]
    else:
        admins = load_json(DB_ADMINS)
        perms = admins.get(str(user_id), [])
        btns = []
        if "إضافة" in perms: btns.append("إضافة ملفات 📤")
        if "نشر" in perms: btns.append("نشر بالقناة 📣")
        if "إذاعة" in perms: btns.append("إذاعة للمشتركين 👥")
        if "إحصائيات" in perms: btns.append("الإحصائيات 📊")
        if "حذف" in perms: btns.append("حذف الملفات 🗑️")
        btns.extend(["الدعم الفني 🛠️", "معلومات البوت ℹ️", "إنهاء ✅"])
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def get_inline_buttons(i_count=0, r_count=0, msg_id=""):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.row(
        types.InlineKeyboardButton(f"استلم 📩 ({r_count})", url=f"https://t.me/{BOT_USERNAME}?start=get_{msg_id}"),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({i_count})", callback_data=f'int_{msg_id}')
    )
    return keyboard

def create_perms_keyboard(admin_id):
    perms = temp_admin_perms.get(str(admin_id), [])
    markup = types.InlineKeyboardMarkup(row_width=2)
    options = {"نشر": "نشر 📣", "إضافة": "إضافة 📤", "إذاعة": "إذاعة 👥", "إحصائيات": "إحصائيات 📊", "حذف": "حذف 🗑️"}
    btns = [types.InlineKeyboardButton(f"{label} {'✅' if key in perms else '❌'}", callback_data=f"tg_{key}_{admin_id}") for key, label in options.items()]
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("حفظ الصلاحيات 💾", callback_data=f"sv_{admin_id}"))
    return markup

# =======================================================
# 4. معالجة الأوامر والملفات (CORE LOGIC)
# =======================================================

@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    users = get_list(DB_USERS)
    
    if str(uid) not in users:
        with open(DB_USERS, "a") as f: f.write(str(uid) + "\n")
        settings = load_json(DB_SETTINGS)
        if settings.get("notify", True):
            try: bot.send_message(OWNER_ID, f"👤 مستخدم جديد:\nالاسم: {message.from_user.first_name}\nID: `{uid}`")
            except: pass

    if "get_" in message.text:
        handle_file_request(message)
        return

    welcome_text = "أهلاً بك مطور SELVA ZOLDEK 😈" if uid == OWNER_ID else "أهلاً بك في نظام الوحش ⚡"
    bot.send_message(uid, welcome_text, reply_markup=get_main_keyboard(uid))

def handle_file_request(message):
    uid, mid = message.from_user.id, message.text.split("_")[1]
    act = load_json(DB_ACTIVITY)
    
    if mid not in act or str(uid) not in act[mid].get("u_i", []):
        bot.send_message(uid, "⚠️ تفاعل أولاً ❤️ في القناة لتستلم الملفات!")
        return
    
    files = get_list(DB_FILES)
    if not files:
        bot.send_message(uid, "❌ لا توجد ملفات حالياً."); return

    bot.send_message(uid, "✅ جاري إرسال الملفات مع الوصف:")
    for line in files:
        try:
            fid, cap = line.split("|", 1) if "|" in line else (line, "بدون وصف")
            bot.send_document(uid, fid, caption=f"📄 **الوصف:**\n{cap}")
        except: pass
    
    if str(uid) not in act[mid].get("u_r", []):
        act[mid].setdefault("u_r", []).append(str(uid))
        act[mid]["r"] = len(act[mid]["u_r"])
        save_json(DB_ACTIVITY, act)
        try: bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=get_inline_buttons(act[mid]["i"], act[mid]["r"], mid))
        except: pass

# =======================================================
# 5. إدارة الإذاعة والمشرفين (ADMIN FUNCTIONS)
# =======================================================

@bot.message_handler(func=lambda m: True)
def main_logic(message):
    uid, text = message.from_user.id, message.text
    admins = load_json(DB_ADMINS)
    perms = ["نشر", "إضافة", "إذاعة", "إحصائيات", "حذف"] if uid == OWNER_ID else admins.get(str(uid), [])

    if text == "الإحصائيات 📊" and "إحصائيات" in perms:
        u, f = len(get_list(DB_USERS)), len(get_list(DB_FILES))
        act = load_json(DB_ACTIVITY)
        ti = sum(v.get('i', 0) for v in act.values())
        bot.send_message(uid, f"📊 **إحصائيات الوحش:**\n👥 مستخدمين: {u}\n📂 ملفات: {f}\n❤️ تفاعلات: {ti}")

    elif text == "نشر بالقناة 📣" and "نشر" in perms:
        sent = bot.send_message(CHANNEL_ID, "🔄 جاري النشر...")
        f_count = len(get_list(DB_FILES))
        settings = load_json(DB_SETTINGS)
        cap = settings.get("custom_caption", "").replace("{count}", str(f_count))
        bot.edit_message_text(cap, CHANNEL_ID, sent.message_id, reply_markup=get_inline_buttons(0, 0, str(sent.message_id)))
        bot.send_message(uid, "✅ تم النشر.")

    elif text == "إذاعة للمشتركين 👥" and "إذاعة" in perms:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("اذاعة مستخدمين", "اذاعة قناة", "اذاعة جميع", "إنهاء ✅")
        bot.send_message(uid, "اختر نوع الإذاعة:", reply_markup=kb)
        bot.register_next_step_handler(message, lambda m: bot.send_message(uid, "أرسل الرسالة:") or bot.register_next_step_handler(m, lambda msg: start_broadcast(msg, m.text)))

    elif text == "إدارة المشرفين 👮‍♂️" and uid == OWNER_ID:
        bot.send_message(uid, "🆔 أرسل ID المستخدم:")
        bot.register_next_step_handler(message, process_admin_id)

    elif text == "إضافة ملفات 📤" and "إضافة" in perms:
        bot.send_message(uid, "📥 أرسل الملف الآن:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, upload_worker)

    elif text == "تخصيص بوست 📝" and uid == OWNER_ID:
        bot.send_message(uid, "📝 أرسل الوصف الجديد (استخدم {count}):")
        bot.register_next_step_handler(message, save_caption_logic)

    elif text == "إدارة الإشتراك 📢" and uid == OWNER_ID:
        subs = load_json(DB_SUBS)
        bot.send_message(uid, f"📢 القنوات: {subs}\nأرسل @المعرف للإضافة أو 'حذف @المعرف'")
        bot.register_next_step_handler(message, manage_subs_logic)

    elif text == "تصفير الإحصائيات ⚠️" and uid == OWNER_ID:
        save_json(DB_ACTIVITY, {}); bot.send_message(uid, "✅ تم التصفير.")

    elif text == "حذف الملفات 🗑️" and "حذف" in perms:
        open(DB_FILES, "w").close(); bot.send_message(uid, "🗑️ تم المسح.")

    elif text == "إنهاء ✅": bot.send_message(uid, "🏠 الرئيسية.", reply_markup=get_main_keyboard(uid))

# --- دوال المساعدة ---
def start_broadcast(message, b_type):
    if message.text == "إنهاء ✅": return
    users, count = get_list(DB_USERS), 0
    for u in users:
        try:
            bot.copy_message(u, message.chat.id, message.message_id)
            count += 1
            if count % 20 == 0: time.sleep(1) # حماية من الحظر
        except: continue
    bot.send_message(message.from_user.id, f"✅ تم للإجمالي {count} مستخدم.")

def process_admin_id(message):
    aid = message.text
    if not aid.isdigit(): return
    temp_admin_perms[aid] = load_json(DB_ADMINS).get(aid, [])
    bot.send_message(OWNER_ID, f"⚙️ صلاحيات `{aid}`:", reply_markup=create_perms_keyboard(aid))

def upload_worker(message):
    if message.text == "إنهاء ✅": 
        bot.send_message(message.from_user.id, "✅ تم.", reply_markup=get_main_keyboard(message.from_user.id))
        return
    fid = message.document.file_id if message.document else (message.photo[-1].file_id if message.photo else None)
    if fid:
        bot.send_message(message.from_user.id, "📝 أرسل وصف الملف:")
        bot.register_next_step_handler(message, lambda m: finalize_upload(m, fid))
    else: bot.register_next_step_handler(message, upload_worker)

def finalize_upload(message, fid):
    cap = message.text if message.text else "بدون وصف"
    with open(DB_FILES, "a", encoding="utf-8") as f: f.write(f"{fid}|{cap}\n")
    bot.send_message(message.from_user.id, "✅ تم. أرسل غيره أو 'إنهاء ✅'")
    bot.register_next_step_handler(message, upload_worker)

def save_caption_logic(message):
    s = load_json(DB_SETTINGS); s["custom_caption"] = message.text; save_json(DB_SETTINGS, s)
    bot.send_message(message.from_user.id, "✅ تم الحفظ.")

def manage_subs_logic(message):
    t, subs = message.text.strip(), load_json(DB_SUBS)
    if "حذف " in t: 
        target = t.replace("حذف ", "")
        if target in subs: subs.remove(target)
    elif t.startswith("@"): subs.append(t)
    save_json(DB_SUBS, list(set(subs)))
    bot.send_message(OWNER_ID, "✅ تم التحديث.")

# =======================================================
# 6. معالجة الضغطات (CALLBACKS)
# =======================================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid, data = str(call.from_user.id), call.data
    if data.startswith("int_"):
        mid = data.split("_")[1]; act = load_json(DB_ACTIVITY)
        if mid not in act: act[mid] = {"i": 0, "r": 0, "u_i": [], "u_r": []}
        if uid not in act[mid]["u_i"]:
            act[mid]["i"] += 1; act[mid]["u_i"].append(uid); save_json(DB_ACTIVITY, act)
            bot.answer_callback_query(call.id, "❤️ شكراً!")
            try: bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=get_inline_buttons(act[mid]["i"], act[mid]["r"], mid))
            except: pass
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً.")
    elif data.startswith("tg_"):
        _, p, aid = data.split("_")
        if p in temp_admin_perms.get(aid, []): temp_admin_perms[aid].remove(p)
        else: temp_admin_perms.setdefault(aid, []).append(p)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_perms_keyboard(aid))
    elif data.startswith("sv_"):
        aid = data.split("_")[1]; admins = load_json(DB_ADMINS); admins[aid] = temp_admin_perms.get(aid, [])
        save_json(DB_ADMINS, admins); bot.edit_message_text(f"✅ تم حفظ صلاحيات `{aid}`", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    print("😈 THE BEAST v4.0 IS ONLINE - OWNER: SELVA ZOLDEK")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

