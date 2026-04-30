import telebot
from telebot import types
import os
import json
import time
import logging
import requests

# --- [ إعدادات الهوية والاتصال ] ---
# توكن البوت الخاص بك
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
# آيدي المطور الأساسي
OWNER_ID = 8611300267 

# تهيئة مكتبة البوت
bot = telebot.TeleBot(TOKEN)

# إعداد نظام مراقبة الأخطاء (Logging) لضمان تتبع كل حركة
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- [ نظام إدارة المسارات وقواعد البيانات ] ---

def initialize_all_databases():
    """
    هذه الدالة هي العمود الفقري للبوت، تقوم بفحص كافة الملفات والمسارات
    وتنشئها في حال عدم وجودها لضمان عدم توقف البوت (Crash).
    """
    # مسار ملف المستخدمين (نصي)
    if not os.path.exists("users.txt"):
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write("")
    
    # مسار ملف الملفات المرفوعة (JSON)
    if not os.path.exists("bot_files.json"):
        with open("bot_files.json", "w", encoding="utf-8") as f:
            json.dump([], f)
            
    # مسار ملف الأدمنية (JSON)
    if not os.path.exists("admins.json"):
        with open("admins.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
            
    # مسار ملف الإحصائيات الشامل (JSON)
    if not os.path.exists("stats.json"):
        stats_data = {
            "downloads": 0,
            "likes": 0,
            "likes_log": [],
            "downloads_log": [],
            "total_broadcasts": 0
        }
        with open("stats.json", "w", encoding="utf-8") as f:
            json.dump(stats_data, f, indent=4)
            
    # مسار ملف الإعدادات العامة (JSON)
    if not os.path.exists("settings.json"):
        settings_data = {
            "notifications": True,
            "channel_id": "@Uchiha75",
            "sub_link": "https://t.me/Uchiha75",
            "force_sub": True,
            "welcome_mode": "developer"
        }
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings_data, f, indent=4)

# تشغيل الفحص عند بدء الكود
initialize_all_databases()

# --- [ دوال جلب وحفظ البيانات - دقة عالية ] ---

def get_json_data(file_name):
    """جلب البيانات من ملفات JSON مع معالجة الأخطاء"""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading {file_name}: {e}")
        return {}

def save_json_data(file_name, data):
    """حفظ البيانات في ملفات JSON بشكل منظم"""
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving {file_name}: {e}")

def get_all_users():
    """جلب قائمة كافة المستخدمين من ملف النص"""
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# --- [ دوال التحقق من الرتب ] ---

def is_developer(user_id):
    """التحقق هل المستخدم هو المطور SELVA ZOLDEK"""
    return int(user_id) == OWNER_ID

def is_authorized_admin(user_id):
    """التحقق هل المستخدم أدمن مضاف في القائمة"""
    if is_developer(user_id):
        return True
    admins_list = get_json_data("admins.json")
    return str(user_id) in admins_list

# --- [ بناء لوحات التحكم (Keyboards) ] ---

