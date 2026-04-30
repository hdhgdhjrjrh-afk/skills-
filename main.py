# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (PROFESSIONAL VERSION) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🛡️ نظام متطور: منع التكرار + النشر التفاعلي + إدارة كاملة
# =========================================================================

import telebot
import os
import json
import time
from telebot import types

# --- [ 1. الإعدادات الأساسية ] ---

# توكن البوت الرسمي
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
# معرف المطور (أنت)
DEVELOPER_ID = 8611300267 
# معرف القناة الرسمية (يجب أن يكون البوت مشرفاً فيها)
OFFICIAL_CHANNEL_ID = "@Uchiha75"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# --- [ 2. محرك إدارة البيانات (JSON) ] ---

def load_database(file_name, default_data):
    """تحميل البيانات من ملف JSON أو إنشاء ملف جديد إذا لم يوجد"""
    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_data

def save_database(file_name, data_object):
    """حفظ البيانات في ملف JSON لضمان عدم ضياعها"""
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data_object, f, indent=4, ensure_ascii=False)

# تهيئة ملف الإحصائيات مع قوائم منع التكرار
# voted_users: للأشخاص الذين ضغطوا 'تفاعل'
# received_users: للأشخاص الذين ضغطوا 'استلام'
stats_initial = {
    "likes_count": 182, 
    "receives_count": 158,
    "voted_users": [], 
    "received_users": []
}
stats_db = load_database("stats.json", stats_initial)

# تهيئة ملف الأدمنية
admins_initial = {
    str(DEVELOPER_ID): {
        "name": "SELVA ZOLDEK",
        "perms": ["upload", "publish", "stats", "broadcast"]
    }
}
admins_db = load_database("admins.json", admins_initial)

# --- [ 3. بناء لوحات المفاتيح (Keyboards) ] ---

def get_inline_post_keyboard():
    """بناء الأزرار التي تظهر تحت المنشور في القناة"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # زر الاستلام مع العداد الحالي
    btn_receive = types.InlineKeyboardButton(
        f"استلم ({stats_db['receives_count']}) 📩", 
        callback_data="action_receive"
    )
    
    # زر التفاعل مع العداد الحالي
    btn_react = types.InlineKeyboardButton(
        f"تفاعل ({stats_db['likes_count']}) ❤️", 
        callback_data="action_like"
    )
    
    # زر تفعيل البوت (يأخذ المستخدم لشات البوت)
    me = bot.get_me()
    btn_activate = types.InlineKeyboardButton(
        "🤖 فعّل البوت أولاً", 
        url=f"https://t.me/{me.username}?start=welcome"
    )
    
    markup.add(btn_receive, btn_react)
    markup.add(btn_activate)
    return markup

def get_admin_reply_keyboard():
    """القائمة الرئيسية للأدمن"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("نشر في القناة 📣", "إضافة ملفات 📤")
    markup.add("الإحصائيات 📊", "قسم الإذاعة 📡")
    markup.add("🔙 العودة للمنزل")
    return markup

# --- [ 4. معالجة الأوامر الرئيسية ] ---

@bot.message_handler(commands=['start'])
def welcome_user(message):
    uid = message.from_user.id
    
    # تسجيل المستخدم في ملف نصي للإذاعة
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()
    
    with open("users.txt", "r+") as f:
        content = f.read()
        if str(uid) not in content:
            f.write(f"{uid}\n")

    welcome_text = "⚡ أهلاً بك في نظام Uchiha Dz\nبوت إدارة ونشر الملفات المتطور."
    
    # إظهار لوحة التحكم إذا كان المستخدم أدمن
    if str(uid) in admins_db or uid == DEVELOPER_ID:
        bot.send_message(uid, welcome_text, reply_markup=get_admin_reply_keyboard())
    else:
        bot.send_message(uid, welcome_text)

# --- [ 5. منطق النشر المطور (إصلاح النشر للقناة) ] ---

@bot.message_handler(func=lambda m: m.text == "نشر في القناة 📣")
def start_publishing(message):
    uid = message.from_user.id
    if str(uid) not in admins_db and uid != DEVELOPER_ID:
        return
    
    prompt = "📣 أرسل الآن الملف (صورة أو مستند) أو النص الذي تريد نشره في القناة مع الأزرار:"
    msg = bot.send_message(uid, prompt)
    bot.register_next_step_handler(msg, process_channel_post)

