import telebot
from telebot import types
import os, json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام الملفات وقاعدة البيانات ---
def init_db():
    files = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "{}", 
        "activity.json": "{}",
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

# --- فحص الصلاحيات ---
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

# --- الكيبوردات (الواجهة) ---
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

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
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

    if int(uid) == OWNER_ID or str(uid) in get_admins():
        return bot.send_message(uid, "👑 أهلاً بك في لوحة التحكم بصلاحياتك:", reply_markup=main_kb(uid))

    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        if conf.get("notifications"):
            bot.send_message(OWNER_ID, f"🔔 مستخدم جديد سجل: {message.from_user.first_name}")

    bot.send_message(uid, "✅ تم تفعيل البوت بنجاح!")

# --- معالجة أزرار الأدمن والعمليات ---
@bot.message_handler(func=lambda m: int(m.from_user.id) == OWNER_ID or str(m.from_user.id) in get_admins())
def handle_admin_actions(message):
    uid, text = message.from_user.id, message.text

    if text == "إرسال إذاعة 📣" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "🎯 اختر نوع الإذاعة:", reply_markup=broadcast_kb())

    elif text == "إذاعة قناة 📢" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "📢 أرسل الرسالة لنشرها في القناة:")
        bot.register_next_step_handler(m, lambda msg: run_bc(msg, "channel"))

    elif text == "إذاعة مستخدمين 👥" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "👥 أرسل الرسالة لإذاعتها للمستخدمين:")
        bot.register_next_step_handler(m, lambda msg: run_bc(msg, "users"))

    elif text == "إذاعة الجميع 🌐" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "🌐 أرسل رسالة للجميع:")
        bot.register_next_step_handler(m, lambda msg: run_bc(msg, "all"))

    elif text == "نشر تلقائي 📣" and has_perm(uid, "can_post"):
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.send_message(uid, "❌ لا توجد ملفات لنشرها!")
        conf = get_conf()
        mk = types.InlineKeyboardMarkup()
        mk.row(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        bot.send_message(conf["channel_id"], f"🚀 تحديث جديد! المتوفر: {len(files)} ملف.", reply_markup=mk)
        bot.send_message(uid, "✅ تم النشر في القناة.")

    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_add_files"):
        m = bot.send_message(uid, "📤 أرسل الملف الآن (صورة، فيديو، مستند):")
        bot.register_next_step_handler(m, save_file)

    elif text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, admin_permission_setup)

    elif text == "إضافة اشتراك 🔗" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🔗 أرسل رابط القناة الجديد:")
        bot.register_next_step_handler(m, update_subscription)

    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        bot.send_message(uid, f"📊 عدد المستخدمين الكلي: {u_count}")

    elif "الإشعارات" in text:
        conf = get_conf()
        conf["notifications"] = not conf["notifications"]
        with open("settings.json", "w") as f: json.dump(conf, f)
        bot.send_message(uid, "⚙️ تم تحديث حالة الإشعارات.", reply_markup=main_kb(uid))

    elif text == "رجوع 🔙":
        bot.send_message(uid, "🔙 العودة للرئيسية:", reply_markup=main_kb(uid))

# --- توابع التنفيذ المتقدمة ---
def run_bc(message, mode):
    conf = get_conf()
    with open("users.txt", "r") as f: users = f.read().splitlines()
    sent = 0
    if mode in ["channel", "all"]:
        try: bot.copy_message(conf["channel_id"], message.chat.id, message.message_id); sent += 1
        except: pass
    if mode in ["users", "all"]:
        for u in users:
            try: bot.copy_message(u, message.chat.id, message.message_id); sent += 1
            except: pass
    bot.send_message(message.from_user.id, f"✅ تمت الإذاعة بنجاح ({sent}).", reply_markup=main_kb(message.from_user.id))

def save_file(message):
    fid = message.document.file_id if message.document else (message.video.file_id if message.video else (message.photo[-1].file_id if message.photo else None))
    if fid:
        with open("bot_files.txt", "a") as f: f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم حفظ الملف!", reply_markup=main_kb(message.from_user.id))
    else: bot.send_message(message.chat.id, "❌ فشل، أرسل ملفاً صحيحاً.")

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

def update_subscription(message):
    if "t.me/" in message.text:
        conf = get_conf()
        conf["sub_link"] = message.text
        conf["channel_id"] = "@" + message.text.split("t.me/")[1].split("/")[0]
        with open("settings.json", "w") as f: json.dump(conf, f)
        bot.send_message(message.chat.id, "✅ تم تحديث القناة الإجبارية.")
    else: bot.send_message(message.chat.id, "❌ رابط غير صحيح.")

# --- معالجة الـ Callbacks (الأزرار الشفافة) ---
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
        with open("admins.json", "w") as f: json.dump(ads, f)
        bot.edit_message_text(f"✅ تم حفظ الأدمن `{target}` بنجاح.", call.message.chat.id, call.message.message_id)

    elif data == "get_files":
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        for fid in files:
            try: bot.send_document(uid, fid)
            except: 
                try: bot.send_video(uid, fid)
                except: bot.send_photo(uid, fid)
        bot.answer_callback_query(call.id, "🚀 تفقد خاصك!")

    elif data == "verify_sub":
        if is_subscribed(uid):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_cmd(call.message)
        else: bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()

