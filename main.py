import telebot
from telebot import types
import os, json, time

# --- [ إعدادات الهوية والاتصال ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- [ نظام إدارة قواعد البيانات - فحص المسارات ] ---
def initialize_system():
    """تجهيز كافة الملفات لضمان عدم وجود مسار مفقود"""
    files_schema = {
        "users.txt": "",
        "bot_files.json": "[]",
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
    for file_name, default_content in files_schema.items():
        if not os.path.exists(file_name):
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(default_content)

initialize_system()

def load_db(file):
    with open(file, "r", encoding="utf-8") as f:
        if file.endswith(".json"): return json.load(f)
        return f.read().splitlines()

def update_db(file, data):
    with open(file, "w", encoding="utf-8") as f:
        if file.endswith(".json"):
            json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            f.write(str(data))

def check_admin(uid):
    if int(uid) == OWNER_ID: return True
    admins = load_db("admins.json")
    return str(uid) in admins

# --- [ صناعة لوحات التحكم - الأزرار ] ---

def get_main_keyboard(uid):
    """لوحة التحكم الرئيسية (تتغير حسب الصلاحية)"""
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if check_admin(uid):
        kb.row("نشر في القناة 📣", "إضافة ملفات 📤")
        kb.row("قسم الإذاعة 📢", "الإحصائيات 📊")
        if int(uid) == OWNER_ID:
            kb.row("صلاحيات أدمن ⚙️", "إضافة اشتراك 🔗")
            kb.row("تصفير ملفات 🗑️", "تنظيف بيانات 🧹")
    else:
        kb.row("مرحباً بك في البوت ⚡")
    return kb

def get_broadcast_markup():
    """أزرار اختيار نوع الإذاعة"""
    mk = types.InlineKeyboardMarkup(row_width=1)
    mk.add(
        types.InlineKeyboardButton("👤 إذاعة للمستخدمين (خاص)", callback_data="bc_users"),
        types.InlineKeyboardButton("📢 إذاعة للقناة (عام)", callback_data="bc_channel"),
        types.InlineKeyboardButton("🌍 إذاعة شاملة (الجميع)", callback_data="bc_all"),
        types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_action")
    )
    return mk

def get_channel_buttons():
    """أزرار القناة التفاعلية"""
    st = load_db("stats.json")
    try: b_name = bot.get_me().username
    except: b_name = "Bot"
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton(f"❤️ تفاعل | {st.get('likes', 0)}", callback_data="hit_like"),
        types.InlineKeyboardButton(f"📩 استلم | {st.get('downloads', 0)}", url=f"https://t.me/{b_name}?start=get_files")
    )
    return mk

# --- [ دوال المعالجة والمنطق ] ---

