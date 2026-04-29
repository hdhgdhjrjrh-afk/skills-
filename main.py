import telebot
from telebot import types
import os
import json

# --- 1. الإعدادات ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# --- 2. نظام البيانات المطور ---
def get_data(file):
    if not os.path.exists(file):
        if file.endswith(".json"): return {}
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            if file.endswith(".json"): return json.load(f)
            return [line.strip() for line in f if line.strip()]
    except: return {} if file.endswith(".json") else []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        if file.endswith(".json"): json.dump(data, f, indent=4, ensure_ascii=False)
        else: f.write("\n".join(map(str, data)) + "\n")

# --- 3. لوحة التحكم (مطابقة للصورة تماماً) ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = get_data("settings.json")
    notif = "إيقاف الإشعارات ❌" if settings.get("notifications") else "تفعيل الإشعارات ✅"
    
    # الأزرار كما في الصورة
    markup.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    markup.row("إذاعة للمستخدمين 👥", "الإحصائيات 📊")
    markup.row(notif, "تنظيف البيانات 🧹")
    markup.row("تصفير الملفات 🗑️", "إنهاء ✅")
    markup.add("إضافة أدمن ➕") # الزر السفلي في الصورة
    return markup

# --- 4. معالجة الأوامر والرسائل ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    users = get_data("users.txt")
    
    if str(uid) not in map(str, users):
        if "activate" in (message.text or ""):
            users.append(str(uid))
            save_data("users.txt", users)
            bot.send_message(uid, "✅ تم تفعيل البوت بنجاح!")
        else:
            settings = get_data("settings.json")
            if settings.get("notifications"):
                uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
                bot.send_message(OWNER_ID, f"👤 دخول مستخدم جديد!\n\n👤 الاسم: {message.from_user.first_name}\n🆔 الآيدي: {uid}\n🔗 اليوزر: {uname}")

    if uid == OWNER_ID or str(uid) in map(str, get_data("admins.json")):
        bot.send_message(uid, "👑 أهلاً بك في لوحة التحكم:", reply_markup=admin_keyboard())
    else:
        bot.send_message(uid, "👋 أهلاً بك! يمكنك الاستلام من القناة.")

@bot.message_handler(func=lambda m: True)
def handle_admin_buttons(message):
    uid, text = message.from_user.id, message.text
    if not (uid == OWNER_ID or str(uid) in map(str, get_data("admins.json"))): return

    if text == "نشر تلقائي 📣":
        count = len(get_data("bot_files.txt"))
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("استلم 📩", callback_data="rcv"), 
                   types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit"))
        markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", url=f"https://t.me/{BOT_USERNAME}?start=activate"))
        bot.send_message(CHANNEL_ID, f"⚡ **تحديث جديد!**\n\n📄 عدد الملفات: {count}\n🚀 سرعة عالية", reply_markup=markup)
        bot.send_message(uid, "✅ تم النشر في القناة.")

    elif text == "الإحصائيات 📊":
        users_count = len(get_data("users.txt"))
        act = get_data("activity.json")
        # حساب المتفاعلين والمستلمين من جميع المنشورات
        total_hits = sum(len(v.get("h", [])) for v in act.values())
        total_rcvs = sum(len(v.get("r", [])) for v in act.values())
        
        stats_msg = (f"📊 **إحصائيات البوت:**\n\n"
                     f"👥 عدد المشتركين: {users_count}\n"
                     f"❤️ عدد المتفاعلين: {total_hits}\n"
                     f"📩 عدد المستلمين: {total_rcvs}")
        bot.send_message(uid, stats_msg)

    elif text == "إذاعة للمستخدمين 👥":
        msg = bot.send_message(uid, "📣 أرسل الرسالة التي تريد إذاعتها لجميع المشتركين:")
        bot.register_next_step_handler(msg, broadcast_to_users)

    elif text == "إضافة ملفات 📤":
        msg = bot.send_message(uid, "📤 أرسل الملفات، ثم اضغط إنهاء ✅", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(msg, upload_process)

    elif "الإشعارات" in text:
        s = get_data("settings.json")
        s["notifications"] = not s["notifications"]
        save_data("settings.json", s)
        bot.send_message(uid, "⚙️ تم التغيير!", reply_markup=admin_keyboard())

# --- 5. دالات الإذاعة والرفع ---
def broadcast_to_users(message):
    users = get_data("users.txt")
    count = 0
    for u in users:
        try:
            bot.copy_message(u, message.chat.id, message.message_id)
            count += 1
        except: pass
    bot.send_message(message.from_user.id, f"✅ تم إرسال الإذاعة إلى {count} مستخدم.", reply_markup=admin_keyboard())

def upload_process(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=admin_keyboard())
        return
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        f = get_data("bot_files.txt")
        f.append(fid)
        save_data("bot_files.txt", f)
        bot.send_message(message.from_user.id, "📥 تم الاستلام!")
    bot.register_next_step_handler(message, upload_process)

# --- 6. التفاعلات الشفافة ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid, mid = str(call.from_user.id), str(call.message.message_id)
    if uid not in get_data("users.txt"):
        return bot.answer_callback_query(call.id, "⚠️ فعّل البوت أولاً!", show_alert=True)
    
    act = get_data("activity.json")
    if mid not in act: act[mid] = {"h": [], "r": []}

    if call.data == "hit":
        if uid not in act[mid]["h"]:
            act[mid]["h"].append(uid)
            save_data("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً!")
        
    elif call.data == "rcv":
        if uid not in act[mid]["r"]: act[mid]["r"].append(uid)
        save_data("activity.json", act)
        for f in get_data("bot_files.txt"): bot.send_document(call.from_user.id, f)
        bot.answer_callback_query(call.id, "📩 تفقد الخاص.")

if __name__ == "__main__":
    bot.infinity_polling()

