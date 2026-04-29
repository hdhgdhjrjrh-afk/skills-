import telebot
from telebot import types
import os
import json
import time

# --- الإعدادات الأساسية ---
TOKEN = "8665176617:AAFngE0bDW_aRpMP-9VIsGuWiSf2NCwqWl8"
OWNER_ID = 7985499470
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "fountainsbot"

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "subs.json", "ban_list.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump([] if "list" in f or "subs" in f else {}, file)
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

def is_banned(user_id):
    bans = load_data("ban_list.json", list)
    return str(user_id) in [str(b) for b in bans]

# --- إنشاء الأزرار ---
def channel_markup(mid, interact_count=0):
    markup = types.InlineKeyboardMarkup()
    url = f"https://t.me/{BOT_USERNAME}?start=get_{mid}"
    markup.row(
        types.InlineKeyboardButton(f"استلم 📩", url=url),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f"hit_{mid}")
    )
    return markup

def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if user_id == OWNER_ID:
        btns = ["إضافة ملفات 📤", "نشر تلقائي 📣", "إذاعة للقناة 📢", "إدارة الحظر 🚫", "الإحصائيات 📊", "حذف الملفات 🗑️", "إنهاء ✅"]
    else:
        btns = ["الإحصائيات 📊", "إنهاء ✅"]
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

# ==========================================
# معالجة الأوامر والوظائف
# ==========================================

@bot.message_handler(func=lambda m: is_banned(m.from_user.id))
def banned_user(message): pass

@bot.message_handler(commands=['start'])
def start_logic(message):
    uid = str(message.from_user.id)
    if uid not in get_list("users.txt"):
        with open("users.txt", "a") as f: f.write(uid + "\n")

    if "get_" in message.text:
        mid = message.text.split("_")[1]
        activity = load_data("activity.json")
        if mid in activity and uid in activity[mid].get("u_interact", []):
            if uid not in activity[mid].get("u_receive", []):
                if "u_receive" not in activity[mid]: activity[mid]["u_receive"] = []
                activity[mid]["u_receive"].append(uid)
                save_data("activity.json", activity)
            
            files = get_list("bot_files.txt")
            if files:
                bot.send_message(uid, "✅ تم التحقق، إليك ملفاتك:")
                for fid in files: bot.send_document(uid, fid)
            else:
                bot.send_message(uid, "❌ السجل فارغ.")
        else:
            bot.send_message(uid, "⚠️ تفاعل ❤️ أولاً في القناة!")
        return

    bot.send_message(uid, "🛠️ أهلاً بك في لوحة التحكم:", reply_markup=get_panel(int(uid)))

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = str(call.from_user.id)
    if call.data.startswith("hit_"):
        mid = call.data.split("_")[1]
        activity = load_data("activity.json")
        if mid not in activity: activity[mid] = {"u_interact": [], "u_receive": []}
        if uid not in activity[mid]["u_interact"]:
            activity[mid]["u_interact"].append(uid)
            save_data("activity.json", activity)
            bot.answer_callback_query(call.id, "❤️ تم تسجيل التفاعل!")
            count = len(activity[mid]["u_interact"])
            try: bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=channel_markup(mid, count))
            except: pass
        else:
            bot.answer_callback_query(call.id, "⚠️ متفاعل بالفعل!", show_alert=True)
    elif call.data == "reset_stats" and int(uid) == OWNER_ID:
        save_data("activity.json", {})
        bot.answer_callback_query(call.id, "✅ تم تصفير الإحصائيات", show_alert=True)
        bot.edit_message_text("♻️ تم تصفير البيانات بنجاح.", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    if uid != OWNER_ID: return

    if message.text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **ملفات جديدة متوفرة!**\n\n📁 العدد: `{f_count}`\n⚠️ تفاعل ❤️ ثم اضغط استلم.", parse_mode="Markdown")
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=channel_markup(str(msg.message_id)))
        bot.send_message(uid, "✅ تم النشر.")

    elif message.text == "إذاعة للقناة 📢":
        msg = bot.send_message(uid, "📣 أرسل ما تريد نشره في القناة الآن:")
        bot.register_next_step_handler(msg, send_channel_broadcast)

    elif message.text == "إضافة ملفات 📤":
        bot.send_message(uid, "📥 أرسل الملفات، ثم اضغط إنهاء ✅", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_upload)

    elif message.text == "الإحصائيات 📊":
        activity = load_data("activity.json")
        inter, receiv = set(), set()
        for mid in activity:
            inter.update(activity[mid].get("u_interact", []))
            receiv.update(activity[mid].get("u_receive", []))
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("♻️ تصفير الإحصائيات", callback_data="reset_stats"))
        msg = (f"📊 **الإحصائيات الدقيقة**\n\n👤 المستخدمين: `{len(get_list('users.txt'))}`\n❤️ المتفاعلون: `{len(inter)}`\n📩 المستلمون: `{len(receiv)}` ")
        bot.send_message(uid, msg, parse_mode="Markdown", reply_markup=kb)

    elif message.text == "إدارة الحظر 🚫":
        bot.send_message(uid, "استخدم `/ban ID` للحظر أو `/unban ID` لفك الحظر.")

    elif message.text == "حذف الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم حذف سجل الملفات.")

    elif message.text == "إنهاء ✅":
        bot.send_message(uid, "🛑 العودة للرئيسية.", reply_markup=get_panel(uid))

def send_channel_broadcast(message):
    try:
        bot.copy_message(CHANNEL_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ تم النشر.")
    except: bot.send_message(message.chat.id, "❌ خطأ في النشر.")

def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=get_panel(message.from_user.id))
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 تم الاستلام.")
    bot.register_next_step_handler(message, process_upload)

@bot.message_handler(commands=['ban', 'unban'])
def handle_ban_commands(message):
    if message.from_user.id != OWNER_ID: return
    cmd = message.text.split()
    if len(cmd) < 2: return
    tid = cmd[1]
    bans = load_data("ban_list.json", list)
    if "/ban" in cmd[0]:
        if tid not in bans: bans.append(tid); save_data("ban_list.json", bans)
        bot.send_message(OWNER_ID, f"🚫 تم حظر `{tid}`")
    else:
        if tid in bans: bans.remove(tid); save_data("ban_list.json", bans)
        bot.send_message(OWNER_ID, f"✅ تم فك حظر `{tid}`")

# ==========================================
# رسالة التشغيل (BOT RUNNING)
# ==========================================
print("-" * 30)
print("🔥 BOT IS RUNNING SUCCESSFULLY!")
print(f"🤖 Bot Username: @{BOT_USERNAME}")
print(f"👤 Owner ID: {OWNER_ID}")
print("-" * 30)

bot.infinity_polling()
