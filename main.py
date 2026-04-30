import telebot
from telebot import types
import os, json, time, sys

# --- [ الإعدادات الأساسية ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# مخزن الجلسات المؤقتة للملفات
pending_files = {}

# --- [ نظام إدارة قاعدة البيانات الاحترافي ] ---
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
            "force_sub": True
        })
    }
    for filename, content in database.items():
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)

init_db()

def get_db(file):
    try:
        if not os.path.exists(file): return [] if "files" in file else {}
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "files" in file and not isinstance(data, list): return []
            return data
    except Exception:
        return [] if "files" in file else {}

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_db("admins.json")
    return admins.get(str(uid), {}).get(perm, False)

# --- [ نظام التحقق من الاشتراك ] ---
def check_subscription(uid):
    conf = get_db("settings.json")
    if not conf.get("force_sub") or int(uid) == OWNER_ID: return True
    try:
        member = bot.get_chat_member(conf["channel_id"], uid)
        if member.status in ['member', 'administrator', 'creator']: return True
        return False
    except Exception: return True # تمرير في حال وجود خطأ تقني

# --- [ لوحات التحكم الشاملة ] ---
def main_keyboard(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    notif_text = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"):
        kb.row("نشر في القناة 📣", "إضافة ملفات 📤")
    
    if has_perm(uid, "can_broadcast"):
        kb.row("قسم الإذاعة 📢", "الإحصائيات 📊")
    
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
        kb.row(notif_text, "تصفير الملفات 🗑️")
        kb.row("تنظيف البيانات 🧹")
    
    return kb

def broadcast_keyboard():
    kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add("إذاعة للمستخدمين 👥", "إذاعة للقنوات 📢", "إذاعة توجيه (Forward) 🔄", "رجوع للخلف 🔙")
    return kb

# --- [ معالجة أمر Start ] ---
@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    
    # التحقق من الاشتراك الإجباري
    if not check_subscription(uid):
        conf = get_db("settings.json")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك هنا أولاً ⚡", url=conf["sub_link"]))
        return bot.send_message(uid, "⚠️ عذراً، يجب عليك الاشتراك في القناة لاستخدام البوت!", reply_markup=markup)

    welcome_msg = "مرحبا ايها مطور 😈SELVA 😈" if int(uid) == OWNER_ID else "مرحبا بك في بوت توزيع الكونفيجات المتطور ⚡"
    
    # تسجيل المستخدم الجديد
    if not os.path.exists("users.txt"): open("users.txt", "w").close()
    with open("users.txt", "r") as f: users = f.read().splitlines()
    
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        conf = get_db("settings.json")
        if conf.get("notifications"):
            try: bot.send_message(OWNER_ID, f"🔔 **مستخدم جديد:**\n👤 الاسم: {message.from_user.first_name}\n🆔 الآيدي: `{uid}`", parse_mode="Markdown")
            except: pass
            
    bot.send_message(uid, welcome_msg, reply_markup=main_keyboard(uid))

# --- [ راوتر العمليات الرئيسي ] ---
@bot.message_handler(func=lambda m: True)
def router(message):
    uid, text = message.from_user.id, message.text
    conf = get_db("settings.json")

    # 1. قسم الإذاعة
    if text == "قسم الإذاعة 📢" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "اختر نوع الإذاعة المطلوبة:", reply_markup=broadcast_keyboard())

    elif text == "إذاعة للمستخدمين 👥" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "أرسل الرسالة (نص، صورة، فيديو) لإذاعتها للجميع:")
        bot.register_next_step_handler(m, lambda msg: start_broadcast_action(msg, "copy"))

    elif text == "إذاعة توجيه (Forward) 🔄" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "أرسل الرسالة لعمل توجيه لها للجميع:")
        bot.register_next_step_handler(m, lambda msg: start_broadcast_action(msg, "forward"))

    elif text == "رجوع للخلف 🔙":
        bot.send_message(uid, "العودة للقائمة الرئيسية...", reply_markup=main_keyboard(uid))

    # 2. إدارة الملفات والنشر
    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_post"):
        pending_files[uid] = [] 
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True); markup.add("إنهاء الحفظ ✅")
        bot.send_message(uid, "📤 أرسل الملفات الآن (ملف أو فيديو) مع أوصافها.\nعند الانتهاء اضغط 'إنهاء الحفظ ✅'.", reply_markup=markup)
        bot.register_next_step_handler(message, file_collector_step)

    elif text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        files_data = get_db("bot_files.json")
        if not files_data: return bot.send_message(uid, "❌ لا توجد ملفات محفوظة لنشرها!")
        
        btn_markup = types.InlineKeyboardMarkup(row_width=2)
        btn_markup.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
                      types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        
        post_caption = (f"⚡ **تحديث جديد للكونفيجات!**\n\n📁 عدد الملفات: {len(files_data)}\n🚀 السرعة: عالية جداً\n━━━━━━━━━━━━━━")
        bot.send_message(conf["channel_id"], post_caption, reply_markup=btn_markup, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    # 3. إعدادات المطور (OWNER ONLY)
    elif text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "➕ أرسل آيدي الشخص المراد ترقيته:")
        bot.register_next_step_handler(m, admin_upgrade_step)

    elif text == "إضافة اشتراك 🔗" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🔗 أرسل رابط قناتك الجديد (مثال: t.me/Uchiha75):")
        bot.register_next_step_handler(m, update_subscription_step)

    elif text == "تصفير الملفات 🗑️" and int(uid) == OWNER_ID:
        save_db("bot_files.json", [])
        bot.send_message(uid, "🗑️ تم مسح كافة الملفات من قاعدة البيانات.")

    elif text == "تنظيف البيانات 🧹" and int(uid) == OWNER_ID:
        save_db("stats.json", {"downloads": 0, "likes": 0, "likes_log": [], "downloads_log": []})
        bot.send_message(uid, "🧹 تم تصفير سجلات التفاعل والإحصائيات.")

    elif text in ["تفعيل الإشعارات ✅", "إيقاف الإشعارات ❌"] and int(uid) == OWNER_ID:
        conf["notifications"] = not conf["notifications"]
        save_db("settings.json", conf)
        bot.send_message(uid, "⚙️ تم تحديث وضع الإشعارات بنجاح.", reply_markup=main_keyboard(uid))

