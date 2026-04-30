import telebot
from telebot import types
import os, json, time, threading

# --- [ الإعدادات الأساسية ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# مخزن مؤقت للجلسات
pending_files = {}

# --- [ نظام إدارة قاعدة البيانات المطور ] ---
def init_db():
    database = {
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
            "sub_link": "https://t.me/Uchiha75",
            "force_sub": True  # تفعيل الاشتراك الإجباري
        })
    }
    for f, c in database.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file:
                file.write(c)

init_db()

def get_db(file):
    try:
        if not os.path.exists(file): return [] if "files" in file else {}
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "files" in file and not isinstance(data, list): return []
            return data
    except: return [] if "files" in file else {}

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_db("admins.json")
    return admins.get(str(uid), {}).get(perm, False)

# --- [ التحقق من الاشتراك الإجباري ] ---
def check_sub(uid):
    conf = get_db("settings.json")
    if not conf.get("force_sub"): return True
    try:
        member = bot.get_chat_member(conf["channel_id"], uid)
        if member.status in ['member', 'administrator', 'creator']: return True
        return False
    except: return True # في حال فشل البوت في التحقق نمرره منعاً للكراش

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
        kb.row(n_status, "تصفير الملفات 🗑️")
        kb.row("تنظيف البيانات 🧹")
    
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add("إذاعة للمستخدمين 👥", "إذاعة للقنوات 📢", "رجوع للخلف 🔙")
    return kb

# --- [ معالجة أمر Start ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
    # التحقق من الاشتراك
    if not check_sub(uid) and int(uid) != OWNER_ID:
        conf = get_db("settings.json")
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اضغط هنا للاشتراك ⚡", url=conf["sub_link"]))
        return bot.send_message(uid, f"⚠️ عذراً عزيزي، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت!", reply_markup=mk)

    welcome = "مرحبا ايها مطور 😈SELVA 😈" if int(uid) == OWNER_ID else "مرحبا بك في بوت توزيع الكونفيجات ⚡"
    
    # تسجيل المستخدم
    if not os.path.exists("users.txt"): open("users.txt", "w").close()
    with open("users.txt", "r") as f: users = f.read().splitlines()
    
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        conf = get_db("settings.json")
        if conf.get("notifications"):
            try: bot.send_message(OWNER_ID, f"🔔 **دخول مستخدم جديد!**\n👤 الاسم: {message.from_user.first_name}\n🆔 الآيدي: `{uid}`", parse_mode="Markdown")
            except: pass
            
    bot.send_message(uid, welcome, reply_markup=main_kb(uid))

# --- [ راوتر العمليات الرئيسي ] ---
@bot.message_handler(func=lambda m: True)
def router(message):
    uid, text = message.from_user.id, message.text
    conf = get_db("settings.json")

    # 1. قسم الإذاعة (للمخلفين بصلاحية)
    if text == "قسم الإذاعة 📢" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "اختر نوع الإذاعة:", reply_markup=broadcast_kb())

    elif text == "إذاعة للمستخدمين 👥" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "أرسل الرسالة (نص، صورة، فيديو) لإذاعتها للجميع:")
        bot.register_next_step_handler(m, start_broadcast)

    elif text == "رجوع للخلف 🔙":
        bot.send_message(uid, "العودة للقائمة...", reply_markup=main_kb(uid))

    # 2. إدارة الملفات والنشر
    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_post"):
        pending_files[uid] = [] 
        mk = types.ReplyKeyboardMarkup(resize_keyboard=True); mk.add("إنهاء الحفظ ✅")
        bot.send_message(uid, "📤 ابدأ بإرسال الملفات مع أوصافها. عند الانتهاء اضغط الزر بالأسفل.", reply_markup=mk)
        bot.register_next_step_handler(message, file_collector_logic)

    elif text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        files = get_db("bot_files.json")
        if not files: return bot.send_message(uid, "❌ لا توجد ملفات لنشرها.")
        
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        
        caption = f"⚡ **تحديث جديد للكونفيجات!**\n\n📁 الإجمالي: {len(files)} ملف\n📍 القناة: {conf['channel_id']}\n━━━━━━━━━━━━━━"
        bot.send_message(conf["channel_id"], caption, reply_markup=mk, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    # 3. إدارة الأدمن (للأونر فقط)
    elif text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "➕ أرسل آيدي الشخص لترقيته:")
        bot.register_next_step_handler(m, add_admin_logic)

    elif text == "الإحصائيات 📊":
        st = get_db("stats.json")
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        bot.send_message(uid, f"📊 **إحصائيات البوت:**\n\n👥 المشتركين: `{u_count}`\n❤️ التفاعلات: `{st.get('likes', 0)}`", parse_mode="Markdown")

    elif text == "تصفير الملفات 🗑️" and int(uid) == OWNER_ID:
        save_db("bot_files.json", [])
        bot.send_message(uid, "🗑️ تم مسح كافة الملفات بنجاح.")