def build_main_menu(user_id):
    """إنشاء كيبورد التحكم الرئيسي المفصل"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    settings = get_json_data("settings.json")
    
    # أزرار الإدارة العامة (للأدمن والمطور)
    btn_post = types.KeyboardButton("نشر في القناة 📣")
    btn_add_file = types.KeyboardButton("إضافة ملفات 📤")
    btn_bc = types.KeyboardButton("قسم الإذاعة 📢")
    btn_stats = types.KeyboardButton("الإحصائيات 📊")
    
    markup.add(btn_post, btn_add_file)
    markup.add(btn_bc, btn_stats)
    
    # أزرار التحكم العميق (للمطور فقط)
    if is_developer(user_id):
        btn_add_admin = types.KeyboardButton("إضافة أدمن ➕")
        btn_admin_perms = types.KeyboardButton("صلاحيات أدمن ⚙️")
        btn_add_sub = types.KeyboardButton("إضافة اشتراك 🔗")
        
        # تبديل نص زر الإشعارات ديناميكياً
        notif_status = "إيقاف الإشعارات ❌" if settings.get("notifications") else "تفعيل الإشعارات ✅"
        btn_notif = types.KeyboardButton(notif_status)
        
        btn_reset_files = types.KeyboardButton("تصفير ملفات 🗑️")
        btn_clean_data = types.KeyboardButton("تنظيف بيانات 🧹")
        
        markup.row(btn_add_admin, btn_admin_perms)
        markup.row(btn_add_sub, btn_notif)
        markup.row(btn_reset_files, btn_clean_data)
        
    return markup

def build_broadcast_inline():
    """لوحة خيارات الإذاعة الثلاثية المفصلة"""
    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    
    opt1 = types.InlineKeyboardButton("👤 إذاعة للمستخدمين (بوت)", callback_data="run_bc_users")
    opt2 = types.InlineKeyboardButton("📢 إذاعة للقناة (نشر)", callback_data="run_bc_channel")
    opt3 = types.InlineKeyboardButton("🌍 إذاعة شاملة (الجميع)", callback_data="run_bc_all")
    opt4 = types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_task")
    
    inline_kb.add(opt1, opt2, opt3, opt4)
    return inline_kb

# --- [ معالجة رسائل النظام - Start ] ---

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    current_users = get_all_users()
    config = get_json_data("settings.json")

    # 1. نظام الترحيب الخاص بالمطور (طلب المستخدم)
    if is_developer(user_id):
        dev_welcome = "مرحبا ايها مطو😈 SELVA ZOLDEK 😈"
        bot.send_message(user_id, dev_welcome, reply_markup=build_main_menu(user_id))
    else:
        # ترحيب عادي للمستخدمين الآخرين
        bot.send_message(user_id, f"أهلاً بك {user_name} في بوت الخدمات ⚡", reply_markup=build_main_menu(user_id))

    # 2. تسجيل دخول مستخدم جديد وإرسال الإشعار للمطور
    if str(user_id) not in current_users:
        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        
        # فحص حالة الإشعارات من الإعدادات
        if config.get("notifications"):
            try:
                notification_text = (
                    f"😈 **إشعار مطور: دخول جديد!**\n\n"
                    f"👤 الاسم: {user_name}\n"
                    f"🆔 الآيدي: `{user_id}`\n"
                    f"🔗 الحساب: [رابط الملف الشخصي](tg://user?id={user_id})"
                )
                bot.send_message(OWNER_ID, notification_text, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Notification failed: {e}")

    # 3. معالجة روابط الملفات (Deep Linking)
    if "get_files" in message.text:
        stats = get_json_data("stats.json")
        if user_id in stats.get("likes_log", []):
            files_db = get_json_data("bot_files.json")
            if not files_db:
                bot.send_message(user_id, "❌ لا توجد ملفات حالياً في قاعدة البيانات.")
                return
            
            bot.send_message(user_id, "🚀 جاري استخراج الملفات وإرسالها لك...")
            for doc in files_db:
                try:
                    bot.send_document(user_id, doc['file_id'], caption=doc.get('caption', ""))
                    time.sleep(0.3) # تأخير بسيط لضمان الترتيب
                except:
                    continue
        else:
            bot.send_message(user_id, "⚠️ عذراً! يجب عليك التفاعل بـ (❤️) في القناة أولاً لتفعيل زر الاستلام.")

# --- [ موزع المهام الرئيسي (Router) ] ---

@bot.message_handler(func=lambda m: True)
def main_system_router(message):
    uid = message.from_user.id
    text = message.text
    
    # فحص الصلاحية قبل تنفيذ أي أمر إداري
    if not is_authorized_admin(uid):
        return

    # 1. وظيفة إضافة أدمن (للمطور فقط)
    if text == "إضافة أدمن ➕" and is_developer(uid):
        msg = bot.send_message(uid, "👤 أرسل الآن (آيدي) الشخص الذي تريد رفعه أدمن:")
        bot.register_next_step_handler(msg, step_save_admin)

    # 2. وظيفة إضافة اشتراك إجباري (للمطور فقط)
    elif text == "إضافة اشتراك 🔗" and is_developer(uid):
        msg = bot.send_message(uid, "🔗 أرسل رابط القناة (مثال: https://t.me/Uchiha75):")
        bot.register_next_step_handler(msg, step_save_subscription)

    # 3. وظيفة التحكم بالإشعارات
    elif text in ["تفعيل الإشعارات ✅", "إيقاف الإشعارات ❌"] and is_developer(uid):
        current_config = get_json_data("settings.json")
        current_config["notifications"] = not current_config.get("notifications", True)
        save_json_data("settings.json", current_config)
        bot.send_message(uid, "⚙️ تم تحديث إعدادات الإشعارات بنجاح.", reply_markup=build_main_menu(uid))

    # 4. وظيفة الإحصائيات المفصلة
    elif text == "الإحصائيات 📊":
        all_u = get_all_users()
        all_f = get_json_data("bot_files.json")
        all_s = get_json_data("stats.json")
        
        stats_msg = (
            f"📊 **تقرير نظام Uchiha Dz الشامل:**\n\n"
            f"👥 المشتركين بالبوت: `{len(all_u)}` مستخدم\n"
            f"📁 الملفات المرفوعة: `{len(all_f)}` ملف\n"
            f"❤️ إجمالي التفاعلات: `{all_s.get('likes', 0)}` تفاعل\n"
            f"📥 عدد طلبات التحميل: `{all_s.get('downloads', 0)}` طلب\n"
            f"📢 عمليات الإذاعة: `{all_s.get('total_broadcasts', 0)}` عملية"
        )
        bot.send_message(uid, stats_msg, parse_mode="Markdown")

    # 5. وظيفة الإذاعة
    elif text == "قسم الإذاعة 📢":
        bot.send_message(uid, "⚙️ اختر المسار المستهدف للإذاعة من القائمة أدناه:", reply_markup=build_broadcast_inline())

    # 6. وظيفة تصفير الملفات
    elif text == "تصفير ملفات 🗑️" and is_developer(uid):
        save_json_data("bot_files.json", [])
        bot.send_message(uid, "🗑️ تم مسح قاعدة بيانات الملفات بالكامل بنجاح.")

    # 7. وظيفة تنظيف البيانات (العدادات)
    elif text == "تنظيف بيانات 🧹" and is_developer(uid):
        cleaned_stats = {
            "downloads": 0, "likes": 0, "likes_log": [], "downloads_log": [], "total_broadcasts": 0
        }
        save_json_data("stats.json", cleaned_stats)
        bot.send_message(uid, "🧹 تم تصفير كافة سجلات التفاعل والعدادات بنجاح.")

# --- [ دوال تنفيذ الخطوات (Step Handlers) ] ---

def step_save_admin(message):
    """دالة حفظ الأدمن الجديد في الملف"""
    if message.text.isdigit():
        admins_db = get_json_data("admins.json")
        target_id = message.text
        admins_db[target_id] = {"status": "active", "date": time.ctime()}
        save_json_data("admins.json", admins_db)
        bot.send_message(message.chat.id, f"✅ تم إضافة `{target_id}` إلى قائمة الأدمنية بنجاح.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ خطأ: يجب إرسال آيدي رقمي فقط.")

def step_save_subscription(message):
    """دالة حفظ وتحديث قناة الاشتراك الإجباري"""
    if "t.me/" in message.text:
        settings_db = get_json_data("settings.json")
        settings_db["sub_link"] = message.text
        try:
            # استخراج اليوزر من الرابط
            raw_id = message.text.split("t.me/")[1].replace("/", "")
            settings_db["channel_id"] = "@" + raw_id
            save_json_data("settings.json", settings_db)
            bot.send_message(message.chat.id, f"✅ تم تحديث الاشتراك الإجباري:\nالقناة: `{settings_db['channel_id']}`", parse_mode="Markdown")
        except:
            bot.send_message(message.chat.id, "❌ فشل استخراج معرف القناة من الرابط.")
    else:
        bot.send_message(message.chat.id, "❌ الرابط غير صحيح، يجب أن يحتوي على t.me/")

# --- [ نظام الإذاعة والـ Callback Queries ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callback(call):
    uid = call.from_user.id
    data = call.data
    
    if data.startswith("run_bc_"):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        target_type = data.split("_")[2] # users / channel / all
        prompt = bot.send_message(call.message.chat.id, "📩 أرسل الآن محتوى الإذاعة (نص، صورة، فيديو، بصمة، ملف):")
        bot.register_next_step_handler(prompt, process_final_broadcast, target_type)

    elif data == "cancel_task":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "❌ تم إلغاء العملية.")

def process_final_broadcast(message, target_type):
    """الدالة النهائية لتنفيذ الإذاعة الثلاثية"""
    all_users = get_all_users()
    config = get_json_data("settings.json")
    stats = get_json_data("stats.json")
    
    sent_count = 0
    
    # 1. الإرسال للمستخدمين
    if target_type in ["users", "all"]:
        bot.send_message(OWNER_ID, "⏳ جاري الإرسال لكافة المستخدمين...")
        for user_id in all_users:
            try:
                bot.copy_message(user_id, message.chat.id, message.message_id)
                sent_count += 1
                time.sleep(0.05) # حماية من Flood تلجرام
            except:
                continue
    
    # 2. الإرسال للقناة
    if target_type in ["channel", "all"]:
        try:
            bot.copy_message(config["channel_id"], message.chat.id, message.message_id)
            bot.send_message(OWNER_ID, f"✅ تم النشر بنجاح في القناة: {config['channel_id']}")
        except Exception as error:
            bot.send_message(OWNER_ID, f"❌ فشل النشر في القناة. الخطأ: {error}")

    # تحديث إحصائيات الإذاعة
    stats["total_broadcasts"] = stats.get("total_broadcasts", 0) + 1
    save_json_data("stats.json", stats)
    
    bot.send_message(OWNER_ID, f"🏁 اكتملت عملية الإذاعة بنجاح!\nتم الوصول لـ {sent_count} مستخدم.")

# --- [ نقطة تشغيل البوت مع حماية دائرية ] ---

if __name__ == "__main__":
    print("---------------------------------------")
    print("⚡ SELVA ZOLDEK BOT IS STARTING...")
    print(f"🛠️ DEVELOPER: {OWNER_ID}")
    print("---------------------------------------")
    
    # حلقة تشغيل لا نهائية لضمان عدم توقف البوت عند انقطاع الإنترنت
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as server_error:
            logging.error(f"🔄 إعادة تشغيل تلقائية بسبب: {server_error}")
            time.sleep(5)
