import telebot
from telebot import types
import os, json, time

# --- [ الإعدادات الأساسية ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- [ نظام إدارة قاعدة البيانات ] ---
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
    except:
        return {}

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_db("admins.json")
    return admins.get(str(uid), {}).get(perm, False)

# --- [ لوحات التحكم - الكيبورد ] ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    n_text = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"):
        kb.row("نشر في القناة 📣", "إضافة ملفات 📤")
    
    if has_perm(uid, "can_broadcast"):
        kb.row("إرسال إذاعة 📣", "الإحصائيات 📊")
    
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
        kb.row(n_text, "تنظيف البيانات 🧹")
    
    kb.row("تصفير الملفات 🗑️")
    return kb

# --- [ معالجة أمر Start ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
    # الترحيب الخاص بالمطور SELVA
    if int(uid) == OWNER_ID:
        welcome_text = "مرحبا ايها مطور 😈SELVA 😈"
    else:
        welcome_text = "مرحبا بك في بوت توزيع الكونفيجات ⚡"
    
    # تسجيل المستخدم الجديد
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()
        
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    
    if str(uid) not in users:
        with open("users.txt", "a") as f:
            f.write(f"{uid}\n")
        
        # إشعار دخول مستخدم جديد
        conf = get_db("settings.json")
        if conf.get("notifications"):
            try:
                bot.send_message(OWNER_ID, f"🔔 **مستخدم جديد دخل للبوت!**\n\n👤 الاسم: {message.from_user.first_name}\n🆔 الآيدي: `{uid}`", parse_mode="Markdown")
            except: pass
            
    bot.send_message(uid, welcome_text, reply_markup=main_kb(uid))

# --- [ راوتر الأزرار ] ---
@bot.message_handler(func=lambda m: True)
def router(message):
    uid, text = message.from_user.id, message.text
    conf = get_db("settings.json")

    # 1. النشر في القناة (الواجهة الاحترافية)
    if text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        with open("bot_files.txt", "r") as f:
            files = f.read().splitlines()
        
        if not files:
            return bot.send_message(uid, "❌ قاعدة البيانات فارغة، أضف ملفات أولاً!")
        
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(
            types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
            types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like")
        )
        
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
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    # 2. إضافة اشتراك
    elif text == "إضافة اشتراك 🔗" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🔗 أرسل رابط القناة الجديد (t.me/...):")
        bot.register_next_step_handler(m, save_sub)

    # 3. تنظيف الإحصائيات
    elif text == "تنظيف البيانات 🧹" and int(uid) == OWNER_ID:
        st = {"downloads": 0, "likes": 0, "likes_log": [], "downloads_log": []}
        save_db("stats.json", st)
        bot.send_message(uid, "🧹 تم تصفير كافة الإحصائيات وسجلات التفاعل.")

    # 4. الإحصائيات
    elif text == "الإحصائيات 📊" and has_perm(uid, "can_broadcast"):
        st = get_db("stats.json")
        with open("users.txt", "r") as f:
            u_count = len(f.read().splitlines())
        
        msg = (f"📊 **إحصائيات البوت:**\n\n"
               f"👥 مستخدمين: `{u_count}`\n"
               f"📩 استلام فريد: `{len(st.get('downloads_log', []))}`\n"
               f"❤️ تفاعل فريد: `{len(st.get('likes_log', []))}`")
        bot.send_message(uid, msg, parse_mode="Markdown")

    # 5. إضافة ملفات
    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_post"):
        m = bot.send_message(uid, "📤 أرسل الملف/الكونفيج الآن:")
        bot.register_next_step_handler(m, save_file)

    # 6. إعدادات الإشعارات
    elif text in ["إيقاف الإشعارات ❌", "تفعيل الإشعارات ✅"]:
        conf["notifications"] = not conf["notifications"]
        save_db("settings.json", conf)
        bot.send_message(uid, "⚙️ تم تحديث الإعدادات.", reply_markup=main_kb(uid))

    # 7. تصفير الملفات
    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w") as f: f.truncate(0)
        bot.send_message(uid, "🗑️ تم مسح قائمة الملفات.")

# --- [ وظائف المساعدة ] ---

def save_sub(message):
    if "t.me/" in message.text:
        conf = get_db("settings.json")
        conf["sub_link"] = message.text
        try:
            username = "@" + message.text.split("t.me/")[1].split("/")[0]
            conf["channel_id"] = username
            save_db("settings.json", conf)
            bot.send_message(message.chat.id, f"✅ تم تحديث القناة لـ: {username}")
        except:
            bot.send_message(message.chat.id, "❌ خطأ في الرابط.")
    else:
        bot.send_message(message.chat.id, "❌ أرسل رابطاً صحيحاً.")

def save_file(message):
    fid = None
    if message.document: fid = message.document.file_id
    elif message.video: fid = message.video.file_id
    elif message.photo: fid = message.photo[-1].file_id
    
    if fid:
        with open("bot_files.txt", "a") as f:
            f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم الحفظ بنجاح.")
    else:
        bot.send_message(message.chat.id, "❌ لم يتم التعرف على الملف.")

# --- [ التفاعلات ومنع التكرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid, st = call.from_user.id, get_db("stats.json")

    if call.data == "hit_like":
        if uid in st.get("likes_log", []):
            bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً!", show_alert=True)
        else:
            st["likes"] += 1
            st.setdefault("likes_log", []).append(uid)
            save_db("stats.json", st)
            bot.answer_callback_query(call.id, f"❤️ شكراً SELVA! الإجمالي: {st['likes']}")

    elif call.data == "get_files":
        with open("bot_files.txt", "r") as f:
            files = f.read().splitlines()
        
        if not files:
            return bot.answer_callback_query(call.id, "❌ لا توجد ملفات.")
        
        if uid not in st.get("downloads_log", []):
            st["downloads"] += 1
            st.setdefault("downloads_log", []).append(uid)
            save_db("stats.json", st)
        
        bot.answer_callback_query(call.id, "🚀 جاري الإرسال...")
        for fid in files:
            try: bot.send_document(uid, fid)
            except: pass

if __name__ == "__main__":
    print("🤖 SELVA BOT IS READY...")
    bot.infinity_polling()

