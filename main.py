import telebot
from telebot import types
import os, json

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

# --- [ لوحات التحكم - الكيبوردات ] ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    n_status = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    # توزيع الأزرار بناءً على الصلاحيات
    if has_perm(uid, "can_post"): kb.row("نشر في القناة 📣")
    if has_perm(uid, "can_add_files"): kb.insert("إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"): kb.row("إرسال إذاعة 📣")
    kb.insert("الإحصائيات 📊")
    
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "تعديل صلاحيات ⚙️")
        kb.row("إضافة اشتراك 🔗", n_status)
    else:
        kb.row(n_status)
        
    if has_perm(uid, "can_reset"): kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
    return kb

# --- [ معالجة الأوامر الرئيسية ] ---
@bot.message_handler(commands=['start'])
def start_command(message):
    uid = message.from_user.id
    # رسالة المطور ورسالة المستخدم الجديد
    welcome = "مرحبا ايها مطور 😈" if int(uid) == OWNER_ID else "مرحبا ايها مستخدم الجديد"
    
    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        conf = get_db("settings.json")
        if conf.get("notifications"):
            try: bot.send_message(OWNER_ID, f"🔔 مستخدم جديد دخل للبوت: `{uid}`", parse_mode="Markdown")
            except: pass
            
    bot.send_message(uid, welcome, reply_markup=main_kb(uid))

# --- [ راوتر الأزرار الرئيسي - Bot Running Router ] ---
@bot.message_handler(func=lambda m: True)
def main_router(message):
    uid, text = message.from_user.id, message.text
    conf = get_db("settings.json")

    # 1. نظام النشر في القناة (الواجهة الاحترافية)
    if text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.send_message(uid, "❌ قائمة الملفات فارغة!")
        
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        
        caption = (
            "⚡ **تم تجديد الملفات الحصرية!**\n"
            "━━━━━━━━━━━━━━\n"
            f"📁 عدد الملفات: `{len(files)}` ملف\n"
            "🚀 السرعة: فائقة (Ultra Speed)\n"
            "━━━━━━━━━━━━━━\n"
            "📌 **طريقة الاستلام:**\n"
            "اضغط على الزر أدناه وسيرسلها البوت لك فوراً\n"
            "━━━━━━━━━━━━━━"
        )
        bot.send_message(conf["channel_id"], caption, reply_markup=mk, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بالواجهة الاحترافية.")

    # 2. نظام إضافة الملفات
    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_add_files"):
        m = bot.send_message(uid, "📤 أرسل الآن (صورة/فيديو/ملف):")
        bot.register_next_step_handler(m, save_file_logic)

    # 3. نظام الإذاعة الثلاثية
    elif text == "إرسال إذاعة 📣" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "🎯 اختر هدف الإذاعة:", reply_markup=broadcast_kb())

    elif text in ["إذاعة قناة 📢", "إذاعة مستخدمين 👥", "إذاعة الجميع 🌐"]:
        mode = "channel" if "قناة" in text else ("users" if "مستخدمين" in text else "all")
        m = bot.send_message(uid, f"💬 أرسل محتوى ({text}):")
        bot.register_next_step_handler(m, lambda msg: exec_broadcast(msg, mode))

    # 4. نظام الأدمن والصلاحيات
    elif text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, admin_setup_logic)

    elif text == "تعديل صلاحيات ⚙️" and int(uid) == OWNER_ID:
        admins = get_db("admins.json")
        if not admins: return bot.send_message(uid, "❌ لا يوجد أدمنية.")
        mk = types.InlineKeyboardMarkup()
        for aid in admins: mk.add(types.InlineKeyboardButton(f"👤 {aid}", callback_data=f"edit_p_{aid}"))
        bot.send_message(uid, "⚙️ اختر آيدي الأدمن لتعديل صلاحياته:", reply_markup=mk)

    # 5. تنظيف وتصفير البيانات
    elif text == "تنظيف البيانات 🧹" and has_perm(uid, "can_reset"):
        with open("users.txt", "w") as f: f.truncate(0)
        save_db("stats.json", {"downloads": 0, "likes": 0})
        bot.send_message(uid, "🧹 تم مسح كافة المستخدمين وتصفير الإحصائيات.")

    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w") as f: f.truncate(0)
        bot.send_message(uid, "🗑️ تم تصفير قائمة الملفات.")

    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u = len(f.read().splitlines())
        st = get_db("stats.json")
        bot.send_message(uid, f"📊 **إحصائيات بوت رانين:**\n\n👥 مستخدمين: `{u}`\n📩 استلام: `{st['downloads']}`\n❤️ تفاعل: `{st['likes']}`", parse_mode="Markdown")

    elif text == "رجوع 🔙":
        bot.send_message(uid, "🔙 العودة للرئيسية:", reply_markup=main_kb(uid))

