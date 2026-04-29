import telebot
from telebot import types
import os, json

# --- الإعدادات الأساسية ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام قاعدة البيانات المحمي ---
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

# --- فحص الصلاحيات ---
def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_db("admins.json")
    return admins.get(str(uid), {}).get(perm, False)

# --- الكيبوردات (Bot Running UI) ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    n_text = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"): kb.row("نشر في القناة 📣")
    if has_perm(uid, "can_add_files"): kb.insert("إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"): kb.row("إرسال إذاعة 📣")
    kb.insert("الإحصائيات 📊")
    
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
    
    kb.row(n_text)
    if has_perm(uid, "can_reset"): kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    return kb

def broadcast_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.row("إذاعة قناة 📢", "إذاعة مستخدمين 👥")
    kb.row("إذاعة الجميع 🌐", "رجوع 🔙")
    return kb

# --- محرك الأوامر والراوتر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
    bot.send_message(uid, "🚀 **Bot Running System:** جاهز.\n💎 لوحة التحكم:", reply_markup=main_kb(uid))

@bot.message_handler(func=lambda m: True)
def bot_router(message):
    uid, text = message.from_user.id, message.text

    # 1. نظام إضافة أدمن (للمالك فقط)
    if text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, process_admin_id)

    # 2. نظام الإذاعة الثلاثية
    elif text == "إرسال إذاعة 📣" and has_perm(uid, "can_broadcast"):
        bot.send_message(uid, "🎯 اختر نوع الإذاعة:", reply_markup=broadcast_kb())
    
    elif text in ["إذاعة قناة 📢", "إذاعة مستخدمين 👥", "إذاعة الجميع 🌐"]:
        mode = "channel" if "قناة" in text else ("users" if "مستخدمين" in text else "all")
        m = bot.send_message(uid, f"💬 أرسل محتوى {text}:")
        bot.register_next_step_handler(m, lambda msg: exec_bc(msg, mode))

    # 3. نظام النشر (التصميم المعتمد)
    elif text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        if not files: return bot.send_message(uid, "❌ لا توجد ملفات!")
        conf = get_db("settings.json")
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(types.InlineKeyboardButton("استلم الملفات 📩", callback_data="get_files"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit_like"))
        caption = f"⚡ **تم تجديد الملفات!**\n📁 عددها: `{len(files)}`"
        bot.send_message(conf["channel_id"], caption, reply_markup=mk, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    # 4. إضافة ملفات
    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_add_files"):
        m = bot.send_message(uid, "📤 أرسل المرفق الآن:")
        bot.register_next_step_handler(m, save_file_logic)

    # 5. تنظيف وتصفير
    elif text == "تنظيف البيانات 🧹" and has_perm(uid, "can_reset"):
        with open("users.txt", "w") as f: f.truncate(0)
        save_db("stats.json", {"downloads": 0, "likes": 0})
        bot.send_message(uid, "✅ تم تنظيف كافة البيانات.")

    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w") as f: f.truncate(0)
        bot.send_message(uid, "✅ تم تصفير الملفات.")

    elif text == "رجوع 🔙":
        bot.send_message(uid, "🔙 القائمة الرئيسية:", reply_markup=main_kb(uid))

# --- وظائف التنفيذ (Logic) ---

def process_admin_id(message):
    target = message.text
    if not target.isdigit(): return bot.send_message(message.chat.id, "❌ آيدي خاطئ.")
    # عرض أزرار الصلاحيات للحفظ
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("💾 تفعيل بكامل الصلاحيات", callback_data=f"save_adm_{target}"))
    bot.send_message(message.chat.id, f"⚙️ تأكيد إضافة الأدمن `{target}`؟", reply_markup=mk)

def save_file_logic(message):
    fid = message.document.file_id if message.document else (
          message.video.file_id if message.video else (
          message.photo[-1].file_id if message.photo else None))
    if fid:
        with open("bot_files.txt", "a") as f: f.write(f"{fid}\n")
        bot.send_message(message.chat.id, "✅ تم حفظ الملف.", reply_markup=main_kb(message.from_user.id))

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
    bot.send_message(message.chat.id, f"✅ اكتملت الإذاعة: {sent}", reply_markup=main_kb(message.from_user.id))

# --- Callbacks ---
@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    uid, data = call.from_user.id, call.data
    if data.startswith("save_adm_"):
        target = data.split("_")[2]
        ads = get_db("admins.json")
        ads[target] = {"can_post": True, "can_broadcast": True, "can_add_files": True, "can_reset": False}
        save_db("admins.json", ads)
        bot.edit_message_text(f"✅ تم تفعيل الأدمن `{target}`.", call.message.chat.id, call.message.message_id)
    
    elif data == "get_files":
        st = get_db("stats.json"); st["downloads"] += 1; save_db("stats.json", st)
        with open("bot_files.txt", "r") as f: files = f.read().splitlines()
        for fid in files:
            try: bot.send_document(uid, fid)
            except: pass
    
    elif data == "hit_like":
        st = get_db("stats.json"); st["likes"] += 1; save_db("stats.json", st)
        bot.answer_callback_query(call.id, "❤️ شكراً!")

if __name__ == "__main__":
    bot.infinity_polling()