# --- [ وظائف التنفيذ المنفصلة ] ---

def start_broadcast_action(message, mode):
    with open("users.txt", "r") as f: users = f.read().splitlines()
    bot.send_message(message.chat.id, f"🚀 جاري الإذاعة لـ {len(users)} مستخدم...")
    count = 0
    for u in users:
        try:
            if mode == "copy": bot.copy_message(u, message.chat.id, message.message_id)
            else: bot.forward_message(u, message.chat.id, message.message_id)
            count += 1
            time.sleep(0.05)
        except: continue
    bot.send_message(message.chat.id, f"✅ اكتملت الإذاعة بنجاح لـ {count} مستخدم.")

def file_collector_step(message):
    uid = message.from_user.id
    if message.text == "إنهاء الحفظ ✅":
        if uid in pending_files and pending_files[uid]:
            db = get_db("bot_files.json")
            db.extend(pending_files[uid]); save_db("bot_files.json", db)
            bot.send_message(uid, f"✅ تم حفظ {len(pending_files[uid])} ملف بنجاح!", reply_markup=main_keyboard(uid))
            del pending_files[uid]
        else: bot.send_message(uid, "❌ لم يتم إرسال ملفات.", reply_markup=main_keyboard(uid))
        return

    # استخراج معرف الملف
    file_id = None
    if message.document: file_id = message.document.file_id
    elif message.video: file_id = message.video.file_id
    elif message.photo: file_id = message.photo[-1].file_id

    if file_id:
        caption = message.caption if message.caption else ""
        pending_files.setdefault(uid, []).append({"file_id": file_id, "caption": caption})
        bot.send_message(uid, f"📥 تم استلام الملف رقم ({len(pending_files[uid])})... أرسل المزيد أو اضغط إنهاء.")
    
    bot.register_next_step_handler(message, file_collector_step)

def admin_upgrade_step(message):
    if message.text.isdigit():
        admins = get_db("admins.json")
        admins[str(message.text)] = {"can_post": True, "can_broadcast": True}
        save_db("admins.json", admins)
        bot.send_message(message.chat.id, f"✅ تم ترقية {message.text} كأدمن.")
    else: bot.send_message(message.chat.id, "❌ الآيدي غير صحيح.")

def update_subscription_step(message):
    if "t.me/" in message.text:
        conf = get_db("settings.json")
        conf["sub_link"] = message.text
        conf["channel_id"] = "@" + message.text.split("t.me/")[1]
        save_db("settings.json", conf)
        bot.send_message(message.chat.id, "✅ تم تحديث بيانات الاشتراك الإجباري.")
    else: bot.send_message(message.chat.id, "❌ رابط غير صالح.")

# --- [ كول باك التفاعلات ] ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    stats = get_db("stats.json"); uid = call.from_user.id
    if call.data == "hit_like":
        if uid not in stats.get("likes_log", []):
            stats["likes"] += 1; stats.setdefault("likes_log", []).append(uid); save_db("stats.json", stats)
            bot.answer_callback_query(call.id, "❤️ شكراً SELVA!")
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً", show_alert=True)
    
    elif call.data == "get_files":
        files = get_db("bot_files.json")
        if not files: return bot.answer_callback_query(call.id, "❌ لا توجد ملفات حالياً.")
        bot.answer_callback_query(call.id, "🚀 جاري إرسال الملفات...")
        for item in files:
            try: bot.send_document(uid, item["file_id"], caption=item["caption"])
            except: continue

if __name__ == "__main__":
    print("🔥 SELVA SUPER BOT (COMPLETE VERSION) IS ONLINE...")
    bot.infinity_polling()
