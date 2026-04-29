import telebot
from telebot import types
import os, json

# --- الإعدادات (تأكد من صحتها) ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"
MAX_USERS = 15

bot = telebot.TeleBot(TOKEN)

# --- نظام إدارة البيانات ---
def load_json(file, default):
    if not os.path.exists(file): return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(file):
    if not os.path.exists(file): return []
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_list(file, data):
    with open(file, "w", encoding="utf-8") as f:
        f.write("\n".join(map(str, data)))

# --- فحص الصلاحيات والاشتراك ---
def is_admin(uid):
    admins = load_json("admins.json", [])
    return uid == OWNER_ID or str(uid) in map(str, admins)

def is_subscribed(uid):
    try:
        status = bot.get_chat_member(CHANNEL_ID, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- لوحات التحكم ---
def admin_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    set_db = load_json("settings.json", {"notifications": True})
    notif_btn = "إيقاف الإشعارات ❌" if set_db.get("notifications") else "تفعيل الإشعارات ✅"
    kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    kb.row("إذاعة للمستخدمين 👥", "إذاعة قناة 📢")
    kb.row("الإحصائيات 📊", notif_btn)
    kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    kb.row("إضافة أدمن ➕", "إنهاء ✅")
    return kb

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
    # 1. الاشتراك الإجباري
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("إشترك هنا أولاً ⚡", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        mk.add(types.InlineKeyboardButton("تحقق ✅", callback_data="check_sub"))
        return bot.send_message(uid, "⚠️ يجب أن تشترك بالقناة لتستخدم البوت!", reply_markup=mk)

    # 2. تسجيل المستخدم والحد الأقصى
    users = get_list("users.txt")
    if str(uid) not in users:
        if len(users) >= MAX_USERS:
            return bot.send_message(uid, f"❌ الحد الأقصى للمشتركين {MAX_USERS} مستخدم فقط.")
        users.append(str(uid))
        save_list("users.txt", users)
        
        # إشعار دخول مستخدم جديد
        set_db = load_json("settings.json", {"notifications": True})
        if set_db.get("notifications"):
            bot.send_message(OWNER_ID, f"🔔 مستخدم جديد:\nالاسم: {message.from_user.first_name}\nالآيدي: `{uid}`")

    # 3. عرض اللوحة
    if is_admin(uid):
        bot.send_message(uid, "👑 أهلاً بك في لوحة التحكم:", reply_markup=admin_kb())
    else:
        bot.send_message(uid, "👋 أهلاً بك! البوت جاهز للاستخدام.")

# --- منطق الأزرار ---
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_panel(message):
    uid, text = message.from_user.id, message.text

    if text == "الإحصائيات 📊":
        u = len(get_list("users.txt"))
        act = load_json("activity.json", {})
        h = sum(len(v.get("h", [])) for v in act.values())
        r = sum(len(v.get("r", [])) for v in act.values())
        bot.send_message(uid, f"📊 **الإحصائيات:**\n👥 مستخدمين: {u}/{MAX_USERS}\n❤️ تفاعلات: {h}\n📩 استلام: {r}")

    elif "الإشعارات" in text:
        set_db = load_json("settings.json", {"notifications": True})
        set_db["notifications"] = not set_db["notifications"]
        save_json("settings.json", set_db)
        bot.send_message(uid, "⚙️ تم تحديث الإعدادات.", reply_markup=admin_kb())

    elif text == "إذاعة قناة 📢":
        m = bot.send_message(uid, "📢 أرسل ما تريد نشره في القناة:")
        bot.register_next_step_handler(m, lambda msg: bot.copy_message(CHANNEL_ID, msg.chat.id, msg.message_id))

    elif text == "إضافة أدمن ➕":
        m = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, save_admin)

    elif text == "تنظيف البيانات 🧹":
        save_json("activity.json", {})
        bot.send_message(uid, "✅ تم تنظيف سجل التفاعلات.")

    elif text == "تصفير الملفات 🗑️":
        save_list("bot_files.txt", [])
        bot.send_message(uid, "🗑️ تم مسح جميع الملفات.")

    elif text == "نشر تلقائي 📣":
        f_count = len(get_list("bot_files.txt"))
        mk = types.InlineKeyboardMarkup()
        mk.row(types.InlineKeyboardButton("استلم 📩", callback_data="rcv"),
               types.InlineKeyboardButton("تفاعل ❤️", callback_data="hit"))
        bot.send_message(CHANNEL_ID, f"⚡ **تحديث جديد!**\n📄 ملفات: {f_count}\n🚀 سرعة فائقة", reply_markup=mk)
        bot.send_message(uid, "✅ تم النشر في القناة.")

def save_admin(message):
    if message.text.isdigit():
        ad = load_json("admins.json", [])
        ad.append(message.text)
        save_json("admins.json", list(set(ad)))
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن.")
    else: bot.send_message(message.from_user.id, "❌ خطأ في الآيدي.")

# --- التفاعلات (Inline) ---
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid, data = str(call.from_user.id), call.data
    
    if data == "check_sub":
        if is_subscribed(call.from_user.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else: bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)
        return

    # تفاعلات القناة (استلم / تفاعل)
    act = load_json("activity.json", {})
    mid = str(call.message.message_id)
    if mid not in act: act[mid] = {"h": [], "r": []}

    if data == "hit":
        if uid not in act[mid]["h"]:
            act[mid]["h"].append(uid); save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً!")
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت سابقاً!")

    elif data == "rcv":
        files = get_list("bot_files.txt")
        if not files: return bot.answer_callback_query(call.id, "❌ لا توجد ملفات!")
        for f in files: bot.send_document(call.from_user.id, f)
        if uid not in act[mid]["r"]: 
            act[mid]["r"].append(uid); save_json("activity.json", act)
        bot.answer_callback_query(call.id, "📩 تم الإرسال للخاص.")

if __name__ == "__main__":
    bot.infinity_polling()

