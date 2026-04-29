import telebot
from telebot import types
import os
import json
import time

# --- الإعدادات الأساسية الجديدة ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 7985499470
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# تجهيز ملفات النظام لضمان الاستقرار
FILES = ["users.txt", "bot_files.txt", "activity.json", "ban_list.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump({} if "activity" in f else [], file)
            else: file.write("")

# --- دالات المساعدة ---
def load_data(filename, default_type=dict):
    try:
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)
    except: return default_type()

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return True

# --- لوحات التحكم ---
def get_admin_panel():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = ["نشر تلقائي 📣", "إضافة ملفات 📤", "إذاعة شاملة 👥", "الإحصائيات 📊", 
            "نسخة احتياطية 📥", "إدارة الحظر 🚫", "تصفير الملفات 🗑️", "إنهاء ✅"]
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def channel_markup(mid, interact_count=0):
    markup = types.InlineKeyboardMarkup()
    url = f"https://t.me/{BOT_USERNAME}?start=get_{mid}"
    markup.row(
        types.InlineKeyboardButton(f"استلم 📩", url=url),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f"hit_{mid}")
    )
    return markup

# ==========================================
# معالجة الأوامر والرسائل
# ==========================================

@bot.message_handler(func=lambda m: str(m.from_user.id) in load_data("ban_list.json", list))
def banned_user(message): pass

@bot.message_handler(commands=['start'])
def start_logic(message):
    uid = str(message.from_user.id)
    uname = message.from_user.first_name
    
    users = get_list("users.txt")
    if uid not in users:
        with open("users.txt", "a") as f: f.write(uid + "\n")
        try: bot.send_message(OWNER_ID, f"👤 **مستخدم جديد دخل للبوت:**\nالاسم: {uname}\nالايدي: `{uid}`", parse_mode="Markdown")
        except: pass

    if "get_" in message.text:
        if not is_subscribed(uid):
            bot.send_message(uid, f"⚠️ يجب الاشتراك في القناة أولاً لتتمكن من الاستلام:\n{CHANNEL_ID}")
            return
        mid = message.text.split("_")[1]
        act = load_data("activity.json")
        if mid in act and uid in act[mid].get("u_interact", []):
            if uid not in act[mid].get("u_receive", []):
                act[mid].setdefault("u_receive", []).append(uid)
                save_data("activity.json", act)
            files = get_list("bot_files.txt")
            if files:
                bot.send_message(uid, "✅ تفضل الملفات المطلوبة:")
                for fid in files: bot.send_document(uid, fid)
            else: bot.send_message(uid, "❌ السجل فارغ حالياً.")
        else: bot.send_message(uid, "⚠️ تفاعل ❤️ أولاً على المنشور في القناة!")
        return

    if int(uid) == OWNER_ID:
        bot.send_message(uid, f"👑 مرحباً يا مدير {uname}.. تم تفعيل لوحة التحكم:", reply_markup=get_admin_panel())
    else:
        bot.send_message(uid, f"👋 أهلاً {uname} في البوت.\nتابع القناة {CHANNEL_ID} للحصول على ملفاتك.")

# ==========================================
# أزرار الإدارة
# ==========================================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID)
def admin_handler(message):
    uid, text = message.from_user.id, message.text

    if text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **تم تحديث الملفات بنجاح!**\n\n📁 العدد المتوفر: `{f_count}`\n⚠️ تفاعل ❤️ أولاً ثم اضغط استلم.", parse_mode="Markdown")
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=channel_markup(str(msg.message_id)))
        bot.send_message(uid, "✅ تم النشر في القناة.")

    elif text == "إضافة ملفات 📤":
        bot.send_message(uid, "📥 أرسل الملفات الآن، ثم اضغط **إنهاء ✅**", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_upload)

    elif text == "إذاعة شاملة 👥":
        msg = bot.send_message(uid, "👥 أرسل رسالة الإذاعة (نص أو وسائط):")
        bot.register_next_step_handler(msg, start_broadcast)

    elif text == "الإحصائيات 📊":
        act = load_data("activity.json")
        inter = len(set(u for m in act for u in act[m].get("u_interact", [])))
        receiv = len(set(u for m in act for u in act[m].get("u_receive", [])))
        msg = (f"📊 **إحصائيات البوت:**\n\n👤 إجمالي المستخدمين: `{len(get_list('users.txt'))}`\n"
               f"📂 الملفات المتوفرة: `{len(get_list('bot_files.txt'))}`\n"
               f"❤️ المتفاعلون الفريدون: `{inter}`\n📩 المستلمون الفريدون: `{receiv}`")
        bot.send_message(uid, msg, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("♻️ تصفير التفاعل", callback_data="reset_stats")))

    elif text == "نسخة احتياطية 📥":
        for f in ["users.txt", "activity.json", "bot_files.txt"]:
            if os.path.exists(f):
                with open(f, "rb") as doc: bot.send_document(uid, doc)

    elif text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم تصفير سجل الملفات بنجاح.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🛑 تم الخروج من وضع التحكم.", reply_markup=types.ReplyKeyboardRemove())

def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ بنجاح.", reply_markup=get_admin_panel())
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 استلمت الملف..")
    bot.register_next_step_handler(message, process_upload)

def start_broadcast(message):
    users = get_list("users.txt")
    success = 0
    for u in users:
        try: bot.copy_message(u, message.chat.id, message.message_id); success += 1; time.sleep(0.05)
        except: continue
    bot.send_message(OWNER_ID, f"✅ اكتملت الإذاعة لـ {success} مستخدم.")

# ==========================================
# معالجة التفاعل والتشغيل
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.from_user.id)
    if call.data.startswith("hit_"):
        mid = call.data.split("_")[1]
        act = load_data("activity.json")
        if mid not in act: act[mid] = {"u_interact": [], "u_receive": []}
        if uid not in act[mid]["u_interact"]:
            act[mid]["u_interact"].append(uid)
            save_data("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=channel_markup(mid, len(act[mid]["u_interact"])))
        else: bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً!", show_alert=True)
    elif call.data == "reset_stats" and int(uid) == OWNER_ID:
        save_data("activity.json", {})
        bot.answer_callback_query(call.id, "♻️ تم تصفير إحصائيات التفاعل.")

if __name__ == "__main__":
    print("-" * 30 + f"\n🚀 BOT @{BOT_USERNAME} IS NOW ONLINE\n" + "-" * 30)
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True, interval=0, timeout=25)

