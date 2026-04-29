import telebot
from telebot import types
import os
import json
import time

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75" # قناتك
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# إنشاء ملفات النظام إذا لم تكن موجودة
FILES = ["users.txt", "bot_files.txt", "activity.json", "settings.json", "channel_files.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump({}, file)
            else: file.write("")

# ==========================================
# 2. الدالات المساعدة لإدارة البيانات
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
    return user_id == OWNER_ID

# ==========================================
# 3. لوحات التحكم (الواجهات)
# ==========================================

# لوحة تحكم المستخدم في الخاص (مثل الصورة 2)
def get_user_markup(user_id, mid="main", interact=0, receive=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    users = get_list("users.txt")
    
    if str(user_id) not in users:
        markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", callback_data="activate_bot"))
    else:
        markup.row(
            types.InlineKeyboardButton(f"استلم ({receive}) 📩", callback_data=f"rcv_{mid}"),
            types.InlineKeyboardButton(f"تفاعل ({interact}) ❤️", callback_data=f"hit_{mid}")
        )
    return markup

# زر تحويل من القناة إلى الخاص (مثل الصورة 1)
def get_channel_markup(mid):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📩 استلم الملف في الخاص", url=f"https://t.me/{BOT_USERNAME}?start=file_{mid}"))
    return markup

# لوحة الأدمن الرئيسية
def get_admin_panel():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("نشر لوحة التحكم 🚀", "الإحصائيات 📊", "تصفير الملفات 🗑️", "إنهاء ✅")
    return markup

# ==========================================
# 4. معالجة الأوامر والرسائل (إشعارات الدخول)
# ==========================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    fname = message.from_user.first_name
    
    # 1. نظام إشعار الدخول المطور (مثل الصورة الأخيرة)
    users = get_list("users.txt")
    if str(uid) not in users:
        # ملاحظة: لا نسجله هنا، نسجله عند ضغط زر "تفعيل" لضمان التفاعل
        notification = (f"👤 دخول مستخدم جديد!\n\n"
                        f"👤 الاسم: {fname}\n"
                        f"🆔 الآيدي: `{uid}`\n"
                        f"🔗 اليوزر: {uname}")
        try: bot.send_message(OWNER_ID, notification, parse_mode="Markdown")
        except: pass

    # 2. نظام استلام الملفات الفردية عبر الروابط
    if "file_" in message.text:
        file_id_msg = message.text.split("_")[1]
        db = load_json("channel_files.json")
        if file_id_msg in db:
            bot.send_document(uid, db[file_id_msg]['file_id'], caption=f"✅ ملف: {db[file_id_msg]['name']}\n🚀 سرعة عالية آمنة.")
        else:
            bot.send_message(uid, "❌ عذراً، هذا الملف لم يعد متاحاً.")
        return

    # 3. عرض رسالة الترحيب الرئيسية
    welcome_text = (
        "⚡ **تم تجديد الكونفيجات!**\n\n"
        "📄 عدد الملفات: 4\n"
        "🚀 سرعة عالية | ⏳ محدد المدة\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "📌 **طريقة الاستلام:**\n"
        "1️⃣ فعّل البوت بالضغط على 🤖\n"
        "2️⃣ ادعمنا بضغطة ❤️\n"
        "3️⃣ اضغط 📩 لاستلام الملفات"
    )
    bot.send_message(uid, welcome_text, reply_markup=get_user_markup(uid), parse_mode="Markdown")

# ==========================================
# 5. التنسيق التلقائي للقناة (مثل الصورة 1)
# ==========================================

@bot.message_handler(content_types=['document'], func=lambda m: m.chat.type == 'channel')
def auto_format_channel(message):
    fid = message.document.file_id
    fname = message.document.file_name
    mid = str(message.message_id)

    # حفظ البيانات لاسترجاعها في الخاص
    db = load_json("channel_files.json")
    db[mid] = {"file_id": fid, "name": fname}
    save_json("channel_files.json", db)

    # ذكاء اصطناعي بسيط لتحديد نوع الملف
    app = "DARK TUNNEL" if ".dark" in fname.lower() else "HTTP INJECTOR" if ".ehi" in fname.lower() else "VPN"
    desc = "كونفيج كسر يوتيوب" if "yt" in fname.lower() else "كونفيج بدون عروض اوريدو + جيزي"

    caption = (f"📄 **{fname}**\n\n"
               f"💬 {desc}\n"
               f"📱 خاص بتطبيق: {app}\n"
               f"⏳ المدة: 4:30 ساعات\n"
               f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    
    try:
        bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id, 
                                 caption=caption, reply_markup=get_channel_markup(mid), parse_mode="Markdown")
    except: pass

# ==========================================
# 6. معالجة الأزرار الشفافة والتفاعلات
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    uid = call.from_user.id
    data = call.data
    mid = call.message.message_id

    if data == "activate_bot":
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        bot.answer_callback_query(call.id, "✅ تم تفعيل البوت بنجاح!")
        bot.edit_message_reply_markup(call.message.chat.id, mid, reply_markup=get_user_markup(uid))

    elif "hit_" in data:
        msg_ref = data.split("_")[1]
        act = load_json("activity.json")
        item = act.get(msg_ref, {"h": 0, "r": 0, "u": []})
        
        if uid not in item["u"]:
            item["h"] += 1
            item["u"].append(uid)
            act[msg_ref] = item
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            bot.edit_message_reply_markup(call.message.chat.id, mid, reply_markup=get_user_markup(uid, msg_ref, item["h"], item["r"]))
        else:
            bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً!", show_alert=True)

    elif "rcv_" in data:
        msg_ref = data.split("_")[1]
        act = load_json("activity.json")
        item = act.get(msg_ref, {"h": 0, "r": 0, "u": []})
        item["r"] += 1
        act[msg_ref] = item
        save_json("activity.json", act)
        
        bot.answer_callback_query(call.id, "📩 جاري إرسال الملفات المتاحة...")
        bot.edit_message_reply_markup(call.message.chat.id, mid, reply_markup=get_user_markup(uid, msg_ref, item["h"], item["r"]))
        
        # إرسال الملفات العامة المخزنة
        files = get_list("bot_files.txt")
        for f in files:
            try: bot.send_document(uid, f)
            except: pass

# ==========================================
# 7. أوامر الأدمن
# ==========================================

@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_cmds(message):
    if message.text == "نشر لوحة التحكم 🚀":
        bot.send_message(message.chat.id, "✅ تم إرسال لوحة التحكم الجديدة للمستخدمين.")
        # تعيد إرسال رسالة البداية كلوحة تحكم
        handle_start(message)
    
    elif message.text == "الإحصائيات 📊":
        users = get_list("users.txt")
        bot.send_message(message.chat.id, f"📊 **إحصائيات البوت:**\n\n👥 مستخدمين نشطين: `{len(users)}`", parse_mode="Markdown")

    elif message.text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(message.chat.id, "🗑️ تم مسح سجل الملفات العامة.")

# ==========================================
# 8. تشغيل البوت
# ==========================================
if __name__ == "__main__":
    print(f"🔥 البوت @{BOT_USERNAME} يعمل بكامل طاقته...")
    bot.infinity_polling()

