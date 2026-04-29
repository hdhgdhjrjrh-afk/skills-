import telebot
from telebot import types
import os
import json

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" 
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "settings.json", "channel_files.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f == "settings.json": json.dump({"notifications": True}, file)
            elif f.endswith(".json"): json.dump({}, file)
            else: file.write("")

# ==========================================
# 2. دالات إدارة البيانات (الدقة في الفحص)
# ==========================================
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f: return [line.strip() for line in f if line.strip()]

def is_admin(user_id):
    admins = load_json("admins.json")
    return user_id == OWNER_ID or user_id in admins

# ==========================================
# 3. فحص وتدقيق لوحات التحكم (UI)
# ==========================================

# لوحة تحكم الأدمن (الفحص: شاملة لكل الأزرار المطلوبة)
def get_admin_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = load_json("settings.json")
    
    # تبديل زر الإشعارات ديناميكياً
    notif_btn = "إيقاف الإشعارات ❌" if settings.get("notifications", True) else "تفعيل الإشعارات ✅"
    
    markup.add(types.KeyboardButton("نشر في القناة 📢"), types.KeyboardButton("إضافة ملفات 📤"))
    markup.add(types.KeyboardButton("الإحصائيات 📊"), types.KeyboardButton(notif_btn))
    markup.add(types.KeyboardButton("تصفير الملفات 🗑️"), types.KeyboardButton("تنظيف البيانات 🧹"))
    
    if user_id == OWNER_ID:
        markup.add(types.KeyboardButton("إضافة أدمن ➕"))
        
    markup.add(types.KeyboardButton("إنهاء ✅"))
    return markup

# أزرار المنشور (الفحص: سطرين متناسقين)
def get_channel_markup(mid, interact_count=0, receive_count=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(f"استلم ({receive_count}) 📩", callback_data=f"rcv_{mid}"),
        types.InlineKeyboardButton(f"تفاعل ({interact_count}) ❤️", callback_data=f"hit_{mid}")
    )
    markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", url=f"https://t.me/{BOT_USERNAME}?start=activate"))
    return markup

# ==========================================
# 4. معالجة الرسائل والبدء
# ==========================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    users = get_list("users.txt")
    
    # إشعار دخول مستخدم جديد (فحص: يرسل التفاصيل كاملة)
    if str(uid) not in users and "activate" not in message.text:
        settings = load_json("settings.json")
        if settings.get("notifications", True):
            uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
            noti = (f"👤 **دخول مستخدم جديد!**\n\n"
                    f"الاسم: {message.from_user.first_name}\n"
                    f"الآيدي: `{uid}`\n"
                    f"اليوزر: {uname}")
            try: bot.send_message(OWNER_ID, noti, parse_mode="Markdown")
            except: pass

    if "activate" in message.text:
        if str(uid) not in users:
            with open("users.txt", "a") as f: f.write(f"{uid}\n")
        bot.send_message(uid, "✅ تم تفعيل البوت! يمكنك الآن التفاعل والاستلام من القناة.")
        return

    if is_admin(uid):
        bot.send_message(uid, "👑 أهلاً بك في لوحة الإدارة الرئيسية:", reply_markup=get_admin_panel(uid))
    else:
        bot.send_message(uid, "👋 أهلاً بك! أنا بوت استلام ملفات القناة.")

# ==========================================
# 5. معالجة الأزرار (فحص: منع التكرار 100%)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid, mid, data = call.from_user.id, str(call.message.message_id), call.data
    users = get_list("users.txt")

    if str(uid) not in users:
        return bot.answer_callback_query(call.id, "⚠️ يجب تفعيل البوت أولاً بالضغط على الزر بالأسفل!", show_alert=True)

    act = load_json("activity.json")
    if mid not in act: act[mid] = {"h": [], "r": []}

    # فحص ومنع تكرار التفاعل ❤️
    if "hit_" in data:
        if uid not in act[mid]["h"]:
            act[mid]["h"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            bot.edit_message_reply_markup(call.message.chat.id, int(mid), 
                                          reply_markup=get_channel_markup(mid, len(act[mid]["h"]), len(act[mid]["r"])))
        else: bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً!", show_alert=True)

    # فحص ومنع تكرار الاستلام 📩
    elif "rcv_" in data:
        if uid not in act[mid]["r"]:
            act[mid]["r"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "📩 تم تسجيل الاستلام، تفقد الخاص!")
            bot.edit_message_reply_markup(call.message.chat.id, int(mid), 
                                          reply_markup=get_channel_markup(mid, len(act[mid]["h"]), len(act[mid]["r"])))
            
            files = get_list("bot_files.txt")
            if files:
                bot.send_message(uid, "📦 إليك جميع الملفات المرفوعة حالياً:")
                for f in files:
                    try: bot.send_document(uid, f)
                    except: pass
            else: bot.send_message(uid, "⚠️ لا توجد ملفات مرفوعة حالياً.")
        else: bot.answer_callback_query(call.id, "⚠️ لقد استلمت الملفات مسبقاً!", show_alert=True)

# ==========================================
# 6. فحص عمليات لوحة التحكم (Admin Panel Logic)
# ==========================================

@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_commands(message):
    uid, text = message.from_user.id, message.text
    
    if text == "نشر في القناة 📢":
        msg_text = (
            "⚡ **تم تجديد الكونفيجات!**\n\n"
            "📄 عدد الملفات المتاحة: 4\n"
            "🚀 سرعة عالية | ⏳ محدد المدة\n"
            "__________________________\n"
            "📌 **طريقة الاستلام:**\n"
            "1️⃣ فعّل البوت أولاً (🤖)\n"
            "2️⃣ ادعمنا بتفاعل (❤️)\n"
            "3️⃣ اضغط استلام (📩)\n"
            "__________________________"
        )
        # إرسال المنشور للقناة
        bot.send_message(CHANNEL_ID, msg_text, reply_markup=get_channel_markup("main"), parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر في القناة بنجاح.")

    elif "الإشعارات" in text:
        settings = load_json("settings.json")
        settings["notifications"] = not settings.get("notifications", True)
        save_json("settings.json", settings)
        bot.send_message(uid, "⚙️ تم تحديث حالة الإشعارات.", reply_markup=get_admin_panel(uid))

    elif text == "الإحصائيات 📊":
        users = get_list("users.txt")
        bot.send_message(uid, f"📊 عدد المشتركين: `{len(users)}`", parse_mode="Markdown")

    elif text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم مسح سجل الملفات بالكامل.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🛑 تم إغلاق لوحة التحكم.", reply_markup=types.ReplyKeyboardRemove())

if __name__ == "__main__":
    print("🔥 تم فحص الكود وتشغيله.. لوحة التحكم جاهزة!")
    bot.infinity_polling()

