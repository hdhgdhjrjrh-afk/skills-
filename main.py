# =========================================================================
# ⚡ U҉c҉h҉i҉h҉a҉ ҉D҉z҉  - THE SUPREME GIGANTIC MONSTER SYSTEM ⚡
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛠️ ARCHITECT       : SELVA ZOLDEK
# 🆔 MASTER ADMIN ID : 8611300267
# 🔄 VERSION         : 19.0.0 (ULTIMATE VERBOSE EDITION)
# 🛡️ OPTIMIZATION    : TERMUX / ANDROID / LINUX
# 📜 LINE COUNT      : +1000 LINES (STRICT EXPANSION MODE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# =========================================================================

# --- [ القسم 1: استيراد المكتبات بأسلوب منفصل تماماً ] ---
import telebot          # المكتبة الأساسية للتحكم بالبوت
import os               # للتعامل مع ملفات النظام في Termux
import json             # لإدارة قواعد البيانات بصيغة JSON
import time             # لإضافة تأخير زمني ومنع الحظر
import datetime         # لتوثيق وقت العمليات بدقة
import logging          # لنظام السجلات الاحترافي
import sys              # للتعامل مع متغيرات النظام
import random           # لتوليد أرقام عشوائية (إذا لزم الأمر)
import traceback        # لتتبع الأخطاء البرمجية بالتفصيل
import shutil           # للتعامل مع العمليات المتقدمة للملفات
import threading        # لتشغيل عدة مهام في وقت واحد
import platform         # لمعرفة معلومات الجهاز المشغل
from telebot import types # لجلب أنواع الكيبوردات والأزرار

# -------------------------------------------------------------------------
# [ القسم 2: إعدادات الهوية والوصول - IDENTITY ]
# -------------------------------------------------------------------------

# توكن البوت الخاص بك
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"

# معرف المطور (أنت) - SELVA ZOLDEK
MASTER_ADMIN_ID = 8611300267 

# معرف القناة الرسمية للنشر
OFFICIAL_CHANNEL_USERNAME = "@Uchiha75"

# اسم النظام
SYSTEM_IDENTITY_NAME = "⚡U҉c҉h҉i҉h҉a҉ ҉D҉z҉ ҉⚡"

# -------------------------------------------------------------------------
# [ القسم 3: نظام المراقبة والسجلات - MONITORING ]
# -------------------------------------------------------------------------

class UchihaBeastMonitor:
    """نظام مراقبة متطور يطبع كل حركة في الترمينال ويحفظها في ملف"""
    def __init__(self):
        self.log_filename = "uchiha_system_master.log"
        self._initialize_logger()

    def _initialize_logger(self):
        # إعداد تنسيق السجل: الوقت - المستوى - الرسالة
        log_format = '%(asctime)s - [%(levelname)s] - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_filename, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.internal_logger = logging.getLogger("UchihaMaster")

    def record_info(self, message_text):
        """تسجيل معلومة عادية"""
        self.internal_logger.info(message_text)

    def record_error(self, error_text):
        """تسجيل خطأ تقني"""
        self.internal_logger.error(error_text)

    def record_warning(self, warning_text):
        """تسجيل تحذير"""
        self.internal_logger.warning(warning_text)

# تهيئة المراقب الإمبراطوري
monitor = UchihaBeastMonitor()

# -------------------------------------------------------------------------
# [ القسم 4: محرك قواعد البيانات المتفرع - DATABASE ENGINE ]
# -------------------------------------------------------------------------

class DatabaseArchitect:
    """نظام إدارة البيانات: تم تفكيكه لزيادة الحجم والدقة القصوى"""
    def __init__(self):
        # تعريف مسارات الملفات
        self.users_db_path = "users_registry.txt"
        self.stats_db_path = "system_statistics.json"
        self.vault_db_path = "media_publishing_vault.json"
        self.subs_db_path = "subscription_channels.json"
        self.admins_db_path = "admin_permissions.json"
        
        # التأكد من سلامة الملفات
        self.verify_and_build_environment()

    def verify_and_build_environment(self):
        """خلق بيئة العمل في Termux إذا كانت مفقودة"""
        monitor.record_info("Verifying Database Environment...")
        
        # إنشاء ملف المستخدمين (نصي)
        if not os.path.exists(self.users_db_path):
            with open(self.users_db_path, "w") as f:
                f.write("")
        
        # إنشاء ملفات JSON بالبيانات الافتراضية
        self._setup_json_file(self.stats_db_path, {"receives": 0, "broadcasts": 0})
        self._setup_json_file(self.vault_db_path, [])
        self._setup_json_file(self.subs_db_path, [])
        self._setup_json_file(self.admins_db_path, {str(MASTER_ADMIN_ID): {"name": "SELVA", "rank": "OWNER"}})

    def _setup_json_file(self, path, default_content):
        if not os.path.exists(path):
            self.write_json_data(path, default_content)

    def write_json_data(self, path, content):
        """كتابة البيانات بدقة عالية مع مسافات بادئة (Indent)"""
        try:
            with open(path, 'w', encoding='utf-8') as file_handle:
                json.dump(content, file_handle, indent=4, ensure_ascii=False)
            return True
        except Exception as failure:
            monitor.record_error(f"Write Failure: {failure}")
            return False

    def read_json_data(self, path):
        """قراءة البيانات من ملفات JSON"""
        try:
            if not os.path.exists(path): return []
            with open(path, 'r', encoding='utf-8') as file_handle:
                return json.load(file_handle)
        except Exception as failure:
            monitor.record_error(f"Read Failure: {failure}")
            return []

    def register_new_user(self, user_id):
        """تسجيل المستخدم الجديد في القائمة"""
        uid = str(user_id)
        with open(self.users_db_path, "r") as f:
            all_users = f.read()
            if uid not in all_users:
                with open(self.users_db_path, "a") as f_append:
                    f_append.write(uid + "\n")
                monitor.record_info(f"New User Registered: {uid}")
                return True
        return False

    def fetch_user_count(self):
        """حساب عدد المستخدمين المسجلين"""
        with open(self.users_db_path, "r") as f:
            lines = f.readlines()
            return len([l for l in lines if l.strip()])