# --- [ وظائف التنفيذ المتقدمة ] ---

def save_file_logic(message):
    fid = message.document.file_id if message.document else (
          message.video.file_id if message.video else (
          message.photo[-1].file_id if message.photo else None))
    if fid:
        with open("bot_files.txt", "a") as f: f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم حفظ الملف بنجاح.", reply_markup=main_kb(message.from_user.id))
    else:
        bot.send_message(message.chat.id, "❌ فشل الحفظ! أرسل ملفاً صحيحاً.", reply_markup=main_kb(message.from_user.id))

def admin_setup_logic(message):
    target = message.text
    if not target.isdigit(): return bot.send_message(message.chat.id, "❌ الآيدي غير صحيح.")
    admins = get_db("admins.json")
    if target not in admins:
        admins[target] = {"can_post": False, "can_broadcast": False, "can_add_files": False, "can_reset": False}
        save_db("admins.json", admins)
    show_perm_panel(message.chat.id, target)

def show_perm_panel(chat_id, target):
    admins = get_db("admins.json")
    p = admins[target]
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton(f"نشر: {'✅' if p['can_post'] else '❌'}", callback_data=f"tg_{target}_can_post"),
        types.InlineKeyboardButton(f"إذاعة: {'✅' if p['can_broadcast'] else '❌'}", callback_data=f"tg_{target}_can_broadcast"),
        types.InlineKeyboardButton(f"ملفات: {'✅' if p['can_add_files'] else '❌'}", callback_data=f"tg_{target}_can_add_files"),
        types.InlineKeyboardButton(f"تصفير: {'✅' if p['can_reset'] else '❌'}", callback_data=f"tg_{target}_can_reset"),
        types.InlineKeyboardButton("🗑️ حذف الأدمن", callback_data=f"rm_adm_{target}"),
        types.InlineKeyboardButton("✅ حفظ الخروج", callback_data="exit_p")
    )
    bot.send_message(chat_id, f"⚙️ تحكم بصلاحيات ({target}):", reply_markup=mk)

def exec_broadcast(message, mode):
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
    bot.send_message(message.chat.id, f"✅ تمت الإذاعة لـ {sent} هدف.", reply_markup=main_kb(message.from_user.id))

# --- [ معالجة الكيوري (Callback Handler) ] ---
@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid, data = call.from_user.id, call.data
    
    if data.startswith("edit_p_"):
        show_perm_panel(call.message.chat.id, data.split("_")[2])
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif data.startswith("tg_"):
        _, target, perm = data.split("_", 2)
        admins = get_db("admins.json")
        admins[target][perm] = not admins[target][perm]
        save_db("admins.json", admins)
        show_perm_panel(call.message.chat.id, target)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif data == "get_files":
        st = get_db("stats.json"); st["downloads"] += 1; save_db("stats.json", st)
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.answer_callback_query(call.id, "❌ لا توجد ملفات حالياً.")
        for f in files: 
            try: bot.send_document(uid, f)
            except: pass
        bot.answer_callback_query(call.id, "📩 تم إرسال كافة الملفات لخاصك!")

    elif data == "hit_like":
        st = get_db("stats.json"); st["likes"] += 1; save_db("stats.json", st)
        bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")

    elif data == "exit_p":
        bot.edit_message_text("✅ تم تحديث كافة الصلاحيات.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    print("🤖 Bot Running System is Online...")
    bot.infinity_polling()

