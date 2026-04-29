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
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

bot = telebot.TeleBot(TOKEN)

# إنشاء ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "channel_files.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump({}, file)
            else: file.write("")

# ==========================================
# 2. الدالات المساعدة
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

# ==========================================
# 3. واجهات الأزرار (مثل الصور تماماً)
# ==========================================

# لوحة القناة (تفاعل + استلم + تفعيل)
def get_channel_markup(mid, interact=0, receive=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(f"استلم ({receive}) 📩", callback_data=f"rcv_{mid}"),
        types.InlineKeyboardButton(f"تفاعل ({interact}) ❤️", callback_data=f"hit_{mid}")
    )
    markup.add(types.InlineKeyboardButton("🤖 فعّل البوت أولاً", url=f"https://t.me/{BOT_USERNAME}?start=activate"))
    return markup

# زر الملف الفردي المنشور
def get_file_markup(mid):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📩 استلم الملف في الخاص", url=f"https://t.me/{BOT_USERNAME}?start=file_{mid}"))
    return markup

# لوحة تحكم الأدمن في الخاص
def get_admin_panel():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("نشر لوحة التحكم 🚀", "الإحصائيات 📊", "تصفير الملفات 🗑️")
    return markup

# ==========================================
# 4. معالجة الدخول والإشعارات
# ==========================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    fname = message.from_user.first_name
    uname = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    
    users = get_list("users.txt")
    
    # إشعار الدخول الجديد للمطور
    if str(uid) not in users and "activate" not in message.text:
        notification = (f"👤 دخول مستخدم جديد!\n\n"
                        f"👤 الاسم: {fname}\n"
                        f"🆔 الآيدي: `{uid}`\n"
                        f"🔗 اليوزر: {uname}")
        try: bot.send_message(OWNER_ID, notification, parse_mode="Markdown")
        except: pass

    # معالجة استلام ملف معين من رابط القناة
    if "file_" in message.text:
        file_key = message.text.split("_")[1]
        db = load_json("channel_files.json")
        if file_key in db:
            bot.send_document(uid, db[file_key]['file_id'], caption=f"✅ تم استلام ملف: {db[file_key]['name']}")
        else:
            bot.send_message(uid, "❌ هذا الملف انتهت صلاحيته أو تم حذفه.")
        return

    # معالجة زر التفعيل
    if "activate" in message.text:
        if str(uid) not in users:
            with open("users.txt", "a") as f: f.write(f"{uid}\n")
        bot.send_message(uid, "✅ تم تفعيل البوت بنجاح! يمكنك الآن الضغط على (تفاعل) و (استلم) في القناة.")
        return

    # الرد العادي
    if uid == OWNER_ID:
        bot.send_message(uid, "👑 أهلاً بك يا مطور، إليك لوحة التحكم:", reply_markup=get_admin_panel())
    else:
        bot.send_message(uid, "👋 أهلاً بك! أنا بوت الكونفيجات، تابع القناة واستلم ملفاتك.")

# ==========================================
# 5. التنسيق التلقائي للقناة (عند نشر ملف)
# ==========================================

@bot.message_handler(content_types=['document'], func=lambda m: m.chat.type == 'channel')
def channel_file_auto_format(message):
    fid = message.document.file_id
    fname = message.document.file_name
    mid = str(message.message_id)

    # حفظ بيانات الملف
    db = load_json("channel_files.json")
    db[mid] = {"file_id": fid, "name": fname}
    save_json("channel_files.json", db)

    # ذكاء التنسيق (مثل الصورة 1)
    app = "DARK TUNNEL" if ".dark" in fname.lower() else "HTTP INJECTOR" if ".ehi" in fname.lower() else "VPN"
    desc = "كونفيج كسر يوتيوب" if "yt" in fname.lower() else "كونفيج بدون عروض"

    caption = (f"📄 **{fname}**\n\n"
               f"💬 {desc}\n"
               f"📱 خاص بتطبيق: {app}\n"
               f"⏳ المدة: 4:30 ساعات\n"
               f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    
    try:
        bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id, 
                                 caption=caption, reply_markup=get_file_markup(mid), parse_mode="Markdown")
    except: pass

