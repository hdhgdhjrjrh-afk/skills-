import telebot
from telebot import types
import os
import json
import time
import threading

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75"  # يجب رفع البوت أدمن في القناة
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# إنشاء ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "settings.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f == "settings.json": json.dump({"notifications": True}, file)
            elif f.endswith(".json"): json.dump({} if "activity" in f else [], file)
            else: file.write("")

# ==========================================
# 2. دالات إدارة البيانات والنظام
# ==========================================
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)
    except: return {} if "activity" in filename else []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f: return [line.strip() for line in f if line.strip()]

def is_admin(user_id):
    admins = load_json("admins.json")
    return user_id == OWNER_ID or user_id in admins

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['creator', 'administrator', 'member']
    except: return True # تمرير المستخدم في حال تعذر الفحص

def clean_old_activity():
    act = load_json("activity.json")
    if not act: return 0
    keys = list(act.keys())
    if len(keys) > 50:
        new_act = {k: act[k] for k in keys[-50:]}
        save_json("activity.json", new_act)
        return len(keys) - 50
    return 0

# ==========================================
# 3. لوحات التحكم (الواجهة)
# ==========================================
def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = load_json("settings.json")
    notif_btn = "إيقاف الإشعارات ❌" if settings.get("notifications", True) else "تفعيل الإشعارات ✅"
    
    btns = [
        "نشر تلقائي 📣", "إضافة ملفات 📤", 
        "إذاعة للمستخدمين 👥", "الإحصائيات 📊", 
        notif_btn, "تنظيف البيانات 🧹", 
        "تصفير الملفات 🗑️", "إنهاء ✅"
    ]
    if user_id == OWNER_ID: btns.append("إضافة أدمن ➕")
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