@bot.message_handler(commands=['start'])
def welcome_handler(message):
    uid = message.from_user.id
    users = load_db("users.txt")
    conf = load_db("settings.json")

    # إشعار المطور بدخول مستخدم جديد
    if str(uid) not in users:
        users.append(str(uid))
        update_db("users.txt", "\n".join(users))
        if conf.get("notifications"):
            try:
                dev_text = (f"😈 **تنبيه مطور: دخول جديد!**\n\n"
                            f"👤 الاسم: {message.from_user.first_name}\n"
                            f"🆔 الآيدي: `{uid}`\n"
                            f"🔗 الحساب: [رابط المستخدم](tg://user?id={uid})")
                bot.send_message(OWNER_ID, dev_text, parse_mode="Markdown")
            except: pass

    # فحص رابط استلام الملفات
    if "get_files" in message.text:
        st = load_db("stats.json")
        if uid in st.get("likes_log", []):
            files = load_db("bot_files.json")
            if not files: return bot.send_message(uid, "❌ قاعدة البيانات فارغة حالياً.")
            bot.send_message(uid, "🚀 تم التحقق! إليك الملفات المطلوبة:")
            for f in files:
                try: bot.send_document(uid, f['file_id'], caption=f.get('caption', ""))
                except: continue
            
            if uid not in st.get("downloads_log", []):
                st["downloads"] += 1
                st["downloads_log"].append(uid)
                update_db("stats.json", st)
        else:
            bot.send_message(uid, "⚠️ خطأ! يجب عليك التفاعل بـ (❤️) في القناة أولاً لاستلام الملفات.")
        return

    bot.send_message(uid, "مرحباً بك في لوحة تحكم ⚡ **Uchiha Dz** ⚡", reply_markup=get_main_keyboard(uid), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def central_router(message):
    uid, text = message.from_user.id, message.text
    if not check_admin(uid): return

    # 1. نظام الإحصائيات
    if text == "الإحصائيات 📊":
        users = load_db("users.txt")
        st = load_db("stats.json")
        files = load_db("bot_files.json")
        report = (f"📊 **تقرير الإحصائيات الحالية:**\n\n"
                  f"👥 المشتركين: `{len(users)}`\n"
                  f"📁 الملفات: `{len(files)}`\n"
                  f"❤️ التفاعلات: `{st['likes']}`\n"
                  f"📥 المستلمين: `{st['downloads']}`")
        bot.send_message(uid, report, parse_mode="Markdown")

    # 2. نظام الإذاعة
    elif text == "قسم الإذاعة 📢" and int(uid) == OWNER_ID:
        bot.send_message(uid, "⚙️ اختر مسار الإذاعة المطلوب:", reply_markup=get_broadcast_markup())

    # 3. تصفير البيانات والملفات
    elif text == "تصفير ملفات 🗑️" and int(uid) == OWNER_ID:
        update_db("bot_files.json", [])
        bot.send_message(uid, "🗑️ تم مسح كافة الملفات من البوت بنجاح.")

    elif text == "تنظيف بيانات 🧹" and int(uid) == OWNER_ID:
        empty_stats = {"downloads": 0, "likes": 0, "likes_log": [], "downloads_log": []}
        update_db("stats.json", empty_stats)
        bot.send_message(uid, "✅ تم تصفير سجلات التفاعل والعدادات.")

    # 4. النشر في القناة
    elif text == "نشر في القناة 📣":
        conf = load_db("settings.json")
        files = load_db("bot_files.json")
        if not files: return bot.send_message(uid, "❌ لا توجد ملفات للنشر.")
        cap = f"⚡ **تحديث جديد!**\n📁 عدد الملفات: {len(files)}\n🚀 السرعة: فائقة\n━━━━━━━━━━━━━━"
        bot.send_message(conf["channel_id"], cap, reply_markup=get_channel_buttons(), parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر في القناة.")

# --- [ معالجة العمليات المتقدمة (Callback & Broadcast) ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid, data = call.from_user.id, call.data
    
    if data.startswith("bc_"):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        target = data.split("_")[1]
        msg = bot.send_message(call.message.chat.id, "📩 أرسل الرسالة (نص/ميديا/ملف) للإذاعة:")
        bot.register_next_step_handler(msg, perform_broadcast, target)

    elif data == "hit_like":
        st = load_db("stats.json")
        if uid not in st.get("likes_log", []):
            st["likes"] += 1
            st["likes_log"].append(uid)
            update_db("stats.json", st)
            bot.answer_callback_query(call.id, "❤️ تم تسجيل تفاعلك!")
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_channel_buttons())
            except: pass
        else:
            bot.answer_callback_query(call.id, "⚠️ أنت متفاعل بالفعل!", show_alert=True)

    elif data == "cancel_action":
        bot.delete_message(call.message.chat.id, call.message.message_id)

def perform_broadcast(message, target):
    users = load_db("users.txt")
    conf = load_db("settings.json")
    success_count = 0

    if target in ["users", "all"]:
        bot.send_message(OWNER_ID, "⏳ جاري الإرسال للمستخدمين...")
        for user_id in users:
            try:
                bot.copy_message(user_id, message.chat.id, message.message_id)
                success_count += 1
                time.sleep(0.05)
            except: continue

    if target in ["channel", "all"]:
        try:
            bot.copy_message(conf["channel_id"], message.chat.id, message.message_id)
            bot.send_message(OWNER_ID, "✅ تم الإرسال للقناة.")
        except Exception as e:
            bot.send_message(OWNER_ID, f"❌ فشل إرسال القناة: {e}")

    bot.send_message(OWNER_ID, f"🏁 انتهت الإذاعة!\nتم الوصول لـ {success_count} مستخدم بنجاح.")

# --- [ نقطة الانطلاق ] ---
if __name__ == "__main__":
    print("🔥 SELVA SYSTEM IS DEPLOYED AND ACTIVE...")
    while True:
        try:
            bot.infinity_polling(timeout=15, long_polling_timeout=5)
        except Exception as e:
            print(f"Network error: {e}")
            time.sleep(5)