# ==========================================
# 6. منع التكرار في التفاعل والاستلام (الطلب الأساسي)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    data = call.data
    mid = call.message.message_id
    users = get_list("users.txt")

    # حماية: يجب تفعيل البوت أولاً
    if str(uid) not in users:
        bot.answer_callback_query(call.id, "⚠️ يجب تفعيل البوت أولاً (اضغط زر 🤖)!", show_alert=True)
        return

    act = load_json("activity.json")
    post_id = str(mid)
    
    # هيكل البيانات: h_u (مستخدمي التفاعل) | r_u (مستخدمي الاستلام)
    if post_id not in act: act[post_id] = {"h_u": [], "r_u": []}

    # 1. معالجة التفاعل ❤️ (منع التكرار)
    if "hit_" in data:
        if uid not in act[post_id]["h_u"]:
            act[post_id]["h_u"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            bot.edit_message_reply_markup(CHANNEL_ID, mid, 
                                          reply_markup=get_channel_markup(post_id, len(act[post_id]["h_u"]), len(act[post_id]["r_u"])))
        else:
            bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً!", show_alert=True)

    # 2. معالجة الاستلام 📩 (منع التكرار)
    elif "rcv_" in data:
        if uid not in act[post_id]["r_u"]:
            act[post_id]["r_u"].append(uid)
            save_json("activity.json", act)
            bot.answer_callback_query(call.id, "📩 جاري إرسال الملفات في الخاص...")
            bot.edit_message_reply_markup(CHANNEL_ID, mid, 
                                          reply_markup=get_channel_markup(post_id, len(act[post_id]["h_u"]), len(act[post_id]["r_u"])))
            
            # إرسال الملفات العامة المرفوعة
            files = get_list("bot_files.txt")
            if files:
                bot.send_message(uid, "📦 إليك جميع ملفات التحديث الجديد:")
                for f in files:
                    try: bot.send_document(uid, f)
                    except: pass
            else:
                bot.send_message(uid, "⚠️ عذراً، لا توجد ملفات عامة مرفوعة حالياً.")
        else:
            bot.answer_callback_query(call.id, "⚠️ لقد استلمت هذه الملفات مسبقاً!", show_alert=True)

# ==========================================
# 7. أوامر الأدمن
# ==========================================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID)
def admin_logic(message):
    if message.text == "نشر لوحة التحكم 🚀":
        text = ("⚡ **تم تجديد الكونفيجات!**\n\n"
                "📄 عدد الملفات: 4\n"
                "🚀 سرعة عالية | ⏳ محدد المدة\n"
                "__________________________\n\n"
                "📌 **طريقة الاستلام:**\n\n"
                "1️⃣ فعّل البوت بالضغط على 🤖\n"
                "2️⃣ ادعمنا بضغطة ❤️\n"
                "3️⃣ اضغط 📩 لاستلام الملفات\n"
                "__________________________\n\n"
                "⚠️ سارع قبل انتهاء الصلاحية!")
        bot.send_message(CHANNEL_ID, text, parse_mode="Markdown", reply_markup=get_channel_markup("main"))
        bot.send_message(OWNER_ID, "✅ تم نشر لوحة التحكم في القناة.")

    elif message.text == "الإحصائيات 📊":
        users = get_list("users.txt")
        bot.send_message(OWNER_ID, f"📊 عدد المشتركين الذين فعلوا البوت: `{len(users)}`", parse_mode="Markdown")

    elif message.text == "تصفير الملفات 🗑️":
        open("bot_files.txt", "w").close()
        bot.send_message(OWNER_ID, "🗑️ تم مسح سجل الملفات العامة.")

# ==========================================
# 8. تشغيل البوت
# ==========================================
if __name__ == "__main__":
    print(f"🔥 البوت @{BOT_USERNAME} يعمل الآن بكل الإصلاحات...")
    bot.infinity_polling()

