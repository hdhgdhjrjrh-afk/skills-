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
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# إنشاء الملفات الضرورية إذا لم تكن موجودة
FILES = ["users.txt", "bot_files.txt", "activity.json", "subs.json", "admins.json", "settings.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f == "settings.json": json.dump({"notifications": True}, file)
            elif f.endswith(".json"): json.dump({} if "activity" in f else [], file)
            else: file.write("")

# ==========================================
# 2. دالات إدارة البيانات
# ==========================================
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {} if "activity" in filename else []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def is_admin(user_id):
    admins = load_json("admins.json")
    return user_id == OWNER_ID or user_id in admins

def clean_old_activity():
    """حذف التفاعلات القديمة والاحتفاظ بآخر 50 منشوراً فقط"""
    act = load_json("activity.json")
    if not act: return 0
    
    keys = list(act.keys())
    before_count = len(keys)
    
    if before_count > 50:
        # الاحتفاظ بآخر 50 منشور (الأحدث)
        new_act = {k: act[k] for k in keys[-50:]}
        save_json("activity.json", new_act)
        return before_count - 50
    return 0

# ==========================================
# 3. لوحات التحكم
# ==========================================
def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = load_json("settings.json")
    
    # تحديد شكل زر الإشعارات بناءً على الحالة الحالية
    notif_btn = "إيقاف الإشعارات ❌" if settings.get("notifications", True) else "تفعيل الإشعارات ✅"
    
    btns = [
        "نشر تلقائي 📣", "إضافة ملفات 📤", 
        "إذاعة للمستخدمين 👥", "إذاعة للقناة 📢", 
        "الإحصائيات 📊", notif_btn,
        "تنظيف البيانات 🧹" # الزر الجديد
    ]
    
    if user_id == OWNER_ID:
        btns.append("إضافة أدمن ➕")
    
    btns.extend(["تصفير الملفات 🗑️", "إنهاء ✅"])
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
# 4. معالجة الرسائل والأوامر
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    settings = load_json("settings.json")
    
    # تسجيل المستخدم وإرسال إشعار الدخول
    users_list = get_list("users.txt")
    if str(uid) not in users_list:
        with open("users.txt", "a") as f:
            f.write(str(uid) + "\n")
        
        # إرسال إشعار للمالك إذا كانت الميزة مفعلة
        if settings.get("notifications", True):
            mention = f"[{message.from_user.first_name}](tg://user?id={uid})"
            msg = f"👤 **دخول مستخدم جديد!**\n\n" \
                  f"👤 الاسم: {mention}\n" \
                  f"🆔 الآيدي: `{uid}`\n" \
                  f"🔗 اليوزر: @{message.from_user.username if message.from_user.username else 'لا يوجد'}"
            try: bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
            except: pass

    # معالجة استلام الملفات
    if message.text and "get_" in message.text:
        files = get_list("bot_files.txt")
        if not files:
            bot.send_message(uid, "❌ لا توجد ملفات حالياً.")
        else:
            bot.send_message(uid, "✅ تفضل، هذه جميع الملفات المتاحة:")
            for f_id in files:
                try: bot.send_document(uid, f_id)
                except: pass
        return

    if is_admin(uid):
        bot.send_message(uid, "👑 أهلاً بك في لوحة التحكم:", reply_markup=get_panel(uid))
    else:
        bot.send_message(uid, "👋 أهلاً بك! تابع القناة للحصول على الملفات.")

@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def handle_admin(message):
    uid, text = message.from_user.id, message.text
    settings = load_json("settings.json")

    if text == "الإحصائيات 📊":
        users = get_list("users.txt")
        files = get_list("bot_files.txt")
        bot.send_message(uid, f"📊 **إحصائيات البوت:**\n\n👥 المستخدمين: `{len(users)}`\n📂 الملفات: `{len(files)}`", parse_mode="Markdown")

    elif text == "تنظيف البيانات 🧹":
        removed = clean_old_activity()
        bot.send_message(uid, f"✅ تم تنظيف السجلات.\nتم حذف بيانات `{removed}` منشور قديم.\nالملف الآن يحتوي على أحدث 50 منشور فقط.")

    elif text == "تفعيل الإشعارات ✅":
        settings["notifications"] = True
        save_json("settings.json", settings)
        bot.send_message(uid, "🔔 تم تفعيل إشعارات دخول المستخدمين.", reply_markup=get_panel(uid))

    elif text == "إيقاف الإشعارات ❌":
        settings["notifications"] = False
        save_json("settings.json", settings)
        bot.send_message(uid, "🔕 تم إيقاف إشعارات الدخول.", reply_markup=get_panel(uid))

    elif text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **تحديث جديد للملفات!**\n📂 العدد: `{f_count}`\n\n⚠️ تفاعل ❤️ ثم اضغط استلم.", parse_mode="Markdown")
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=channel_markup(msg.message_id))
        bot.send_message(uid, "✅ تم النشر في القناة.")

    elif text == "إضافة ملفات 📤":
        bot.send_message(uid, "📤 أرسل الملفات الآن (صور، فيديو، ملفات)، ثم اضغط إنهاء ✅", 
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_upload)

    elif text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم حذف سجل الملفات بنجاح.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🛑 تم إغلاق القائمة.", reply_markup=get_panel(uid))

# ==========================================
# 5. وظائف إضافية (الرفع والتبادل)
# ==========================================
def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.chat.id, "✅ تم حفظ الملفات.", reply_markup=get_panel(message.from_user.id))
        return
    
    file_id = None
    if message.document: file_id = message.document.file_id
    elif message.photo: file_id = message.photo[-1].file_id
    elif message.video: file_id = message.video.file_id
    
    if file_id:
        with open("bot_files.txt", "a") as f: f.write(file_id + "\n")
        bot.send_message(message.chat.id, "📥 تم الاستلام.. أرسل المزيد أو اضغط إنهاء.")
    
    bot.register_next_step_handler(message, process_upload)

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
            bot.answer_callback_query(call.id, "❤️ تم تسجيل تفاعلك!")
            try:
                bot.edit_message_reply_markup(call.message.chat.id, int(mid), 
                                              reply_markup=channel_markup(mid, len(act[mid]["u_interact"])))
            except: pass
        else:
            bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت بالفعل!", show_alert=True)

if __name__ == "__main__":
    clean_old_activity() # تنظيف تلقائي عند كل تشغيل
    print("🚀 البوت يعمل الآن...")
    bot.infinity_polling()