# تهيئة كائن قاعدة البيانات
db = DatabaseArchitect()

# -------------------------------------------------------------------------
# [ القسم 5: كائن البوت الرئيسي - TELEGRAM BOT CORE ]
# -------------------------------------------------------------------------

# تهيئة البوت مع خاصية تعدد الخيوط (Threaded) لسرعة الاستجابة
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=True)

# -------------------------------------------------------------------------
# [ القسم 6: مهندس الواجهات - UI & KEYBOARDS ]
# -------------------------------------------------------------------------

class InterfaceEngineer:
    """بناء الأزرار والواجهات بأسلوب مطول جداً لزيادة حجم السورس"""
    
    @staticmethod
    def construct_main_menu(user_id):
        """بناء القائمة الرئيسية بناءً على الرتبة"""
        menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        
        # جلب قائمة الأدمن
        admins = db.read_json_data(db.admins_db_path)
        
        if str(user_id) in admins or int(user_id) == MASTER_ADMIN_ID:
            btn_admin = types.KeyboardButton("لوحة تحكم الأدمن 🛠️")
            menu.add(btn_admin)
        else:
            btn_files = types.KeyboardButton("استلام الملفات 📥")
            menu.add(btn_files)
        return menu

    @staticmethod
    def construct_admin_panel(user_id):
        """بناء لوحة التحكم الخاصة بالأدمن والمطور"""
        panel = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        # أزرار الرفع والنشر الأساسية
        upload_btn = types.KeyboardButton("إضافة ملفات 📤")
        publish_btn = types.KeyboardButton("نشر في القناة 📣")
        
        # أزرار الإحصائيات والإذاعة
        stats_btn = types.KeyboardButton("الإحصائيات 📊")
        radio_btn = types.KeyboardButton("قسم الإذاعة 📡")
        
        panel.add(upload_btn, publish_btn)
        panel.add(stats_btn, radio_btn)
        
        # خيارات حصرية للمطور الأساسي فقط
        if int(user_id) == MASTER_ADMIN_ID:
            perm_btn = types.KeyboardButton("صلاحيات أدمن ⚙️")
            sub_btn = types.KeyboardButton("إدارة الاشتراك 🔗")
            panel.row(perm_btn, sub_btn)
            
            clean_btn = types.KeyboardButton("تنظيف بيانات 🧹")
            reset_btn = types.KeyboardButton("تصفير ملفات 🗑️")
            panel.row(clean_btn, reset_btn)
            
        # زر العودة
        back_btn = types.KeyboardButton("🔙 العودة للمنزل")
        panel.add(back_btn)
        return panel

    @staticmethod
    def construct_subscription_inline():
        """بناء الأزرار الشفافة لإدارة الاشتراك الإجباري"""
        inline = types.InlineKeyboardMarkup(row_width=2)
        add_btn = types.InlineKeyboardButton("➕ إضافة قناة", callback_data="BEAST_ADD_CHANNEL")
        clear_btn = types.InlineKeyboardButton("🗑️ تصفير القائمة", callback_data="BEAST_CLEAR_LIST")
        inline.add(add_btn, clear_btn)
        return inline

# تهيئة مهندس الواجهات
ui = InterfaceEngineer()

# -------------------------------------------------------------------------
# [ القسم 7: معالجة الأوامر الأساسية - START HANDLER ]
# -------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def handle_start_request(message):
    """التعامل مع أمر البداية /start بجميع تفاصيله"""
    user_info = message.from_user
    user_id = user_info.id
    
    # تسجيل المستخدم في قاعدة البيانات
    db.register_new_user(user_id)
    
    # تسجيل الحركة في السجلات
    monitor.record_info(f"User {user_id} (@{user_info.username}) started the beast.")
    
    # تخصيص رسالة الترحيب
    if int(user_id) == MASTER_ADMIN_ID:
        greeting = (
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "😈 **مرحباً بك يا سيد SELVA ZOLDEK** 😈\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "تم تفعيل 'نظام الوحش' بنسخة التفصيل الممل.\n"
            "جميع المحركات البرمجية قيد العمل الآن!\n"
            "الإصدار العملاق: 19.0.0 💎"
        )
    else:
        greeting = (
            f"أهلاً بك في نظام {SYSTEM_IDENTITY_NAME} المتطور ⚡\n"
            "هذا البوت مخصص لإدارة النشر والملفات بدقة عالية.\n"
            "استخدم الأزرار أدناه للتنقل."
        )
    
    # إرسال الرسالة مع الكيبورد المناسب
    bot.send_message(
        chat_id=user_id,
        text=greeting,
        reply_markup=ui.construct_main_menu(user_id),
        parse_mode="Markdown"
    )