# ==========================================
# 4. معالجة الأوامر والرسائل
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    settings = load_json("settings.json")
    
    # تسجيل المستخدم وإشعار الدخول
    if str(uid) not in get_list("users.txt"):
        with open("users.txt", "a") as f: f.write(str(uid) + "\n")
        if settings.get("notifications", True):
            try: bot.send_message(OWNER_ID, f"👤 **مستخدم جديد:** [{message.from_user.first_name}](tg://user?id={uid})", parse_mode="Markdown")
            except: pass

    # معالجة استلام الملفات (زر استلم)
    if "get_" in message.text:
        if not check_sub(uid):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("اشترك هنا أولاً ✅", url=f"https://t.me/{CHANNEL_ID.replace('@','')}"))
            bot.send_message(uid, f"⚠️ يجب عليك الاشتراك في القناة {CHANNEL_ID} لتتمكن من استلام الملفات.", reply_markup=markup)
            return

        files = get_list("bot_files.txt")
        if not files:
            bot.send_message(uid, "❌ السجل فارغ حالياً.")
        else:
            bot.send_message(uid, "✅ جاري إرسال جميع الملفات المرفوعة...")
            for f_id in files:
                try: bot.send_document(uid, f_id)
                except: pass
        return

    if is_admin(uid):
        bot.send_message(uid, "👑 أهلاً بك في لوحة الإدارة:", reply_markup=get_panel(uid))
    else:
        bot.send_message(uid, "👋 أهلاً بك! تابع القناة للحصول على أحدث الملفات.")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def handle_admin(message):
    uid, text = message.from_user.id, message.text
    settings = load_json("settings.json")

    if text == "الإحصائيات 📊":
        users = get_list("users.txt")
        files = get_list("bot_files.txt")
        activity = load_json("activity.json")
        total_likes = sum(len(v.get("u_interact", [])) for v in activity.values())
        try: ch_count = bot.get_chat_member_count(CHANNEL_ID)
        except: ch_count = "غير متاح"

        stats = (f"📊 **إحصائيات البوت:**\n\n"
                 f"👥 مستخدمين الخاص: `{len(users)}`\n"
                 f"📢 أعضاء القناة: `{ch_count}`\n"
                 f"📂 ملفات مرفوعة: `{len(files)}`\n"
                 f"❤️ إجمالي التفاعلات: `{total_likes}`")
        bot.send_message(uid, stats, parse_mode="Markdown")

    elif text == "إضافة ملفات 📤":
        msg = bot.send_message(uid, "📤 أرسل ملفاتك الآن.. ثم اضغط إنهاء الإضافة ✅", 
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء الإضافة ✅"))
        bot.register_next_step_handler(msg, process_upload)

    elif text == "إذاعة للمستخدمين 👥":
        msg = bot.send_message(uid, "🗣️ أرسل الإذاعة (نص/صورة/ملف):", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إلغاء ❌"))
        bot.register_next_step_handler(msg, run_broadcast)

    elif text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **تحديث جديد!**\n📂 عدد الملفات: `{f_count}`\n\nتفاعل ❤️ ثم استلم.", parse_mode="Markdown")
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=channel_markup(msg.message_id))
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    elif text == "تفعيل الإشعارات ✅":
        settings["notifications"] = True
        save_json("settings.json", settings)
        bot.send_message(uid, "🔔 تم تفعيل إشعارات الدخول.", reply_markup=get_panel(uid))

    elif text == "إيقاف الإشعارات ❌":
        settings["notifications"] = False
        save_json("settings.json", settings)
        bot.send_message(uid, "🔕 تم إيقاف إشعارات الدخول.", reply_markup=get_panel(uid))

    elif text == "تنظيف البيانات 🧹":
        removed = clean_old_activity()
        bot.send_message(uid, f"🧹 تم حذف سجل {removed} منشور قديم.")

    elif text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم مسح جميع الملفات من السجل.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🛑 تم الخروج من القائمة الرئيسية.", reply_markup=get_panel(uid))

# ==========================================
# 5. دالات العمليات الخلفية
# ==========================================
def process_upload(message):
    uid = message.from_user.id
    if message.text == "إنهاء الإضافة ✅":
        bot.send_message(uid, "✅ تم الحفظ.", reply_markup=get_panel(uid))
        return

    file_id = None
    if message.document: file_id = message.document.file_id
    elif message.photo: file_id = message.photo[-1].file_id
    elif message.video: file_id = message.video.file_id
    elif message.audio: file_id = message.audio.file_id

    if file_id:
        existing = get_list("bot_files.txt")
        if file_id not in existing:
            with open("bot_files.txt", "a") as f: f.write(file_id + "\n")
            bot.send_message(uid, "📥 تم الحفظ.. أرسل المزيد أو اضغط إنهاء.")
        else:
            bot.send_message(uid, "⚠️ هذا الملف مضاف مسبقاً!")
    
    bot.register_next_step_handler(message, process_upload)

def run_broadcast(message):
    if message.text == "إلغاء ❌":
        bot.send_message(message.chat.id, "🛑 تم إلغاء الإذاعة.", reply_markup=get_panel(message.from_user.id))
        return
    users = get_list("users.txt")
    bot.send_message(message.chat.id, f"🚀 جاري الإرسال لـ {len(users)} مستخدم...")
    for u in users:
        try: bot.copy_message(u, message.chat.id, message.message_id)
        except: pass
    bot.send_message(message.chat.id, "✅ اكتملت الإذاعة.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = str(call.from_user.id)
    if call.data.startswith("hit_"):
        mid = call.data.split("_")[1]
        act = load_json("activity.json")
        if mid not in act: act[mid] = {"u_interact": []}
        if uid not in act[mid]["u_interact"]:
            act[mid]["u_interact"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ تم التفاعل!")
            try: bot.edit_message_reply_markup(call.message.chat.id, int(mid), reply_markup=channel_markup(mid, len(act[mid]["u_interact"])))
            except: pass
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً!", show_alert=True)

if __name__ == "__main__":
    clean_old_activity()
    print(f"🔥 {BOT_USERNAME} يعمل بكفاءة...")
    bot.infinity_polling()

