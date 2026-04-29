import telebot
from telebot import types
import os, json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام قاعدة البيانات ---
def init_db():
    database = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "{}", 
        "stats.json": json.dumps({"downloads": 0, "likes": 0}),
        "settings.json": json.dumps({
            "notifications": True, 
            "channel_id": "@Uchiha75", 
            "sub_link": "https://t.me/Uchiha75"
        })
    }
    for f, c in database.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file: file.write(c)

init_db()

def get_db(file):
    with open(file, "r", encoding="utf-8") as f: return json.load(f)

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_db("admins.json")
    return admins.get(str(uid), {}).get(perm, False)

# --- الكيبوردات ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    n_text = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"): kb.row("نشر في القناة 📣")
    if has_perm(uid, "can_add_files"): kb.insert("إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"): kb.row("إرسال إذاعة 📣")
    kb.insert("الإحصائيات 📊")
    
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
    
    kb.row(n_text)
    if has_perm(uid, "can_reset"): kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
    return kb

# --- الأوامر الرئيسية ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    conf = get_db("settings.json")
    
    # رسالة المطور الخاصة
    welcome_msg = "مرحبا ايها مطور 😈" if int(uid) == OWNER_ID else "💎 أهلاً بك في لوحة التحكم:"

    # تسجيل المستخدم وإشعار المطور
    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        if conf.get("notifications"):
            try: bot.send_message(OWNER_ID, f"🔔 مستخدم جديد دخل للبوت:\n👤 {message.from_user.first_name}\n🆔 `{uid}`", parse_mode="Markdown")
            except: pass
    
    bot.send_message(uid, welcome_msg, reply_markup=main_kb(uid))

# --- راوتر الأزرار ---
@bot.message_handler(func=lambda m: True)
def bot_router(message):
    uid, text = message.from_user.id, message.text
    conf = get_db("settings.json")

    # 1. إضافة اشتراك (مُفعل الآن)
    if text == "إضافة اشتراك 🔗" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🔗 أرسل رابط القناة الجديد (t.me/...):")
        bot.register_next_step_handler(m, save_sub_logic)

    # 2. الإحصائيات (مُفصلة الآن)
    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        with open("bot_files.txt", "r") as f: f_count = len(f.read().splitlines())
        st = get_db("stats.json")
        msg = (f"📊 **تقارير بوت رانين:**\n\n"
               f"👥 المشتركين: `{u_count}`\n"
               f"📁 الملفات المرفوعة: `{f_count}`\n"
               f"📩 مرات الاستلام: `{st['downloads']}`\n"
               f"❤️ إجمالي التفاعل: `{st['likes']}`\n"
               f"🔔 الإشعارات: `{'مفعلة' if conf['notifications'] else 'معطلة'}`")
        bot.send_message(uid, msg, parse_mode="Markdown")

    # 3. إضافة أدمن
    elif text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, process_admin_id)

    # 4. نشر في القناة
    elif text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.send_message(uid, "❌ القائمة فارغة!")
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        caption = f"⚡ **تم تجديد الملفات!**\n📁 عددها: `{len(files)}`"
        bot.send_message(conf["channel_id"], caption, reply_markup=mk, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر.")

    # 5. تنبيهات الإشعارات (Toggle)
    elif text in ["إيقاف الإشعارات ❌", "تفعيل الإشعارات ✅"]:
        conf["notifications"] = not conf["notifications"]
        save_db("settings.json", conf)
        bot.send_message(uid, "⚙️ تم تحديث إعدادات التنبيهات.", reply_markup=main_kb(uid))

    # 6. الإذاعة والرجوع
    elif text == "إرسال إذاعة 📣" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "🎯 اختر نوع الإذاعة:", reply_markup=broadcast_kb())
    
    elif text == "رجوع 🔙":
        bot.send_message(uid, "🔙 الرئيسية:", reply_markup=main_kb(uid))

# --- وظائف التنفيذ المفقودة ---

def save_sub_logic(message):
    if "t.me/" in message.text:
        conf = get_db("settings.json")
        conf["sub_link"] = message.text
        # استخراج المعرف تلقائياً
        conf["channel_id"] = "@" + message.text.split("t.me/")[1].split("/")[0]
        save_db("settings.json", conf)
        bot.send_message(message.chat.id, f"✅ تم تحديث الاشتراك لـ: {conf['channel_id']}")
    else:
        bot.send_message(message.chat.id, "❌ رابط غير صحيح.")

def process_admin_id(message):
    target = message.text
    if not target.isdigit(): return bot.send_message(message.chat.id, "❌ آيدي خاطئ.")
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("💾 تفعيل بكامل الصلاحيات", callback_data=f"save_adm_{target}"))
    bot.send_message(message.chat.id, f"⚙️ تأكيد إضافة الأدمن `{target}`؟", reply_markup=mk)

# (بقية الدوال: save_file_logic, exec_bc, callbacks تبقى كما هي لضمان الاستقرار)

if __name__ == "__main__":
    print("🤖 Bot is fully running now...")
    bot.infinity_polling()