# --- [ وظائف التنفيذ المساعدة ] ---

def start_broadcast(message):
    with open("users.txt", "r") as f: users = f.read().splitlines()
    bot.send_message(message.chat.id, f"🚀 جاري الإرسال إلى {len(users)} مستخدم...")
    success = 0
    for u in users:
        try:
            bot.copy_message(u, message.chat.id, message.message_id)
            success += 1
            time.sleep(0.05)
        except: continue
    bot.send_message(message.chat.id, f"✅ اكتملت الإذاعة بنجاح لـ {success} مستخدم.")

def add_admin_logic(message):
    if message.text.isdigit():
        admins = get_db("admins.json")
        admins[message.text] = {"can_post": True, "can_broadcast": True}
        save_db("admins.json", admins)
        bot.send_message(message.chat.id, f"✅ تم تعيين {message.text} كأدمن.")
    else: bot.send_message(message.chat.id, "❌ آيدي غير صحيح.")

def file_collector_logic(message):
    uid = message.from_user.id
    if message.text == "إنهاء الحفظ ✅":
        if uid in pending_files and pending_files[uid]:
            db = get_db("bot_files.json")
            db.extend(pending_files[uid]); save_db("bot_files.json", db)
            bot.send_message(uid, f"✅ تم حفظ {len(pending_files[uid])} ملف.", reply_markup=main_kb(uid))
            del pending_files[uid]
        else: bot.send_message(uid, "❌ لم يتم إرسال ملفات.", reply_markup=main_kb(uid))
        return

    fid = message.document.file_id if message.document else (message.video.file_id if message.video else (message.photo[-1].file_id if message.photo else None))
    if fid:
        pending_files.setdefault(uid, []).append({"file_id": fid, "caption": message.caption or ""})
        bot.send_message(uid, f"📥 تم الاستلام ({len(pending_files[uid])})...")
    bot.register_next_step_handler(message, file_collector_logic)

# --- [ كول باك التفاعلات ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    st = get_db("stats.json"); uid = call.from_user.id
    if call.data == "hit_like":
        if uid not in st.get("likes_log", []):
            st["likes"] += 1; st.setdefault("likes_log", []).append(uid); save_db("stats.json", st)
            bot.answer_callback_query(call.id, "❤️ شكراً SELVA!")
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً", show_alert=True)
    
    elif call.data == "get_files":
        files = get_db("bot_files.json")
        if not files: return bot.answer_callback_query(call.id, "❌ القائمة فارغة.")
        bot.answer_callback_query(call.id, "🚀 استلم يا وحش...")
        for item in files:
            try: bot.send_document(uid, item["file_id"], caption=item["caption"])
            except: continue

if __name__ == "__main__":
    print("🔥 SELVA ULTIMATE BOT IS ONLINE...")
    bot.infinity_polling()

