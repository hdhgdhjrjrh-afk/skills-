import telebot
from telebot import types
import os, json, time

# --- [ الإعدادات الأساسية ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- [ نظام إدارة قاعدة البيانات الشامل ] ---
def init_db():
    database = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "{}", 
        "stats.json": json.dumps({
            "downloads": 0, 
            "likes": 0, 
            "likes_log": [], 
            "downloads_log": []
        }),
        "settings.json": json.dumps({
            "notifications": True, 
            "channel_id": "@Uchiha75", 
            "sub_link": "https://t.me/Uchiha75"
        })
    }
    for f, c in database.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file:
                file.write(c)

init_db()

def get_db(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_db("admins.json")
    return admins.get(str(uid), {}).get(perm, False)

# --- [ لوحات التحكم المتقدمة ] ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    n_status = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"):
        kb.row("نشر في القناة 📣", "إضافة ملفات 📤")
    
    if has_perm(uid, "can_broadcast"):
        kb.row("قسم الإذاعة 📢", "الإحصائيات 📊")
    
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
        kb.row(n_status, "تنظيف البيانات 🧹")
    
    kb.row("تصفير الملفات 🗑️")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add("إذاعة للمستخدمين 👥", "إذاعة للقنوات 📢", "إذاعة توجيه (Forward) 🔄", "رجوع للخلف 🔙")
    return kb

# --- [ معالجة أمر Start ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
    # الترحيب الخاص بك يا زعيم
    if int(uid) == OWNER_ID:
        welcome_text = "مرحبا ايها مطور 😈SELVA 😈"
    else:
        welcome_text = "مرحبا بك في بوت توزيع الكونفيجات ⚡"
    
    # نظام تسجيل المستخدمين الجديد
    if not os.path.exists("users.txt"): open("users.txt", "w").close()
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    
    if str(uid) not in users:
        with open("users.txt", "a") as f:
            f.write(f"{uid}\n")
        
        # إشعار الدخول للمطور
        conf = get_db("settings.json")
        if conf.get("notifications"):
            try:
                bot.send_message(OWNER_ID, f"🔔 **دخل مستخدم جديد!**\n👤 الاسم: {message.from_user.first_name}\n🆔 الآيدي: `{uid}`", parse_mode="Markdown")
            except: pass
            
    bot.send_message(uid, welcome_text, reply_markup=main_kb(uid))

# --- [ راوتر العمليات الرئيسي ] ---
@bot.message_handler(func=lambda m: True)
def router(message):
    uid, text = message.from_user.id, message.text
    conf = get_db("settings.json")

    # --- 1. قسم الإذاعة المتطور ---
    if text == "قسم الإذاعة 📢" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "اختر نوع الإذاعة المطلوبة:", reply_markup=broadcast_kb())

    elif text == "إذاعة للمستخدمين 👥" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "أرسل الرسالة التي تريد إرسالها للجميع (نسخة طبق الأصل):")
        bot.register_next_step_handler(m, lambda msg: start_broadcast(msg, "copy"))

    elif text == "إذاعة للقنوات 📢" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "أرسل الرسالة التي تريد نشرها في قناتك المربوطة:")
        bot.register_next_step_handler(m, lambda msg: start_broadcast(msg, "channel"))

    elif text == "إذاعة توجيه (Forward) 🔄" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "أرسل الرسالة التي تريد عمل (Forward) لها للجميع:")
        bot.register_next_step_handler(m, lambda msg: start_broadcast(msg, "forward"))

    elif text == "رجوع للخلف 🔙":
        bot.send_message(uid, "العودة للقائمة الرئيسية...", reply_markup=main_kb(uid))

    # --- 2. قسم الإدارة والنشر ---
    elif text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.send_message(uid, "❌ قاعدة البيانات فارغة!")
        
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        
        caption = (
            "⚡ **تم تجديد الكونفيجات!**\n\n"
            f"📁 عدد الملفات: {len(files)}\n"
            "🚀 سرعة عالية | ⏳ محدد المدة\n"
            "━━━━━━━━━━━━━━\n"
            "📌 **طريقة الاستلام:**\n\n"
            "1️⃣ ادعمنا بضغطة ❤️\n"
            "2️⃣ اضغط 📩 لاستلام الملفات\n"
            "━━━━━━━━━━━━━━\n"
            "⚠️ **سارع قبل انتهاء الصلاحية!**"
        )
        bot.send_message(conf["channel_id"], caption, reply_markup=mk, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر في القناة.")

    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_post"):
        m = bot.send_message(uid, "📤 أرسل الملف/الكونفيج الآن ليتم تخزينه:")
        bot.register_next_step_handler(m, save_file_logic)

    elif text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "➕ أرسل آيدي (ID) الشخص المراد ترقيته:")
        bot.register_next_step_handler(m, add_admin_logic)

    elif text == "إضافة اشتراك 🔗" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🔗 أرسل رابط قناتك الجديد (مثل t.me/Uchiha75):")
        bot.register_next_step_handler(m, save_sub_logic)

    elif text == "الإحصائيات 📊":
        st = get_db("stats.json")
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        msg = (f"📊 **إحصائيات البوت:**\n\n"
               f"👥 مستخدمين: `{u_count}`\n"
               f"📩 استلام فريد: `{len(st.get('downloads_log', []))}`\n"
               f"❤️ تفاعل فريد: `{len(st.get('likes_log', []))}`")
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif text == "تنظيف البيانات 🧹" and int(uid) == OWNER_ID:
        st = {"downloads": 0, "likes": 0, "likes_log": [], "downloads_log": []}
        save_db("stats.json", st)
        bot.send_message(uid, "🧹 تم تصفير كافة الإحصائيات بنجاح.")

    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w") as f: f.truncate(0)
        bot.send_message(uid, "🗑️ تم مسح قائمة الملفات بالكامل.")

    elif text in ["تفعيل الإشعارات ✅", "إيقاف الإشعارات ❌"]:
        conf["notifications"] = not conf["notifications"]
        save_db("settings.json", conf)
        bot.send_message(uid, "⚙️ تم تحديث وضع الإشعارات.", reply_markup=main_kb(uid))