def process_channel_post(message):
    admin_id = message.from_user.id
    
    # نص المنشور الثابت كما في الصورة
    caption_text = (
        "⚡ **تم تجديد الكونفيجات!**\n\n"
        "📁 عدد الملفات: 5\n"
        "🚀 سرعة عالية | ⏳ محدد المدة\n"
        "──────────────────\n"
        "📌 **طريقة الاستلام:**\n\n"
        "1️⃣ فعّل البوت بالضغط على 🤖\n"
        "2️⃣ ادعمنا بضغطة ❤️\n"
        "3️⃣ اضغط 📩 لاستلام الملفات\n"
        "──────────────────\n"
        "⚠️ سارع قبل انتهاء الصلاحية!"
    )

    try:
        # إذا أرسل الأدمن صورة
        if message.content_type == 'photo':
            bot.send_photo(
                OFFICIAL_CHANNEL_ID, 
                message.photo[-1].file_id, 
                caption=caption_text, 
                reply_markup=get_inline_post_keyboard(),
                parse_mode="Markdown"
            )
        # إذا أرسل الأدمن ملف/مستند
        elif message.content_type == 'document':
            bot.send_document(
                OFFICIAL_CHANNEL_ID, 
                message.document.file_id, 
                caption=caption_text, 
                reply_markup=get_inline_post_keyboard(),
                parse_mode="Markdown"
            )
        # إذا أرسل نصاً فقط
        else:
            bot.send_message(
                OFFICIAL_CHANNEL_ID, 
                caption_text, 
                reply_markup=get_inline_post_keyboard(),
                parse_mode="Markdown"
            )
            
        bot.send_message(admin_id, "✅ تم النشر بنجاح مع الأزرار التفاعلية!")
    except Exception as e:
        bot.send_message(admin_id, f"❌ حدث خطأ أثناء النشر: {e}")

# --- [ 6. معالجة ضغطات الأزرار (منع التكرار) ] ---

@bot.callback_query_handler(func=lambda call: call.data in ["action_receive", "action_like"])
def handle_callback_actions(call):
    user_id = call.from_user.id
    global stats_db
    
    # 1. زر التفاعل
    if call.data == "action_like":
        if user_id in stats_db["voted_users"]:
            bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً مع هذا المنشور!", show_alert=False)
            return
        
        # إضافة المستخدم للقائمة وزيادة العداد
        stats_db["voted_users"].append(user_id)
        stats_db["likes_count"] += 1
        bot.answer_callback_query(call.id, "❤️ شكراً على دعمك!")

    # 2. زر الاستلام
    elif call.data == "action_receive":
        if user_id in stats_db["received_users"]:
            bot.answer_callback_query(call.id, "⚠️ لقد استلمت الملفات مسبقاً!", show_alert=False)
        else:
            stats_db["received_users"].append(user_id)
            stats_db["receives_count"] += 1
            bot.answer_callback_query(call.id, "✅ تم تسجيل طلبك، تفقد الخاص لاستلام الملفات.", show_alert=True)
            # هنا يمكنك إرسال ملف فعلي للمستخدم في الخاص
            # bot.send_document(user_id, "FILE_ID_HERE")

    # حفظ التعديلات في الملف
    save_database("stats.json", stats_db)
    
    # تحديث واجهة الأزرار على الرسالة فوراً ليعرف الجميع الأرقام الجديدة
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            reply_markup=get_inline_post_keyboard()
        )
    except:
        pass

# --- [ 7. تشغيل النظام ] ---

@bot.message_handler(func=lambda m: m.text == "الإحصائيات 📊")
def show_statistics(message):
    if str(message.from_user.id) not in admins_db and message.from_user.id != DEVELOPER_ID:
        return
    msg = f"📊 إحصائيات النظام:\n\n❤️ عدد التفاعلات: {stats_db['likes_count']}\n📩 عدد المستلمين: {stats_db['receives_count']}"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "🔙 العودة للمنزل")
def back_home(message):
    welcome_user(message)

print(">>> Uchiha Dz Bot is Online and Ready!")
bot.infinity_polling()

