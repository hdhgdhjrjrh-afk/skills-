import telebot
from telebot import types
import os, json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام قاعدة البيانات ---
def init_db():
    files = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "{}", 
        "stats.json": json.dumps({"downloads": 0, "likes": 0}), # لتخزين الإحصائيات
        "settings.json": json.dumps({
            "notifications": True, 
            "channel_id": "@Uchiha75", 
            "sub_link": "https://t.me/Uchiha75"
        })
    }
    for f, c in files.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file: file.write(c)

init_db()

def get_conf():
    with open("settings.json", "r", encoding="utf-8") as f: return json.load(f)

def get_admins():
    with open("admins.json", "r", encoding="utf-8") as f: return json.load(f)

def get_stats():
    with open("stats.json", "r", encoding="utf-8") as f: return json.load(f)

def update_stats(key):
    stats = get_stats()
    stats[key] += 1
    with open("stats.json", "w", encoding="utf-8") as f: json.dump(stats, f)

# --- فحص الصلاحيات والاشتراك ---
def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_admins()
    admin_data = admins.get(str(uid))
    if admin_data and admin_data.get(perm): return True
    return False

def is_subscribed(uid):
    conf = get_conf()
    try:
        status = bot.get_chat_member(conf["channel_id"], uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- لوحات التحكم ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_conf()
    n_status = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"): kb.row("نشر تلقائي 📣")
    if has_perm(uid, "can_add_files"): kb.row("إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"): kb.row("إرسال إذاعة 📣")
    kb.row("الإحصائيات 📊", n_status)
    if has_perm(uid, "can_reset"): kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    if int(uid) == OWNER_ID: kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
    kb.row("إنهاء ✅")
    return kb

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    conf = get_conf()
    
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك هنا أولاً 📢", url=conf["sub_link"]))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="verify_sub"))
        return bot.send_message(uid, "⚠️ يجب الاشتراك في القناة أولاً لاستخدام البوت!", reply_markup=mk)

    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        if conf.get("notifications"):
            try: bot.send_message(OWNER_ID, f"🔔 مستخدم جديد سجل: {message.from_user.first_name}")
            except: pass

    bot.send_message(uid, "✅ أهلاً بك! استخدم القائمة أدناه:", reply_markup=main_kb(uid))

# --- معالجة أزرار الأدمن ---
@bot.message_handler(func=lambda m: int(m.from_user.id) == OWNER_ID or str(m.from_user.id) in get_admins())
def handle_admin_actions(message):
    uid, text = message.from_user.id, message.text

    if text == "نشر تلقائي 📣" and has_perm(uid, "can_post"):
        if not os.path.exists("bot_files.txt"): files = []
        else:
            with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        
        if not files: return bot.send_message(uid, "❌ لا توجد ملفات لنشرها!")
        
        conf = get_conf()
        caption = (
            "⚡ **تم تجديد الكونفيجات!**\n\n"
            f"📁 عدد الملفات: {len(files)}\n"
            "🚀 سرعة عالية | ⏳ محدد المدة\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "📌 **طريقة الاستلام:**\n\n"
            "1️⃣ فعّل البوت بالضغط على 🤖\n"
            "2️⃣ ادعمنا بضغطة ❤️\n"
            "3️⃣ اضغط 📩 لاستلام الملفات\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "⚠️ سارع قبل انتهاء الصلاحية!"
        )
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        
        bot.send_message(conf["channel_id"], caption, reply_markup=mk, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر في القناة.")

    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w", encoding="utf-8") as f: f.write("")
        bot.send_message(uid, "✅ تم تصفير جميع الملفات بنجاح.")

    elif text == "تنظيف البيانات 🧹" and has_perm(uid, "can_reset"):
        with open("users.txt", "w", encoding="utf-8") as f: f.write("")
        with open("stats.json", "w", encoding="utf-8") as f: json.dump({"downloads": 0, "likes": 0}, f)
        bot.send_message(uid, "✅ تم تنظيف قائمة المستخدمين والإحصائيات.")

    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        stats = get_stats()
        msg = (
            "📊 **إحصائيات البوت الحالية:**\n\n"
            f"👥 عدد المشتركين: `{u_count}`\n"
            f"📩 عدد مرات الاستلام: `{stats['downloads']}`\n"
            f"❤️ عدد التفاعلات: `{stats['likes']}`"
        )
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_add_files"):
        m = bot.send_message(uid, "📤 أرسل الملف الآن (صورة، فيديو، مستند):")
        bot.register_next_step_handler(m, save_file)

    elif text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, admin_permission_setup)

# --- وظائف إضافية ---
def save_file(message):
    fid = None
    if message.document: fid = message.document.file_id
    elif message.video: fid = message.video.file_id
    elif message.photo: fid = message.photo[-1].file_id
    
    if fid:
        with open("bot_files.txt", "a", encoding="utf-8") as f: f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم حفظ الملف!", reply_markup=main_kb(message.from_user.id))
    else: bot.send_message(message.chat.id, "❌ خطأ في الملف.")

def admin_permission_setup(message):
    if not message.text.isdigit(): return bot.send_message(message.chat.id, "❌ آيدي خاطئ.")
    target = message.text
    mk = types.InlineKeyboardMarkup()
    mk.row(types.InlineKeyboardButton("إذاعة ✅", callback_data=f"p_bc_{target}"),
           types.InlineKeyboardButton("نشر ✅", callback_data=f"p_pst_{target}"))
    mk.row(types.InlineKeyboardButton("ملفات ✅", callback_data=f"p_fl_{target}"),
           types.InlineKeyboardButton("تصفير ✅", callback_data=f"p_rs_{target}"))
    mk.add(types.InlineKeyboardButton("💾 حفظ الصلاحيات", callback_data=f"sv_ad_{target}"))
    bot.send_message(message.chat.id, f"⚙️ اختر صلاحيات الأدمن `{target}`:", reply_markup=mk)

# --- معالجة الـ Callbacks ---
temp_p = {}
@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    uid, data = call.from_user.id, call.data
    
    if data.startswith("p_"):
        _, p_type, target = data.split("_")
        if target not in temp_p: temp_p[target] = {"can_broadcast":False, "can_post":False, "can_add_files":False, "can_reset":False}
        map_p = {"bc":"can_broadcast", "pst":"can_post", "fl":"can_add_files", "rs":"can_reset"}
        temp_p[target][map_p[p_type]] = not temp_p[target][map_p[p_type]]
        bot.answer_callback_query(call.id, "تم التعديل ✅")

    elif data.startswith("sv_ad_"):
        target = data.split("_")[-1]
        ads = get_admins()
        ads[target] = temp_p.get(target, {"can_broadcast":False, "can_post":False, "can_add_files":False, "can_reset":False})
        with open("admins.json", "w", encoding="utf-8") as f: json.dump(ads, f)
        bot.edit_message_text(f"✅ تم حفظ الأدمن `{target}`.", call.message.chat.id, call.message.message_id)

    elif data == "get_files":
        if not os.path.exists("bot_files.txt"): files = []
        else:
            with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        
        if not files: return bot.answer_callback_query(call.id, "❌ لا توجد ملفات.", show_alert=True)
        
        update_stats("downloads") # تحديث إحصائيات الاستلام
        bot.answer_callback_query(call.id, "🚀 جاري الإرسال...")
        for fid in files:
            try: bot.send_document(uid, fid)
            except: 
                try: bot.send_video(uid, fid)
                except: bot.send_photo(uid, fid)

    elif data == "hit_like":
        update_stats("likes") # تحديث إحصائيات التفاعل
        bot.answer_callback_query(call.id, "❤️ تم تسجيل التفاعل، شكراً لك!")

    elif data == "verify_sub":
        if is_subscribed(uid):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(uid, "✅ تم التحقق! أرسل /start الآن.")
        else: bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()