# --- [ وظائف التنفيذ المساعدة ] ---

def start_broadcast(message, b_type):
    conf = get_db("settings.json")
    if b_type == "channel":
        try:
            bot.copy_message(conf["channel_id"], message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "✅ تم النشر في القناة.")
        except: bot.send_message(message.chat.id, "❌ فشل النشر في القناة، تأكد من أن البوت مشرف.")
        return

    with open("users.txt", "r") as f: users = f.read().splitlines()
    bot.send_message(message.chat.id, f"🚀 جاري الإذاعة لـ {len(users)} مستخدم...")
    count = 0
    for u in users:
        try:
            if b_type == "copy": bot.copy_message(u, message.chat.id, message.message_id)
            elif b_type == "forward": bot.forward_message(u, message.chat.id, message.message_id)
            count += 1
            time.sleep(0.05)
        except: continue
    bot.send_message(message.chat.id, f"✅ اكتملت الإذاعة لـ {count} مستخدم.")

def add_admin_logic(message):
    if message.text.isdigit():
        admins = get_db("admins.json")
        admins[str(message.text)] = {"can_post": True, "can_broadcast": True, "can_reset": False}
        save_db("admins.json", admins)
        bot.send_message(message.chat.id, f"✅ تم إضافة `{message.text}` كأدمن بمساعدة SELVA.")
    else: bot.send_message(message.chat.id, "❌ الآيدي يجب أن يكون أرقاماً.")

def save_sub_logic(message):
    if "t.me/" in message.text:
        conf = get_db("settings.json")
        conf["sub_link"] = message.text
        conf["channel_id"] = "@" + message.text.split("t.me/")[1]
        save_db("settings.json", conf)
        bot.send_message(message.chat.id, f"✅ تم تحديث القناة المربوطة.")
    else: bot.send_message(message.chat.id, "❌ رابط غير صحيح.")

def save_file_logic(message):
    fid = message.document.file_id if message.document else (message.video.file_id if message.video else (message.photo[-1].file_id if message.photo else None))
    if fid:
        with open("bot_files.txt", "a") as f: f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم حفظ الملف بنجاح.")

# --- [ كول باك التفاعلات ومنع التكرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    st = get_db("stats.json")
    uid = call.from_user.id
    if call.data == "hit_like":
        if uid not in st.get("likes_log", []):
            st["likes"] += 1; st.setdefault("likes_log", []).append(uid); save_db("stats.json", st)
            bot.answer_callback_query(call.id, "❤️ شكراً SELVA!")
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً", show_alert=True)
    elif call.data == "get_files":
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.answer_callback_query(call.id, "❌ لا توجد ملفات.")
        if uid not in st.get("downloads_log", []):
            st["downloads"] += 1; st.setdefault("downloads_log", []).append(uid); save_db("stats.json", st)
        bot.answer_callback_query(call.id, "🚀 جاري الإرسال...")
        for fid in files:
            try: bot.send_document(uid, fid)
            except: pass

if __name__ == "__main__":
    print("🔥 SELVA SUPER BOT IS ONLINE...")
    bot.infinity_polling()
