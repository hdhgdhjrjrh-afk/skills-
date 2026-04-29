import telebot
from telebot import types
import os, json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام قاعدة البيانات المحمي (Bot Running Storage) ---
def init_db():
    database = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "{}", 
        "stats.json": json.dumps({"downloads": 0, "likes": 0}),
        "settings.json": json.dumps({
            "notifications": True, 
            "channel_id": "@Uchiha75", 
            "sub_link": "https://t.me/Uchiha75",
            "running_status": "Active ✅"
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

# --- فحص الصلاحيات ---
def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    return get_db("admins.json").get(str(uid), {}).get(perm, False)

# --- كيبوردات التشغيل (Running Keyboards) ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    n_text = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"): kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"): kb.row("إرسال إذاعة 📣", "الإحصائيات 📊")
    if int(uid) == OWNER_ID: kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
    kb.row(n_text)
    if has_perm(uid, "can_reset"): kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
    return kb

# --- معالجة الأوامر والتشغيل (Core Engine) ---
@bot.message_handler(commands=['start'])
def start_bot(message):
    uid = message.from_user.id
    # تسجيل المستخدم لضمان عمل الإحصائيات
    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
    
    bot.send_message(uid, "🚀 **Bot Running System:** مفعل وجاهز.\n💎 أهلاً بك في لوحة التحكم:", reply_markup=main_kb(uid), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def bot_running_router(message):
    uid, text = message.from_user.id, message.text

    # 1. نظام الإذاعة الثلاثية
    if text == "إرسال إذاعة 📣" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "🎯 حدد نوع الإذاعة المطلوبة:", reply_markup=broadcast_kb())
    
    elif text == "إذاعة قناة 📢" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "📢 أرسل الرسالة لنشرها في القناة:")
        bot.register_next_step_handler(m, lambda msg: exec_bc(msg, "channel"))
        
    elif text == "إذاعة مستخدمين 👥" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "👥 أرسل الرسالة لإذاعتها للمستخدمين:")
        bot.register_next_step_handler(m, lambda msg: exec_bc(msg, "users"))
        
    elif text == "إذاعة الجميع 🌐" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "🌐 أرسل رسالة للجميع (قناة + مستخدمين):")
        bot.register_next_step_handler(m, lambda msg: exec_bc(msg, "all"))

    # 2. نظام إضافة الملفات (المُصلح)
    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_add_files"):
        m = bot.send_message(uid, "📤 أرسل (الملف، صورة، أو فيديو) الآن:")
        bot.register_next_step_handler(m, save_file_logic)

    # 3. نظام تنظيف البيانات (المُصلح)
    elif text == "تنظيف البيانات 🧹" and has_perm(uid, "can_reset"):
        with open("users.txt", "w") as f: f.truncate(0)
        save_db("stats.json", {"downloads": 0, "likes": 0})
        bot.send_message(uid, "✅ تم تنظيف كافة البيانات وتصفير الإحصائيات.", reply_markup=main_kb(uid))

    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w") as f: f.truncate(0)
        bot.send_message(uid, "✅ تم مسح جميع الملفات المرفوعة.", reply_markup=main_kb(uid))

    # 4. الإحصائيات الشاملة
    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        st = get_db("stats.json")
        msg = (f"📊 **إحصائيات التشغيل:**\n\n"
               f"👥 المشتركين: `{u_count}`\n"
               f"📩 استلام الملفات: `{st['downloads']}`\n"
               f"❤️ التفاعلات: `{st['likes']}`")
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif text == "رجوع 🔙":
        bot.send_message(uid, "🔙 العودة للرئيسية:", reply_markup=main_kb(uid))

# --- وظائف التشغيل المتقدمة (Execution Logic) ---

def save_file_logic(message):
    # مصلح: يدعم جميع أنواع المرفقات
    fid = message.document.file_id if message.document else (
          message.video.file_id if message.video else (
          message.photo[-1].file_id if message.photo else None))
    
    if fid:
        with open("bot_files.txt", "a") as f: f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم حفظ الملف بنجاح في قاعدة بيانات بوت رانين.", reply_markup=main_kb(message.from_user.id))
    else:
        bot.send_message(message.chat.id, "❌ خطأ: لم يتم التعرف على الملف. تأكد من إرساله كمرفق.", reply_markup=main_kb(message.from_user.id))

def exec_bc(message, mode):
    conf = get_db("settings.json")
    with open("users.txt", "r") as f: users = f.read().splitlines()
    sent = 0
    if mode in ["channel", "all"]:
        try: bot.copy_message(conf["channel_id"], message.chat.id, message.message_id); sent += 1
        except: pass
    if mode in ["users", "all"]:
        for u in users:
            try: bot.copy_message(u, message.chat.id, message.message_id); sent += 1
            except: pass
    bot.send_message(message.chat.id, f"✅ اكتملت عملية الإذاعة بنجاح.\n🎯 الإجمالي: {sent}", reply_markup=main_kb(message.from_user.id))

# --- Callbacks (تحديث الإحصائيات) ---
@bot.callback_query_handler(func=lambda call: True)
def calls_running(call):
    uid, data = call.from_user.id, call.data
    if data == "get_files":
        st = get_db("stats.json")
        st["downloads"] += 1
        save_db("stats.json", st)
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        for fid in files:
            try: bot.send_document(uid, fid)
            except: pass
    elif data == "hit_like":
        st = get_db("stats.json")
        st["likes"] += 1
        save_db("stats.json", st)
        bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")

if __name__ == "__main__":
    print("🤖 Bot Running System is Active...")
    bot.infinity_polling()

