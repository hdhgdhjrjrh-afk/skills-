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

# التأكد من وجود ملفات النظام وتجهيزها
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "ban_list.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump([] if "list" in f else {}, file)
            else: file.write("")

# --- دالات النظام الأساسية ---
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

# --- لوحة تحكم الأدمن (المتقدمة) ---
def get_admin_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # أزرار الإدارة الأساسية
    btn1 = types.KeyboardButton("إضافة ملفات 📤")
    btn2 = types.KeyboardButton("نشر تلقائي 📣")
    btn3 = types.KeyboardButton("إذاعة للقناة 📢")
    btn4 = types.KeyboardButton("إذاعة للمشتركين 👥")
    btn5 = types.KeyboardButton("إدارة الحظر 🚫")
    btn6 = types.KeyboardButton("الإحصائيات 📊")
    btn7 = types.KeyboardButton("حذف الملفات 🗑️")
    btn8 = types.KeyboardButton("إنهاء ✅")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    return markup

# --- زر التفاعل في القناة ---
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

@bot.message_handler(func=lambda m: is_banned(m.from_user.id))
def banned_user(message): pass # تجاهل المحظورين تماماً

@bot.message_handler(commands=['start'])
def start_logic(message):
    uid = str(message.from_user.id)
    # تسجيل المستخدم الجديد
    if uid not in get_list("users.txt"):
        with open("users.txt", "a") as f: f.write(uid + "\n")

    # معالجة رابط "استلم" من القناة
    if "get_" in message.text:
        mid = message.text.split("_")[1]
        activity = load_data("activity.json")
        if mid in activity and uid in activity[mid].get("u_interact", []):
            # تسجيل الاستلام
            if uid not in activity[mid].get("u_receive", []):
                if "u_receive" not in activity[mid]: activity[mid]["u_receive"] = []
                activity[mid]["u_receive"].append(uid)
                save_data("activity.json", activity)
            
            files = get_list("bot_files.txt")
            if files:
                bot.send_message(uid, f"✅ أهلاً {message.from_user.first_name}، إليك ملفاتك:")
                for fid in files: bot.send_document(uid, fid)
            else:
                bot.send_message(uid, "❌ السجل فارغ حالياً.")
        else:
            bot.send_message(uid, "⚠️ يجب التفاعل بـ ❤️ على المنشور أولاً!")
        return

    # إظهار لوحة التحكم للمالك
    if int(uid) == OWNER_ID:
        bot.send_message(uid, "👑 مرحباً بك يا مدير.. تم تفعيل لوحة التحكم:", reply_markup=get_admin_panel(int(uid)))
    else:
        bot.send_message(uid, "👋 أهلاً بك في بوت استلام الملفات.\nاشترك في القناة لكي تصلك الملفات الجديدة.")

# ==========================================
# وظائف لوحة التحكم
# ==========================================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID)
def handle_admin_commands(message):
    uid = message.from_user.id
    text = message.text

    if text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **ملفات جديدة متوفرة!**\n\n📁 العدد: `{f_count}`\n⚠️ تفاعل ❤️ ثم اضغط استلم.", parse_mode="Markdown")
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=channel_markup(str(msg.message_id)))
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    elif text == "إضافة ملفات 📤":
        bot.send_message(uid, "📥 أرسل الملفات الآن، وعند الانتهاء اضغط **إنهاء ✅**", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_upload)

    elif text == "إذاعة للقناة 📢":
        msg = bot.send_message(uid, "📣 أرسل الرسالة التي تريد توجيهها للقناة:")
        bot.register_next_step_handler(msg, channel_broadcast)

    elif text == "إذاعة للمشتركين 👥":
        msg = bot.send_message(uid, "👥 أرسل نص الإذاعة لجميع مستخدمي البوت:")
        bot.register_next_step_handler(msg, users_broadcast)

    elif text == "الإحصائيات 📊":
        activity = load_data("activity.json")
        inter, receiv = set(), set()
        for mid in activity:
            inter.update(activity[mid].get("u_interact", []))
            receiv.update(activity[mid].get("u_receive", []))
        
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("♻️ تصفير البيانات", callback_data="reset_stats"))
        stats = (f"📊 **إحصائيات النظام الشاملة**\n\n"
                 f"👤 المشتركين بالبوت: `{len(get_list('users.txt'))}`\n"
                 f"📂 الملفات المسجلة: `{len(get_list('bot_files.txt'))}`\n"
                 f"❤️ إجمالي المتفاعلين: `{len(inter)}`\n"
                 f"📩 إجمالي المستلمين: `{len(receiv)}` ")
        bot.send_message(uid, stats, parse_mode="Markdown", reply_markup=kb)

    elif text == "إدارة الحظر 🚫":
        bot.send_message(uid, "💡 للحظر: أرسل `/ban ID`\n💡 لفك الحظر: أرسل `/unban ID`")

    elif text == "حذف الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم مسح جميع الملفات من السجل.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🛑 تم الخروج من وضع التحكم.", reply_markup=types.ReplyKeyboardRemove())

# --- دالات المعالجة الخلفية ---
def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم حفظ الملفات.", reply_markup=get_admin_panel(message.from_user.id))
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 استلمت ملفاً جديداً..")
    bot.register_next_step_handler(message, process_upload)

def channel_broadcast(message):
    try:
        bot.copy_message(CHANNEL_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ تم النشر في القناة.")
    except: bot.send_message(message.chat.id, "❌ خطأ في الصلاحيات.")

def users_broadcast(message):
    users = get_list("users.txt")
    count = 0
    bot.send_message(message.chat.id, f"⏳ جاري الإرسال لـ {len(users)} مشترك..")
    for u in users:
        try:
            bot.copy_message(u, message.chat.id, message.message_id)
            count += 1
            time.sleep(0.05) # تجنب الحظر من تلجرام
        except: continue
    bot.send_message(message.chat.id, f"✅ اكتملت الإذاعة لـ {count} شخص.")

# ==========================================
# نظام الـ Callback والحظر
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid = str(call.from_user.id)
    if call.data.startswith("hit_"):
        mid = call.data.split("_")[1]
        activity = load_data("activity.json")
        if mid not in activity: activity[mid] = {"u_interact": [], "u_receive": []}
        if uid not in activity[mid]["u_interact"]:
            activity[mid]["u_interact"].append(uid)
            save_data("activity.json", activity)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            count = len(activity[mid]["u_interact"])
            try: bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=channel_markup(mid, count))
            except: pass
        else: bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً!", show_alert=True)
    elif call.data == "reset_stats" and int(uid) == OWNER_ID:
        save_data("activity.json", {})
        bot.answer_callback_query(call.id, "♻️ تم تصفير البيانات.")

@bot.message_handler(commands=['ban', 'unban'])
def handle_ban(message):
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

# تشغيل البوت
print("-" * 30)
print("🔥 ADMIN PANEL READY & RUNNING")
print("-" * 30)
bot.infinity_polling()