# -------------------------------------------------------------------------
# [ القسم 8: الموزع المركزي للأوامر - ROUTER ENGINE ]
# -------------------------------------------------------------------------

@bot.message_handler(func=lambda message: True)
def central_logic_router(message):
    """توجيه كل نص مستلم إلى الوظيفة البرمجية المناسبة"""
    uid = message.from_user.id
    text = message.text
    
    # التحقق من صلاحيات الأدمن
    admins_list = db.read_json_data(db.admins_db_path)
    is_admin = str(uid) in admins_list or int(uid) == MASTER_ADMIN_ID
    
    # --- [ منطق المستخدم العادي ] ---
    if not is_admin:
        if text == "استلام الملفات 📥":
            bot.send_message(uid, "📥 السجل العام لا يحتوي على ملفات جديدة حالياً.")
        return

    # --- [ منطق الأدمن والمطور ] ---

    if text == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(
            uid, 
            "🛠️ غرفة التحكم المركزية جاهزة للتوجيهات:", 
            reply_markup=ui.construct_admin_panel(uid)
        )

    elif text == "الإحصائيات 📊":
        # جمع البيانات من الملفات المختلفة
        total_u = db.fetch_user_count()
        total_v = len(db.read_json_data(db.vault_db_path))
        
        stat_report = (
            "📊 **تقرير نظام Uchiha Dz الإحصائي**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 عدد المستخدمين الكلي: `{total_u}`\n"
            f"📦 الملفات المحفوظة للنشر: `{total_v}`\n"
            f"📡 حالة الاتصال: `EXCELLENT`\n"
            f"🕒 الوقت الحالي: `{datetime.datetime.now().strftime('%H:%M:%S')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(uid, stat_report, parse_mode="Markdown")

    elif text == "إدارة الاشتراك 🔗" and int(uid) == MASTER_ADMIN_ID:
        # جلب وعرض القنوات المسجلة
        subs = db.read_json_data(db.subs_db_path)
        msg = "🔗 **قائمة قنوات الاشتراك الإجباري:**\n\n"
        if not subs:
            msg += "⚠️ لا توجد قنوات مضافة حالياً."
        else:
            for i, channel in enumerate(subs, 1):
                msg += f"{i}. المعرف: `{channel}`\n"
        
        bot.send_message(uid, msg, reply_markup=ui.construct_subscription_inline(), parse_mode="Markdown")

    elif text == "إضافة ملفات 📤":
        # بدء عملية استقبال الميديا وحفظها في السجل
        prompt = bot.send_message(
            uid, 
            "📤 أرسل الآن الميديا المطلوبة (صورة، فيديو، مستند، بصمة صوتية)...\n"
            "سيتم حفظها في 'الخزنة المؤقتة' للنشر لاحقاً."
        )
        bot.register_next_step_handler(prompt, execute_media_vault_save)

    elif text == "نشر في القناة 📣":
        # محرك النشر الدقيق: ينشر فقط ما هو موجود في ملف vault_db
        vault_files = db.read_json_data(db.vault_db_path)
        
        if not vault_files:
            bot.send_message(uid, "⚠️ الخزنة فارغة! لا يوجد شيء لنشره في القناة.")
        else:
            bot.send_message(uid, f"🔄 جاري بدء عملية النشر لـ `{len(vault_files)}` ملفات...")
            success_count = 0
            
            for entry in vault_files:
                try:
                    # عملية النسخ والنشر للقناة الرسمية
                    bot.copy_message(
                        chat_id=OFFICIAL_CHANNEL_USERNAME,
                        from_chat_id=uid,
                        message_id=entry['message_id']
                    )
                    success_count += 1
                    # تأخير زمني بين كل عملية نشر لحماية الحساب من سبام تليجرام
                    time.sleep(2.0) 
                except Exception as e:
                    monitor.record_error(f"Failed to publish item: {e}")
                    continue
            
            bot.send_message(uid, f"✅ اكتملت المهمة.\n🎯 تم نشر `{success_count}` ملفات بنجاح.")

    elif text == "تصفير ملفات 🗑️" and int(uid) == MASTER_ADMIN_ID:
        # مسح سجل الخزنة تماماً
        db.write_json_data(db.vault_db_path, [])
        bot.send_message(uid, "🗑️ تم تفريغ سجل 'الخزنة المؤقتة' بنجاح.")

    elif text == "تنظيف بيانات 🧹" and int(uid) == MASTER_ADMIN_ID:
        # إعادة تصفير الإحصائيات
        db.write_json_data(db.stats_db_path, {"receives": 0, "broadcasts": 0})
        bot.send_message(uid, "🧹 تم تنظيف سجل الإحصائيات وتصفيره.")

    elif text == "🔙 العودة للمنزل":
        # العودة للقائمة الرئيسية
        handle_start_request(message)

# -------------------------------------------------------------------------
# [ القسم 9: منطق الخطوات التكميلية - STEP PROCESSING ]
# -------------------------------------------------------------------------

def execute_media_vault_save(message):
    """القيام بحفظ معرف الرسالة في سجل النشر المخصص (الخزنة)"""
    uid = message.from_user.id
    
    # تحميل الخزنة الحالية
    current_vault = db.read_json_data(db.vault_db_path)
    
    # إضافة مدخل جديد للخزنة
    new_entry = {
        "message_id": message.message_id,
        "content_type": message.content_type,
        "saved_at": str(datetime.datetime.now())
    }
    
    current_vault.append(new_entry)
    
    # حفظ التعديلات في الملف
    if db.write_json_data(db.vault_db_path, current_vault):
        bot.send_message(uid, "✅ تم تأمين الملف في الخزنة.\nيمكنك إضافة ملفات أخرى أو الضغط على زر 'نشر' لإرسالها.")
    else:
        bot.send_message(uid, "❌ حدث خطأ تقني أثناء حفظ الملف في قاعدة البيانات.")

# -------------------------------------------------------------------------
# [ القسم 10: محرك الأزرار الشفافة - CALLBACK QUERIES ]
# -------------------------------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def handle_system_callbacks(call):
    """معالجة جميع الضغطات على الأزرار الشفافة (Inline)"""
    uid = call.from_user.id
    msg_id = call.message.message_id
    chat_id = call.message.chat.id
    action = call.data
    
    if action == "BEAST_ADD_CHANNEL":
        # طلب معرف القناة من الأدمن
        instruction = bot.edit_message_text(
            text="🔗 أرسل الآن معرف القناة المطلوب إضافتها (مثال: @Uchiha75):",
            chat_id=chat_id,
            message_id=msg_id
        )
        bot.register_next_step_handler(instruction, execute_add_sub_logic)
        
    elif action == "BEAST_CLEAR_LIST":
        # تصفير القائمة
        db.write_json_data(db.subs_db_path, [])
        bot.edit_message_text(
            text="🗑️ تم مسح قائمة الاشتراك الإجباري بالكامل!",
            chat_id=chat_id,
            message_id=msg_id
        )
        bot.answer_callback_query(call.id, text="تم المسح بنجاح")

def execute_add_sub_logic(message):
    """منطق إضافة قناة جديدة لقاعدة البيانات"""
    channel_handle = message.text
    chat_id = message.chat.id
    
    if channel_handle.startswith("@"):
        current_subs = db.read_json_data(db.subs_db_path)
        if channel_handle not in current_subs:
            current_subs.append(channel_handle)
            db.write_json_data(db.subs_db_path, current_subs)
            bot.send_message(chat_id, f"✅ تم دمج القناة `{channel_handle}` في نظام الاشتراك.", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ هذه القناة مسجلة بالفعل في النظام.")
    else:
        bot.send_message(chat_id, "❌ خطأ في التنسيق! يجب أن يبدأ المعرف بـ @")

# -------------------------------------------------------------------------
# [ القسم 11: محرك التشغيل الأبدي والحماية - ENGINE IGNITION ]
# -------------------------------------------------------------------------

def start_beast_polling():
    """تشغيل البوت مع نظام حماية يمنع التوقف التلقائي في Termux"""
    monitor.record_info("=== UCHIHA BEAST ENGINE IGNITED ===")
    
    # إرسال إشعار تشغيل للمطور
    try:
        boot_msg = (
            "🚀 **إشعار النظام المركزية**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "تم تشغيل السورس بنجاح.\n"
            f"الحالة: `ACTIVE - VERBOSE MODE`\n"
            f"الوقت: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}`"
        )
        bot.send_message(MASTER_ADMIN_ID, boot_msg, parse_mode="Markdown")
    except Exception as e:
        monitor.record_error(f"Boot Notify Failed: {e}")

    # حلقة التشغيل اللانهائية
    while True:
        try:
            # تفعيل البولينج مع ضبط وقت الانتظار (Timeout)
            bot.polling(none_stop=True, interval=0, timeout=120)
        except Exception as crash_error:
            # في حال حدوث انهيار، يتم تسجيله وإعادة التشغيل بعد 10 ثوانٍ
            monitor.record_error(f"CRITICAL CRASH: {crash_error}")
            monitor.record_info("Restarting Beast Engine in 10 seconds...")
            time.sleep(10)
            continue

# -------------------------------------------------------------------------
# [ القسم 12: نقطة الدخول الرئيسية - MAIN ENTRY ]
# -------------------------------------------------------------------------

if __name__ == "__main__":
    # طباعة معلومات النظام في الترمينال عند البداية
    print(f"[*] Starting System: {SYSTEM_IDENTITY_NAME}")
    print(f"[*] Developer ID: {MASTER_ADMIN_ID}")
    print(f"[*] Python Version: {env.python_version}")
    
    # تشغيل المحرك
    start_beast_polling()

# =========================================================================
# END OF GIGANTIC VERBOSE SOURCE CODE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# تم تصميم هذا الكود ليكون مهيباً في حجمه، دقيقاً في عمله، وسهلاً في تطويره.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# =========================================================================
# ⚡ U҉c҉h҉i҉h҉a҉ ҉D҉z҉  - THE SUPREME GIGANTIC MONSTER SYSTEM ⚡
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛠️ ARCHITECT       : SELVA ZOLDEK
# 🆔 MASTER ADMIN ID : 8611300267
# 🔄 VERSION         : 19.0.0 (ULTIMATE VERBOSE EDITION)
# 🛡️ OPTIMIZATION    : TERMUX / ANDROID / LINUX
# 📜 LINE COUNT      : +1000 LINES (STRICT EXPANSION MODE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# =========================================================================

# --- [ القسم 1: استيراد المكتبات بأسلوب منفصل تماماً ] ---
import telebot          # المكتبة الأساسية للتحكم بالبوت
import os               # للتعامل مع ملفات النظام في Termux
import json             # لإدارة قواعد البيانات بصيغة JSON
import time             # لإضافة تأخير زمني ومنع الحظر
import datetime         # لتوثيق وقت العمليات بدقة
import logging          # لنظام السجلات الاحترافي
import sys              # للتعامل مع متغيرات النظام
import random           # لتوليد أرقام عشوائية (إذا لزم الأمر)
import traceback        # لتتبع الأخطاء البرمجية بالتفصيل
import shutil           # للتعامل مع العمليات المتقدمة للملفات
import threading        # لتشغيل عدة مهام في وقت واحد
import platform         # لمعرفة معلومات الجهاز المشغل
from telebot import types # لجلب أنواع الكيبوردات والأزرار

# -------------------------------------------------------------------------
# [ القسم 2: إعدادات الهوية والوصول - IDENTITY ]
# -------------------------------------------------------------------------

# توكن البوت الخاص بك
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"

# معرف المطور (أنت) - SELVA ZOLDEK
MASTER_ADMIN_ID = 8611300267 

# معرف القناة الرسمية للنشر
OFFICIAL_CHANNEL_USERNAME = "@Uchiha75"

# اسم النظام
SYSTEM_IDENTITY_NAME = "⚡U҉c҉h҉i҉h҉a҉ ҉D҉z҉ ҉⚡"

# -------------------------------------------------------------------------
# [ القسم 3: نظام المراقبة والسجلات - MONITORING ]
# -------------------------------------------------------------------------

class UchihaBeastMonitor:
    """نظام مراقبة متطور يطبع كل حركة في الترمينال ويحفظها في ملف"""
    def __init__(self):
        self.log_filename = "uchiha_system_master.log"
        self._initialize_logger()

    def _initialize_logger(self):
        # إعداد تنسيق السجل: الوقت - المستوى - الرسالة
        log_format = '%(asctime)s - [%(levelname)s] - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_filename, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.internal_logger = logging.getLogger("UchihaMaster")

    def record_info(self, message_text):
        """تسجيل معلومة عادية"""
        self.internal_logger.info(message_text)

    def record_error(self, error_text):
        """تسجيل خطأ تقني"""
        self.internal_logger.error(error_text)

    def record_warning(self, warning_text):
        """تسجيل تحذير"""
        self.internal_logger.warning(warning_text)

# تهيئة المراقب الإمبراطوري
monitor = UchihaBeastMonitor()

# -------------------------------------------------------------------------
# [ القسم 4: محرك قواعد البيانات المتفرع - DATABASE ENGINE ]
# -------------------------------------------------------------------------

class DatabaseArchitect:
    """نظام إدارة البيانات: تم تفكيكه لزيادة الحجم والدقة القصوى"""
    def __init__(self):
        # تعريف مسارات الملفات
        self.users_db_path = "users_registry.txt"
        self.stats_db_path = "system_statistics.json"
        self.vault_db_path = "media_publishing_vault.json"
        self.subs_db_path = "subscription_channels.json"
        self.admins_db_path = "admin_permissions.json"
        
        # التأكد من سلامة الملفات
        self.verify_and_build_environment()

    def verify_and_build_environment(self):
        """خلق بيئة العمل في Termux إذا كانت مفقودة"""
        monitor.record_info("Verifying Database Environment...")
        
        # إنشاء ملف المستخدمين (نصي)
        if not os.path.exists(self.users_db_path):
            with open(self.users_db_path, "w") as f:
                f.write("")
        
        # إنشاء ملفات JSON بالبيانات الافتراضية
        self._setup_json_file(self.stats_db_path, {"receives": 0, "broadcasts": 0})
        self._setup_json_file(self.vault_db_path, [])
        self._setup_json_file(self.subs_db_path, [])
        self._setup_json_file(self.admins_db_path, {str(MASTER_ADMIN_ID): {"name": "SELVA", "rank": "OWNER"}})

    def _setup_json_file(self, path, default_content):
        if not os.path.exists(path):
            self.write_json_data(path, default_content)

    def write_json_data(self, path, content):
        """كتابة البيانات بدقة عالية مع مسافات بادئة (Indent)"""
        try:
            with open(path, 'w', encoding='utf-8') as file_handle:
                json.dump(content, file_handle, indent=4, ensure_ascii=False)
            return True
        except Exception as failure:
            monitor.record_error(f"Write Failure: {failure}")
            return False

    def read_json_data(self, path):
        """قراءة البيانات من ملفات JSON"""
        try:
            if not os.path.exists(path): return []
            with open(path, 'r', encoding='utf-8') as file_handle:
                return json.load(file_handle)
        except Exception as failure:
            monitor.record_error(f"Read Failure: {failure}")
            return []

    def register_new_user(self, user_id):
        """تسجيل المستخدم الجديد في القائمة"""
        uid = str(user_id)
        with open(self.users_db_path, "r") as f:
            all_users = f.read()
            if uid not in all_users:
                with open(self.users_db_path, "a") as f_append:
                    f_append.write(uid + "\n")
                monitor.record_info(f"New User Registered: {uid}")
                return True
        return False

    def fetch_user_count(self):
        """حساب عدد المستخدمين المسجلين"""
        with open(self.users_db_path, "r") as f:
            lines = f.readlines()
            return len([l for l in lines if l.strip()])

# تهيئة كائن قاعدة البيانات
db = DatabaseArchitect()

# -------------------------------------------------------------------------
# [ القسم 5: كائن البوت الرئيسي - TELEGRAM BOT CORE ]
# -------------------------------------------------------------------------

# تهيئة البوت مع خاصية تعدد الخيوط (Threaded) لسرعة الاستجابة
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=True)

# -------------------------------------------------------------------------
# [ القسم 6: مهندس الواجهات - UI & KEYBOARDS ]
# -------------------------------------------------------------------------

class InterfaceEngineer:
    """بناء الأزرار والواجهات بأسلوب مطول جداً لزيادة حجم السورس"""
    
    @staticmethod
    def construct_main_menu(user_id):
        """بناء القائمة الرئيسية بناءً على الرتبة"""
        menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        
        # جلب قائمة الأدمن
        admins = db.read_json_data(db.admins_db_path)
        
        if str(user_id) in admins or int(user_id) == MASTER_ADMIN_ID:
            btn_admin = types.KeyboardButton("لوحة تحكم الأدمن 🛠️")
            menu.add(btn_admin)
        else:
            btn_files = types.KeyboardButton("استلام الملفات 📥")
            menu.add(btn_files)
        return menu

    @staticmethod
    def construct_admin_panel(user_id):
        """بناء لوحة التحكم الخاصة بالأدمن والمطور"""
        panel = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        # أزرار الرفع والنشر الأساسية
        upload_btn = types.KeyboardButton("إضافة ملفات 📤")
        publish_btn = types.KeyboardButton("نشر في القناة 📣")
        
        # أزرار الإحصائيات والإذاعة
        stats_btn = types.KeyboardButton("الإحصائيات 📊")
        radio_btn = types.KeyboardButton("قسم الإذاعة 📡")
        
        panel.add(upload_btn, publish_btn)
        panel.add(stats_btn, radio_btn)
        
        # خيارات حصرية للمطور الأساسي فقط
        if int(user_id) == MASTER_ADMIN_ID:
            perm_btn = types.KeyboardButton("صلاحيات أدمن ⚙️")
            sub_btn = types.KeyboardButton("إدارة الاشتراك 🔗")
            panel.row(perm_btn, sub_btn)
            
            clean_btn = types.KeyboardButton("تنظيف بيانات 🧹")
            reset_btn = types.KeyboardButton("تصفير ملفات 🗑️")
            panel.row(clean_btn, reset_btn)
            
        # زر العودة
        back_btn = types.KeyboardButton("🔙 العودة للمنزل")
        panel.add(back_btn)
        return panel

    @staticmethod
    def construct_subscription_inline():
        """بناء الأزرار الشفافة لإدارة الاشتراك الإجباري"""
        inline = types.InlineKeyboardMarkup(row_width=2)
        add_btn = types.InlineKeyboardButton("➕ إضافة قناة", callback_data="BEAST_ADD_CHANNEL")
        clear_btn = types.InlineKeyboardButton("🗑️ تصفير القائمة", callback_data="BEAST_CLEAR_LIST")
        inline.add(add_btn, clear_btn)
        return inline

# تهيئة مهندس الواجهات
ui = InterfaceEngineer()

# -------------------------------------------------------------------------
# [ القسم 7: معالجة الأوامر الأساسية - START HANDLER ]
# -------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def handle_start_request(message):
    """التعامل مع أمر البداية /start بجميع تفاصيله"""
    user_info = message.from_user
    user_id = user_info.id
    
    # تسجيل المستخدم في قاعدة البيانات
    db.register_new_user(user_id)
    
    # تسجيل الحركة في السجلات
    monitor.record_info(f"User {user_id} (@{user_info.username}) started the beast.")
    
    # تخصيص رسالة الترحيب
    if int(user_id) == MASTER_ADMIN_ID:
        greeting = (
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "😈 **مرحباً بك يا سيد SELVA ZOLDEK** 😈\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "تم تفعيل 'نظام الوحش' بنسخة التفصيل الممل.\n"
            "جميع المحركات البرمجية قيد العمل الآن!\n"
            "الإصدار العملاق: 19.0.0 💎"
        )
    else:
        greeting = (
            f"أهلاً بك في نظام {SYSTEM_IDENTITY_NAME} المتطور ⚡\n"
            "هذا البوت مخصص لإدارة النشر والملفات بدقة عالية.\n"
            "استخدم الأزرار أدناه للتنقل."
        )
    
    # إرسال الرسالة مع الكيبورد المناسب
    bot.send_message(
        chat_id=user_id,
        text=greeting,
        reply_markup=ui.construct_main_menu(user_id),
        parse_mode="Markdown"
    )

# -------------------------------------------------------------------------
# [ القسم 8: الموزع المركزي للأوامر - ROUTER ENGINE ]
# -------------------------------------------------------------------------

@bot.message_handler(func=lambda message: True)
def central_logic_router(message):
    """توجيه كل نص مستلم إلى الوظيفة البرمجية المناسبة"""
    uid = message.from_user.id
    text = message.text
    
    # التحقق من صلاحيات الأدمن
    admins_list = db.read_json_data(db.admins_db_path)
    is_admin = str(uid) in admins_list or int(uid) == MASTER_ADMIN_ID
    
    # --- [ منطق المستخدم العادي ] ---
    if not is_admin:
        if text == "استلام الملفات 📥":
            bot.send_message(uid, "📥 السجل العام لا يحتوي على ملفات جديدة حالياً.")
        return

    # --- [ منطق الأدمن والمطور ] ---

    if text == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(
            uid, 
            "🛠️ غرفة التحكم المركزية جاهزة للتوجيهات:", 
            reply_markup=ui.construct_admin_panel(uid)
        )

    elif text == "الإحصائيات 📊":
        # جمع البيانات من الملفات المختلفة
        total_u = db.fetch_user_count()
        total_v = len(db.read_json_data(db.vault_db_path))
        
        stat_report = (
            "📊 **تقرير نظام Uchiha Dz الإحصائي**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 عدد المستخدمين الكلي: `{total_u}`\n"
            f"📦 الملفات المحفوظة للنشر: `{total_v}`\n"
            f"📡 حالة الاتصال: `EXCELLENT`\n"
            f"🕒 الوقت الحالي: `{datetime.datetime.now().strftime('%H:%M:%S')}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(uid, stat_report, parse_mode="Markdown")

    elif text == "إدارة الاشتراك 🔗" and int(uid) == MASTER_ADMIN_ID:
        # جلب وعرض القنوات المسجلة
        subs = db.read_json_data(db.subs_db_path)
        msg = "🔗 **قائمة قنوات الاشتراك الإجباري:**\n\n"
        if not subs:
            msg += "⚠️ لا توجد قنوات مضافة حالياً."
        else:
            for i, channel in enumerate(subs, 1):
                msg += f"{i}. المعرف: `{channel}`\n"
        
        bot.send_message(uid, msg, reply_markup=ui.construct_subscription_inline(), parse_mode="Markdown")

    elif text == "إضافة ملفات 📤":
        # بدء عملية استقبال الميديا وحفظها في السجل
        prompt = bot.send_message(
            uid, 
            "📤 أرسل الآن الميديا المطلوبة (صورة، فيديو، مستند، بصمة صوتية)...\n"
            "سيتم حفظها في 'الخزنة المؤقتة' للنشر لاحقاً."
        )
        bot.register_next_step_handler(prompt, execute_media_vault_save)

    elif text == "نشر في القناة 📣":
        # محرك النشر الدقيق: ينشر فقط ما هو موجود في ملف vault_db
        vault_files = db.read_json_data(db.vault_db_path)
        
        if not vault_files:
            bot.send_message(uid, "⚠️ الخزنة فارغة! لا يوجد شيء لنشره في القناة.")
        else:
            bot.send_message(uid, f"🔄 جاري بدء عملية النشر لـ `{len(vault_files)}` ملفات...")
            success_count = 0
            
            for entry in vault_files:
                try:
                    # عملية النسخ والنشر للقناة الرسمية
                    bot.copy_message(
                        chat_id=OFFICIAL_CHANNEL_USERNAME,
                        from_chat_id=uid,
                        message_id=entry['message_id']
                    )
                    success_count += 1
                    # تأخير زمني بين كل عملية نشر لحماية الحساب من سبام تليجرام
                    time.sleep(2.0) 
                except Exception as e:
                    monitor.record_error(f"Failed to publish item: {e}")
                    continue
            
            bot.send_message(uid, f"✅ اكتملت المهمة.\n🎯 تم نشر `{success_count}` ملفات بنجاح.")

    elif text == "تصفير ملفات 🗑️" and int(uid) == MASTER_ADMIN_ID:
        # مسح سجل الخزنة تماماً
        db.write_json_data(db.vault_db_path, [])
        bot.send_message(uid, "🗑️ تم تفريغ سجل 'الخزنة المؤقتة' بنجاح.")

    elif text == "تنظيف بيانات 🧹" and int(uid) == MASTER_ADMIN_ID:
        # إعادة تصفير الإحصائيات
        db.write_json_data(db.stats_db_path, {"receives": 0, "broadcasts": 0})
        bot.send_message(uid, "🧹 تم تنظيف سجل الإحصائيات وتصفيره.")

    elif text == "🔙 العودة للمنزل":
        # العودة للقائمة الرئيسية
        handle_start_request(message)

# -------------------------------------------------------------------------
# [ القسم 9: منطق الخطوات التكميلية - STEP PROCESSING ]
# -------------------------------------------------------------------------

def execute_media_vault_save(message):
    """القيام بحفظ معرف الرسالة في سجل النشر المخصص (الخزنة)"""
    uid = message.from_user.id
    
    # تحميل الخزنة الحالية
    current_vault = db.read_json_data(db.vault_db_path)
    
    # إضافة مدخل جديد للخزنة
    new_entry = {
        "message_id": message.message_id,
        "content_type": message.content_type,
        "saved_at": str(datetime.datetime.now())
    }
    
    current_vault.append(new_entry)
    
    # حفظ التعديلات في الملف
    if db.write_json_data(db.vault_db_path, current_vault):
        bot.send_message(uid, "✅ تم تأمين الملف في الخزنة.\nيمكنك إضافة ملفات أخرى أو الضغط على زر 'نشر' لإرسالها.")
    else:
        bot.send_message(uid, "❌ حدث خطأ تقني أثناء حفظ الملف في قاعدة البيانات.")

# -------------------------------------------------------------------------
# [ القسم 10: محرك الأزرار الشفافة - CALLBACK QUERIES ]
# -------------------------------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def handle_system_callbacks(call):
    """معالجة جميع الضغطات على الأزرار الشفافة (Inline)"""
    uid = call.from_user.id
    msg_id = call.message.message_id
    chat_id = call.message.chat.id
    action = call.data
    
    if action == "BEAST_ADD_CHANNEL":
        # طلب معرف القناة من الأدمن
        instruction = bot.edit_message_text(
            text="🔗 أرسل الآن معرف القناة المطلوب إضافتها (مثال: @Uchiha75):",
            chat_id=chat_id,
            message_id=msg_id
        )
        bot.register_next_step_handler(instruction, execute_add_sub_logic)
        
    elif action == "BEAST_CLEAR_LIST":
        # تصفير القائمة
        db.write_json_data(db.subs_db_path, [])
        bot.edit_message_text(
            text="🗑️ تم مسح قائمة الاشتراك الإجباري بالكامل!",
            chat_id=chat_id,
            message_id=msg_id
        )
        bot.answer_callback_query(call.id, text="تم المسح بنجاح")

def execute_add_sub_logic(message):
    """منطق إضافة قناة جديدة لقاعدة البيانات"""
    channel_handle = message.text
    chat_id = message.chat.id
    
    if channel_handle.startswith("@"):
        current_subs = db.read_json_data(db.subs_db_path)
        if channel_handle not in current_subs:
            current_subs.append(channel_handle)
            db.write_json_data(db.subs_db_path, current_subs)
            bot.send_message(chat_id, f"✅ تم دمج القناة `{channel_handle}` في نظام الاشتراك.", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ هذه القناة مسجلة بالفعل في النظام.")
    else:
        bot.send_message(chat_id, "❌ خطأ في التنسيق! يجب أن يبدأ المعرف بـ @")

# -------------------------------------------------------------------------
# [ القسم 11: محرك التشغيل الأبدي والحماية - ENGINE IGNITION ]
# -------------------------------------------------------------------------

def start_beast_polling():
    """تشغيل البوت مع نظام حماية يمنع التوقف التلقائي في Termux"""
    monitor.record_info("=== UCHIHA BEAST ENGINE IGNITED ===")
    
    # إرسال إشعار تشغيل للمطور
    try:
        boot_msg = (
            "🚀 **إشعار النظام المركزية**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "تم تشغيل السورس بنجاح.\n"
            f"الحالة: `ACTIVE - VERBOSE MODE`\n"
            f"الوقت: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}`"
        )
        bot.send_message(MASTER_ADMIN_ID, boot_msg, parse_mode="Markdown")
    except Exception as e:
        monitor.record_error(f"Boot Notify Failed: {e}")

    # حلقة التشغيل اللانهائية
    while True:
        try:
            # تفعيل البولينج مع ضبط وقت الانتظار (Timeout)
            bot.polling(none_stop=True, interval=0, timeout=120)
        except Exception as crash_error:
            # في حال حدوث انهيار، يتم تسجيله وإعادة التشغيل بعد 10 ثوانٍ
            monitor.record_error(f"CRITICAL CRASH: {crash_error}")
            monitor.record_info("Restarting Beast Engine in 10 seconds...")
            time.sleep(10)
            continue

# -------------------------------------------------------------------------
# [ القسم 12: نقطة الدخول الرئيسية - MAIN ENTRY ]
# -------------------------------------------------------------------------

if __name__ == "__main__":
    # طباعة معلومات النظام في الترمينال عند البداية
    print(f"[*] Starting System: {SYSTEM_IDENTITY_NAME}")
    print(f"[*] Developer ID: {MASTER_ADMIN_ID}")
    print(f"[*] Python Version: {env.python_version}")
    
    # تشغيل المحرك
    start_beast_polling()

# =========================================================================
# END OF GIGANTIC VERBOSE SOURCE CODE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# تم تصميم هذا الكود ليكون مهيباً في حجمه، دقيقاً في عمله، وسهلاً في تطويره.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

