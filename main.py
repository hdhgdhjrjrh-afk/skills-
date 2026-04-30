import telebot
from telebot import types
import os
import json
import time
import logging
import datetime

# --- [ إعدادات الهوية والاتصال ] ---
# توكن البوت
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
# آيدي المطور SELVA ZOLDEK
OWNER_ID = 8611300267 

bot = telebot.TeleBot(TOKEN)

# --- [ نظام مراقبة الأداء والسجلات - Logging ] ---
# هذا الجزء لمراقبة كل حركة يقوم بها البوت في الترمكس
logging.basicConfig(
    filename='bot_activity.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- [ نظام إدارة قواعد البيانات - المسارات الصلبة ] ---

def check_and_create_files():
    """
    دالة فحص المسارات: تضمن وجود كل ملف بشكل مستقل
    وتنشئ محتوى افتراضي لمنع الأخطاء البرمجية.
    """
    # 1. ملف مستخدمي البوت
    if not os.path.exists("users.txt"):
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write("")
        logger.info("Created users.txt")

    # 2. ملف تخزين ملفات المطور (التي سيتم نشرها)
    if not os.path.exists("bot_files.json"):
        with open("bot_files.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        logger.info("Created bot_files.json")

    # 3. ملف قائمة الأدمنية وصلاحياتهم
    if not os.path.exists("admins.json"):
        with open("admins.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
        logger.info("Created admins.json")

    # 4. ملف الإحصائيات الدقيقة
    if not os.path.exists("stats.json"):
        initial_stats = {
            "downloads": 0,
            "likes": 0,
            "likes_log": [],
            "downloads_log": [],
            "broadcast_count": 0
        }
        with open("stats.json", "w", encoding="utf-8") as f:
            json.dump(initial_stats, f, indent=4)
        logger.info("Created stats.json")

    # 5. ملف الإعدادات والتحكم
    if not os.path.exists("settings.json"):
        initial_settings = {
            "notifications": True,
            "channel_id": "@Uchiha75",
            "sub_link": "https://t.me/Uchiha75",
            "force_sub": True,
            "dev_name": "SELVA ZOLDEK"
        }
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(initial_settings, f, indent=4)
        logger.info("Created settings.json")

# تشغيل نظام الفحص فور تشغيل السكريبت
check_and_create_files()

# --- [ دوال المعالجة المباشرة للبيانات ] ---

def load_json_file(file_path):
    """تحميل بيانات JSON مع التحقق من سلامة الملف"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return {}

def write_json_file(file_path, data):
    """حفظ بيانات JSON بشكل منسق وطويل"""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            return True
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {e}")
        return False

def fetch_users_list():
    """جلب قائمة اليوزرات من ملف النص"""
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as f:
            content = f.read().splitlines()
            return content
    return []

# --- [ نظام الصلاحيات - مستويات الوصول ] ---

def is_super_dev(uid):
    """فحص هل المستخدم هو المطور الأساسي"""
    if int(uid) == OWNER_ID:
        return True
    return False

def is_bot_admin(uid):
    """فحص هل المستخدم يملك صلاحيات أدمن"""
    if is_super_dev(uid):
        return True
    admins_data = load_json_file("admins.json")
    if str(uid) in admins_data:
        return True
    return False

# --- [ هندسة واجهة المستخدم - الأزرار ] ---

def create_main_keyboard(uid):
    """بناء لوحة التحكم الرئيسية بشكل مفصل وغير مختصر"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    config = load_json_file("settings.json")
    
    # أزرار الإدارة للأدمن والمطور
    btn_post_channel = types.KeyboardButton("نشر في القناة 📣")
    btn_upload_files = types.KeyboardButton("إضافة ملفات 📤")
    btn_broadcast_sec = types.KeyboardButton("قسم الإذاعة 📢")
    btn_view_stats = types.KeyboardButton("الإحصائيات 📊")
    
    keyboard.add(btn_post_channel, btn_upload_files)
    keyboard.add(btn_broadcast_sec, btn_view_stats)
    
    # أزرار خاصة بالمطور SELVA ZOLDEK فقط
    if is_super_dev(uid):
        btn_add_adm = types.KeyboardButton("إضافة أدمن ➕")
        btn_adm_settings = types.KeyboardButton("صلاحيات أدمن ⚙️")
        btn_link_sub = types.KeyboardButton("إضافة اشتراك 🔗")
        
        # تحديد نص زر الإشعارات بناءً على الحالة الحالية
        if config.get("notifications") == True:
            btn_notif_ctrl = types.KeyboardButton("إيقاف الإشعارات ❌")
        else:
            btn_notif_ctrl = types.KeyboardButton("تفعيل الإشعارات ✅")
            
        btn_reset_files = types.KeyboardButton("تصفير ملفات 🗑️")
        btn_purge_data = types.KeyboardButton("تنظيف بيانات 🧹")
        
        keyboard.row(btn_add_adm, btn_adm_settings)
        keyboard.row(btn_link_sub, btn_notif_ctrl)
        keyboard.row(btn_reset_files, btn_purge_data)
        
    return keyboard

def create_broadcast_markup():
    """بناء أزرار الإذاعة التفاعلية"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    button_user = types.InlineKeyboardButton("👤 إرسال للمستخدمين (خاص)", callback_data="target_users")
    button_chan = types.InlineKeyboardButton("📢 إرسال للقناة (عام)", callback_data="target_channel")
    button_both = types.InlineKeyboardButton("🌍 إرسال للجميع (شامل)", callback_data="target_all")
    button_exit = types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="close_broadcaster")
    
    markup.add(button_user, button_chan, button_both, button_exit)
    return markup

# --- [ معالجة رسائل البداية - Start Handler ] ---

@bot.message_handler(commands=['start'])
def welcome_start(message):
    uid = message.from_user.id
    first_name = message.from_user.first_name
    all_users = fetch_users_list()
    settings = load_json_file("settings.json")

    # 1. الترحيب الخاص بالمطور SELVA ZOLDEK
    if is_super_dev(uid):
        dev_msg = "مرحبا ايها مطو😈 SELVA ZOLDEK 😈"
        bot.send_message(uid, dev_msg, reply_markup=create_main_keyboard(uid))
    else:
        # الترحيب بالمستخدم العادي
        bot.send_message(uid, f"أهلاً بك {first_name} في لوحة خدمات Uchiha Dz ⚡", reply_markup=create_main_keyboard(uid))

    # 2. تسجيل المستخدم في النظام وإرسال إشعار للمطور
    if str(uid) not in all_users:
        try:
            with open("users.txt", "a", encoding="utf-8") as f:
                f.write(f"{uid}\n")
            
            # فحص إعدادات الإشعارات
            if settings.get("notifications") == True:
                notify_text = (
                    f"🚀 **مستخدم جديد دخل البوت!**\n\n"
                    f"👤 الاسم: {first_name}\n"
                    f"🆔 الآيدي: `{uid}`\n"
                    f"🔗 الحساب: [فتح البروفايل](tg://user?id={uid})\n"
                    f"📅 التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                bot.send_message(OWNER_ID, notify_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to register user {uid}: {e}")

    # 3. نظام استلام الملفات (Deep Linking)
    if "get_files" in message.text:
        stats_data = load_json_file("stats.json")
        # فحص هل تفاعل المستخدم في القناة (من سجل التفاعلات)
        if uid in stats_data.get("likes_log", []):
            files_list = load_json_file("bot_files.json")
            if not files_list:
                bot.send_message(uid, "❌ عذراً، لا توجد ملفات متوفرة في النظام حالياً.")
                return
            
            bot.send_message(uid, "⏳ جاري جلب الملفات من السيرفر...")
            for item in files_list:
                try:
                    bot.send_document(uid, item['file_id'], caption=item.get('caption', ""))
                    time.sleep(0.5) # حماية من التلجرام سبام
                except:
                    continue
        else:
            bot.send_message(uid, "⚠️ خطأ في الوصول! يجب عليك العودة للقناة والتفاعل بـ (❤️) أولاً.")

# --- [ موزع الأوامر والوظائف - System Router ] ---

@bot.message_handler(func=lambda message: True)
def system_operation_router(message):
    uid = message.from_user.id
    txt = message.text
    
    # منع غير الأدمنية من استخدام هذه الأوامر
    if not is_bot_admin(uid):
        return

    # --- وظيفة: إضافة ملفات 📤 ---
    if txt == "إضافة ملفات 📤":
        prompt = bot.send_message(uid, "📤 أرسل الآن الملف (Document) مع الوصف في الكابشن:")
        bot.register_next_step_handler(prompt, save_uploaded_file_step)

    # --- وظيفة: نشر في القناة 📣 ---
    elif txt == "نشر في القناة 📣":
        conf = load_json_file("settings.json")
        docs = load_json_file("bot_files.json")
        
        if not docs:
            bot.send_message(uid, "❌ لا يمكن النشر! قاعدة البيانات لا تحتوي على ملفات.")
            return
            
        inline_btn = types.InlineKeyboardMarkup()
        inline_btn.add(types.InlineKeyboardButton("❤️ تفاعل واستلم الملفات فوراً", url=f"https://t.me/{bot.get_me().username}?start=get_files"))
        
        channel_post = (
            f"⚡ **تحديث جديد متاح الآن!**\n\n"
            f"📁 عدد الملفات المرفوعة: {len(docs)}\n"
            f"🚀 حالة السيرفر: سريع جداً\n"
            f"━━━━━━━━━━━━━━\n"
            f"📥 اضغط على الزر بالأسفل للاستلام 👇"
        )
        try:
            bot.send_message(conf["channel_id"], channel_post, reply_markup=inline_btn, parse_mode="Markdown")
            bot.send_message(uid, f"✅ تم النشر بنجاح في القناة {conf['channel_id']}")
        except Exception as err:
            bot.send_message(uid, f"❌ فشل النشر. تأكد من أن البوت أدمن في القناة.\nالخطأ: {err}")

    # --- وظيفة: إضافة أدمن ➕ (المطور فقط) ---
    elif txt == "إضافة أدمن ➕" and is_super_dev(uid):
        prompt = bot.send_message(uid, "👤 أرسل الآن آيدي (ID) الشخص المراد منحه صلاحيات أدمن:")
        bot.register_next_step_handler(prompt, save_admin_id_step)

    # --- وظيفة: عرض صلاحيات أدمن ⚙️ ---
    elif txt == "صلاحيات أدمن ⚙️" and is_super_dev(uid):
        all_admins = load_json_file("admins.json")
        if not all_admins:
            bot.send_message(uid, "❌ قائمة المسؤولين فارغة.")
            return
        
        admin_report = "⚙️ **قائمة مدراء النظام:**\n\n"
        for a_id, info in all_admins.items():
            admin_report += f"🔹 الآيدي: `{a_id}` | التاريخ: {info.get('at', 'غير معروف')}\n"
        bot.send_message(uid, admin_report, parse_mode="Markdown")

    # --- وظيفة: إضافة اشتراك 🔗 ---
    elif txt == "إضافة اشتراك 🔗" and is_super_dev(uid):
        prompt = bot.send_message(uid, "🔗 أرسل رابط القناة (t.me/...):")
        bot.register_next_step_handler(prompt, save_channel_link_step)

    # --- وظيفة: التحكم في الإشعارات ---
    elif txt in ["تفعيل الإشعارات ✅", "إيقاف الإشعارات ❌"] and is_super_dev(uid):
        settings_db = load_json_file("settings.json")
        settings_db["notifications"] = not settings_db.get("notifications", True)
        write_json_file("settings.json", settings_db)
        bot.send_message(uid, "✅ تم تحديث تفضيلات الإشعارات.", reply_markup=create_main_keyboard(uid))

    # --- وظيفة: قسم الإذاعة 📢 ---
    elif txt == "قسم الإذاعة 📢":
        bot.send_message(uid, "⚙️ يرجى اختيار وجهة الإذاعة من القائمة:", reply_markup=create_broadcast_markup())

    # --- وظيفة: الإحصائيات 📊 ---
    elif txt == "الإحصائيات 📊":
        u_count = fetch_users_list()
        f_count = load_json_file("bot_files.json")
        s_count = load_json_file("stats.json")
        
        final_report = (
            f"📊 **إحصائيات النظام الشاملة:**\n\n"
            f"👥 المشتركين: `{len(u_count)}` مستخدم\n"
            f"📁 الملفات المرفوعة: `{len(f_count)}` ملف\n"
            f"❤️ التفاعلات: `{s_count.get('likes', 0)}` تفاعل\n"
            f"📥 التحميلات: `{s_count.get('downloads', 0)}` عملية"
        )
        bot.send_message(uid, final_report, parse_mode="Markdown")

    # --- وظيفة: تصفير الملفات 🗑️ ---
    elif txt == "تصفير ملفات 🗑️" and is_super_dev(uid):
        write_json_file("bot_files.json", [])
        bot.send_message(uid, "🗑️ تم حذف كافة الملفات من قاعدة البيانات.")

    # --- وظيفة: تنظيف بيانات 🧹 ---
    elif txt == "تنظيف بيانات 🧹" and is_super_dev(uid):
        reset_stats = {"downloads": 0, "likes": 0, "likes_log": [], "downloads_log": [], "broadcast_count": 0}
        write_json_file("stats.json", reset_stats)
        bot.send_message(uid, "🧹 تم تنظيف كافة العدادات وسجلات التفاعل.")

# --- [ وظائف معالجة الخطوات - Step Handlers ] ---

def save_uploaded_file_step(message):
    """حفظ الملف المرفوع في قاعدة البيانات JSON بشكل دقيق"""
    if message.content_type == 'document':
        current_files = load_json_file("bot_files.json")
        new_file = {
            "file_id": message.document.file_id,
            "caption": message.caption if message.caption else "ملف من Uchiha Dz",
            "uploaded_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        current_files.append(new_file)
        if write_json_file("bot_files.json", current_files):
            bot.send_message(message.chat.id, "✅ تم رفع الملف وحفظه بنجاح!")
        else:
            bot.send_message(message.chat.id, "❌ خطأ تقني في حفظ الملف.")
    else:
        bot.send_message(message.chat.id, "❌ فشل! يرجى إرسال ملف بصيغة Document.")

def save_admin_id_step(message):
    """إضافة آيدي الأدمن الجديد للقائمة"""
    if message.text and message.text.isdigit():
        admins_db = load_json_file("admins.json")
        new_admin_id = message.text
        admins_db[new_admin_id] = {"at": datetime.datetime.now().strftime('%Y-%m-%d')}
        write_json_file("admins.json", admins_db)
        bot.send_message(message.chat.id, f"✅ تم منح صلاحيات أدمن للآيدي: `{new_admin_id}`", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ خطأ: الآيدي يجب أن يكون عبارة عن أرقام فقط.")

def save_channel_link_step(message):
    """تحديث رابط القناة ومعرفها"""
    if "t.me/" in message.text:
        settings_db = load_json_file("settings.json")
        settings_db["sub_link"] = message.text
        try:
            # استخراج اليوزر نيم من الرابط
            user_part = message.text.split("t.me/")[1].split("/")[0]
            settings_db["channel_id"] = "@" + user_part
            write_json_file("settings.json", settings_db)
            bot.send_message(message.chat.id, f"✅ تم تحديث الاشتراك الإجباري:\nقناة: `{settings_db['channel_id']}`", parse_mode="Markdown")
        except:
            bot.send_message(message.chat.id, "❌ فشل استخراج المعرف. تأكد من صحة الرابط.")
    else:
        bot.send_message(message.chat.id, "❌ رابط غير صحيح.")

# --- [ نظام الإذاعة والـ Callback Queries ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_system_callbacks(call):
    uid = call.from_user.id
    data = call.data
    
    if data.startswith("target_"):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        target_type = data.split("_")[1] # users, channel, or all
        msg_prompt = bot.send_message(call.message.chat.id, "📩 أرسل الآن المحتوى (نص/ميديا/ملف) الذي تود إذاعته:")
        bot.register_next_step_handler(msg_prompt, execute_broadcast_final, target_type)

    elif data == "close_broadcaster":
        bot.delete_message(call.message.chat.id, call.message.message_id)

def execute_broadcast_final(message, target_type):
    """الدالة النهائية لتنفيذ الإذاعة الطويلة والدقيقة"""
    users_to_send = fetch_users_list()
    config_data = load_json_file("settings.json")
    success_hits = 0
    
    # الإرسال للمستخدمين في الخاص
    if target_type in ["users", "all"]:
        bot.send_message(OWNER_ID, "⏳ جاري تنفيذ الإذاعة للمستخدمين...")
        for u_id in users_to_send:
            try:
                bot.copy_message(u_id, message.chat.id, message.message_id)
                success_hits += 1
                time.sleep(0.05) # تأخير بسيط للحماية
            except:
                continue
    
    # الإرسال للقناة
    if target_type in ["channel", "all"]:
        try:
            bot.copy_message(config_data["channel_id"], message.chat.id, message.message_id)
            bot.send_message(OWNER_ID, f"✅ تم النشر في القناة: {config_data['channel_id']}")
        except Exception as e:
            bot.send_message(OWNER_ID, f"❌ فشل إرسال القناة: {e}")

    # تحديث إحصائيات الإذاعة
    stats_db = load_json_file("stats.json")
    stats_db["broadcast_count"] = stats_db.get("broadcast_count", 0) + 1
    write_json_file("stats.json", stats_db)
    
    bot.send_message(OWNER_ID, f"🏁 انتهت العملية بنجاح!\nعدد المستلمين في الخاص: {success_hits}")

# --- [ نقطة الانطلاق والتشغيل النهائي ] ---

if __name__ == "__main__":
    print("---------------------------------------")
    print(f"⚡ BOT @{bot.get_me().username} IS ONLINE")
    print(f"🛠️ DEVELOPER: {OWNER_ID} (SELVA ZOLDEK)")
    print("---------------------------------------")
    
    # حلقة تشغيل لا نهائية لضمان الاستقرار في بيئة Termux
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=15)
        except Exception as critical_error:
            logger.critical(f"Bot crashed! Restarting... Error: {critical_error}")
            time.sleep(5)

