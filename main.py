import telebot
from telebot import types
import os
import json

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75"  # قناتك التي يجب الاشتراك بها
BOT_USERNAME = "gudurjbot"
MAX_USERS = 15            # الحد الأقصى للمشتركين

bot = telebot.TeleBot(TOKEN)

# ==========================================
# 2. إدارة البيانات والملفات
# ==========================================
def get_data(file):
    if not os.path.exists(file):
        return {} if file.endswith(".json") else []
    try:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return {} if file.endswith(".json") else []
            return json.loads(content) if file.endswith(".json") else content.splitlines()
    except: return {} if file.endswith(".json") else []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        if file.endswith(".json"): json.dump(data, f, indent=4, ensure_ascii=False)
        else: f.write("\n".join(map(str, data)) + "\n")

# التحقق من الاشتراك الإجباري
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def is_admin(uid):
    if int(uid) == OWNER_ID: return True
    admins = get_data("admins.json")
    return str(uid) in map(str, admins) if isinstance(admins, list) else False

# ==========================================
# 3. لوحات التحكم (UI)
# ==========================================
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = get_data("settings.json")
    if not settings: settings = {"notifications": True}
    notif = "إيقاف الإشعارات ❌" if settings.get("notifications") else "تفعيل الإشعارات ✅"
    
    markup.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    markup.row("إذاعة للمستخدمين 👥", "إذاعة قناة 📢")
    markup.row("الإحصائيات 📊", notif)
    markup.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    markup.row("إضافة أدمن ➕", "إنهاء ✅")
    return markup

def channel_markup(mid, h=0, r=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(f"استلم ({r}) 📩", callback_data=f"rcv_{mid}"),
               types.InlineKeyboardButton(f"تفاعل ({h}) ❤️", callback_data=f"hit_{mid}"))
    markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", url=f"https://t.me/{BOT_USERNAME}?start=activate"))
    return markup

# ==========================================
# 4. منطق الدخول والاشتراك
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    users = get_data("users.txt")

    # التحقق من الاشتراك الإجباري
    if not is_subscribed(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك في القناة أولاً 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        markup.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub"))
        return bot.send_message(uid, "⚠️ لن يعمل البوت حتى تشترك في القناة!", reply_markup=markup)

    # التحقق من حد الـ 15 مستخدم
    if str(uid) not in map(str, users):
        if len(users) >= MAX_USERS:
            return bot.send_message(uid, f"❌ عذراً، اكتمل عدد المشتركين المسموح بهم ({MAX_USERS}).")
        users.append(str(uid))
        save_data("users.txt", users)
        # إشعار المطور
        settings = get_data("settings.json")
        if settings.get("notifications", True):
            uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
            bot.send_message(OWNER_ID, f"👤 مستخدم جديد!\nالاسم: {message.from_user.first_name}\nالآيدي: {uid}\nاليوزر: {uname}")

    if is_admin(uid):
        bot.send_message(uid, "👑 لوحة التحكم الشاملة:", reply_markup=admin_keyboard())
    else:
        bot.send_message(uid, "👋 أهلاً بك! يمكنك الآن استخدام البوت والاستلام من القناة.")

# ==========================================
# 5. معالجة أزرار الأدمن
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_logic(message):
    uid, text = message.from_user.id, message.text

    if text == "نشر تلقائي 📣":
        count = len(get_data("bot_files.txt"))
        bot.send_message(CHANNEL_ID, f"⚡ **تحديث جديد!**\n\n📄 عدد الملفات: {count}\n🚀 سرعة عالية", reply_markup=channel_markup("main"), parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    elif text == "إحصائيات 📊":
        users = len(get_data("users.txt"))
        act = get_data("activity.json")
        h = sum(len(v.get("h", [])) for v in act.values()) if isinstance(act, dict) else 0
        r = sum(len(v.get("r", [])) for v in act.values()) if isinstance(act, dict) else 0
        bot.send_message(uid, f"📊 **الإحصائيات:**\n👤 مشتركين: {users}/{MAX_USERS}\n❤️ تفاعلات: {h}\n📩 استلام: {r}")

    elif text == "إذاعة قناة 📢":
        msg = bot.send_message(uid, "📢 أرسل ما تريد نشره في القناة:")
        bot.register_next_step_handler(msg, lambda m: bot.copy_message(CHANNEL_ID, m.chat.id, m.message_id))

    elif text == "إذاعة للمستخدمين 👥":
        msg = bot.send_message(uid, "👥 أرسل رسالة الإذاعة للخاص:")
        bot.register_next_step_handler(msg, broadcast_users)

    elif text == "إضافة ملفات 📤":
        msg = bot.send_message(uid, "📤 أرسل الملفات، ثم اضغط إنهاء ✅", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(msg, upload_files)

    elif text == "تصفير الملفات 🗑️":
        save_data("bot_files.txt", [])
        bot.send_message(uid, "🗑️ تم تصفير الملفات.")

    elif text == "إضافة أدمن ➕":
        msg = bot.send_message(uid, "🆔 أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(msg, add_admin_step)

# ==========================================
# 6. وظائف إضافية
# ==========================================
def broadcast_users(message):
    users = get_data("users.txt")
    sent = 0
    for u in users:
        try: bot.copy_message(u, message.chat.id, message.message_id); sent += 1
        except: pass
    bot.send_message(message.from_user.id, f"✅ تم الإرسال إلى {sent} مستخدم.")

def add_admin_step(message):
    if message.text.isdigit():
        admins = get_data("admins.json")
        if not isinstance(admins, list): admins = []
        admins.append(message.text); save_data("admins.json", list(set(admins)))
        bot.send_message(message.from_user.id, "✅ تم إضافة الأدمن.")
    else: bot.send_message(message.from_user.id, "❌ خطأ في الآيدي.")

def upload_files(message):
    if message.text == "إنهاء ✅":
        return bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=admin_keyboard())
    fid = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    if fid:
        files = get_data("bot_files.txt")
        files.append(fid); save_data("bot_files.txt", files)
        bot.send_message(message.from_user.id, "📥 تم الاستلام!")
    bot.register_next_step_handler(message, upload_files)

# ==========================================
# 7. التفاعلات (Inline Buttons)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    uid, mid, data = str(call.from_user.id), str(call.message.message_id), call.data
    
    if data == "check_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ شكراً لاشتراكك! أرسل /start")
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else: bot.answer_callback_query(call.id, "❌ ما زلت غير مشترك!", show_alert=True)
        return

    if uid not in map(str, get_data("users.txt")):
        return bot.answer_callback_query(call.id, "⚠️ سجل في البوت أولاً!", show_alert=True)

    act = get_data("activity.json")
    if mid not in act: act[mid] = {"h": [], "r": []}

    if "hit_" in data:
        if uid not in act[mid]["h"]:
            act[mid]["h"].append(uid); save_data("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً!"); update_msg(call)
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً!")

    elif "rcv_" in data:
        if uid not in act[mid]["r"]: act[mid]["r"].append(uid); save_data("activity.json", act)
        for f in get_data("bot_files.txt"):
            try: bot.send_document(uid, f)
            except: pass
        bot.answer_callback_query(call.id, "📩 تفقد الخاص."); update_msg(call)

def update_msg(call):
    mid = str(call.message.message_id)
    act = get_data("activity.json")
    bot.edit_message_reply_markup(call.message.chat.id, int(mid), 
                                  reply_markup=channel_markup(mid, len(act[mid]["h"]), len(act[mid]["r"])))

if __name__ == "__main__":
    bot.infinity_polling()

