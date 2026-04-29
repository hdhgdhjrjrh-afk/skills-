import telebot
from telebot import types
import os, json

# --- الإعدادات ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام الملفات ---
def init_db():
    files = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "{}", 
        "stats.json": json.dumps({"downloads": 0, "likes": 0}),
        "settings.json": json.dumps({"notifications": True, "channel_id": "@Uchiha75", "sub_link": "https://t.me/Uchiha75"})
    }
    for f, c in files.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file: file.write(c)

init_db()

def get_conf():
    with open("settings.json", "r", encoding="utf-8") as f: return json.load(f)

def save_conf(conf):
    with open("settings.json", "w", encoding="utf-8") as f: json.dump(conf, f, indent=4)

def get_stats():
    with open("stats.json", "r", encoding="utf-8") as f: return json.load(f)

def is_subscribed(uid):
    conf = get_conf()
    try:
        status = bot.get_chat_member(conf["channel_id"], uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = json.load(open("admins.json"))
    admin_data = admins.get(str(uid))
    return admin_data.get(perm, False) if admin_data else False

# --- الكيبورد الرئيسي ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_conf()
    n_text = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"): kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"): kb.row("إرسال إذاعة 📣", "الإحصائيات 📊")
    kb.row("إضافة اشتراك 🔗", n_text)
    if has_perm(uid, "can_reset"): kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    if int(uid) == OWNER_ID: kb.row("إضافة أدمن ➕")
    kb.row("إنهاء ✅")
    return kb

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        conf = get_conf()
        mk.add(types.InlineKeyboardButton("اشترك هنا 📢", url=conf["sub_link"]))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="verify_sub"))
        return bot.send_message(uid, "⚠️ يجب الاشتراك أولاً!", reply_markup=mk)

    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        conf = get_conf()
        if conf.get("notifications"):
            try: bot.send_message(OWNER_ID, f"🔔 مستخدم جديد: {message.from_user.first_name}")
            except: pass

    bot.send_message(uid, "💎 لوحة التحكم جاهزة:", reply_markup=main_kb(uid))

# --- فحص عمل الأزرار (Admin Logic) ---
@bot.message_handler(func=lambda m: True)
def admin_logic(message):
    uid, text = message.from_user.id, message.text
    conf = get_conf()

    if text in ["إيقاف الإشعارات ❌", "تفعيل الإشعارات ✅"]:
        conf["notifications"] = not conf["notifications"]
        save_conf(conf)
        bot.send_message(uid, "⚙️ تم تحديث حالة الإشعارات.", reply_markup=main_kb(uid))

    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        st = get_stats()
        bot.send_message(uid, f"📊 **إحصائيات البوت:**\n\n👥 المشتركين: `{u_count}`\n📩 الاستلام: `{st['downloads']}`\n❤️ التفاعل: `{st['likes']}`", parse_mode="Markdown")

    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w") as f: f.write("")
        bot.send_message(uid, "✅ تم تصفير جميع الملفات.")

    elif text == "تنظيف البيانات 🧹" and has_perm(uid, "can_reset"):
        with open("users.txt", "w") as f: f.write("")
        with open("stats.json", "w") as f: json.dump({"downloads": 0, "likes": 0}, f)
        bot.send_message(uid, "✅ تم تنظيف المستخدمين والإحصائيات.")

    elif text == "نشر تلقائي 📣" and has_perm(uid, "can_post"):
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.send_message(uid, "❌ لا توجد ملفات!")
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        bot.send_message(conf["channel_id"], f"⚡ **تم تجديد الملفات!**\n📁 عددها: {len(files)}\n\nاستخدم الأزرار أدناه 👇", reply_markup=mk, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_add_files"):
        m = bot.send_message(uid, "📤 أرسل الملف الآن:")
        bot.register_next_step_handler(m, save_file)

# --- Callbacks ---
@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    uid, data = call.from_user.id, call.data
    
    if data == "verify_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ تم التحقق!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(uid, "💎 أهلاً بك مرة أخرى!", reply_markup=main_kb(uid))
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

    elif data == "get_files":
        with open("stats.json", "r") as f: st = json.load(f)
        st["downloads"] += 1
        with open("stats.json", "w") as f: json.dump(st, f)
        bot.answer_callback_query(call.id, "🚀 تفقد خاصك!")
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        for fid in files:
            try: bot.send_document(uid, fid)
            except: pass

    elif data == "hit_like":
        with open("stats.json", "r") as f: st = json.load(f)
        st["likes"] += 1
        with open("stats.json", "w") as f: json.dump(st, f)
        bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")

def save_file(message):
    fid = message.document.file_id if message.document else (message.video.file_id if message.video else None)
    if fid:
        with open("bot_files.txt", "a") as f: f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم الحفظ!", reply_markup=main_kb(message.from_user.id))

if __name__ == "__main__":
    bot.infinity_polling()

