# =========================================================================
# ⚡ U҉c҉h҉i҉h҉a҉ ҉D҉z҉  - THE SUPREME GIGANTIC MONSTER SYSTEM ⚡
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛠️ ARCHITECT       : SELVA ZOLDEK
# 🆔 MASTER ADMIN ID : 8611300267
# 🔄 VERSION         : 99.0.0 (ULTIMATE VERBOSE & EXPANDED EDITION)
# 🛡️ OPTIMIZATION    : TERMUX / ANDROID / LINUX / VPS
# 📜 DESIGN PATTERN   : MULTI-LAYERED ARCHITECTURE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# =========================================================================

# -------------------------------------------------------------------------
# [ القسم 1: استيراد المكتبات بأسلوب منفصل تماماً ]
# -------------------------------------------------------------------------
import telebot          
import os               
import json             
import time             
import datetime         
import logging          
import sys              
import random           
import traceback        
import shutil           
import threading        
import platform         
import socket           
from telebot import types 

# -------------------------------------------------------------------------
# [ القسم 2: الثوابت الإمبراطورية - CORE CONSTANTS ]
# -------------------------------------------------------------------------

BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
MASTER_ADMIN_ID = 8611300267 
OFFICIAL_CHANNEL_USERNAME = "@Uchiha75"
SYSTEM_IDENTITY_NAME = "⚡U҉c҉h҉i҉h҉a҉ ҉D҉z҉ ҉⚡"
START_TIME = datetime.datetime.now()

# -------------------------------------------------------------------------
# [ القسم 3: محرك السجلات العملاق - THE BEAST MONITOR ]
# -------------------------------------------------------------------------

class SystemLogger:
    """نظام مراقبة احترافي يسجل كل صغيرة وكبيرة في ملف خارجي"""
    def __init__(self):
        self.filename = "uchiha_master_log.txt"
        self._setup_logging()

    def _setup_logging(self):
        fmt = '%(asctime)s | %(levelname)s | %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=fmt,
            handlers=[
                logging.FileHandler(self.filename, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("UchihaBeast")

    def log_action(self, user_id, action):
        self.logger.info(f"USER[{user_id}] -> ACTION: {action}")

    def log_error(self, error_msg):
        self.logger.error(f"CRITICAL ERROR: {error_msg}")

monitor = SystemLogger()

# -------------------------------------------------------------------------
# [ القسم 4: مهندس قواعد البيانات المركزية - DATABASE ARCHITECT ]
# -------------------------------------------------------------------------

class DatabaseArchitect:
    """نظام إدارة البيانات: تفكيك كامل للملفات لزيادة الحجم والدقة"""
    def __init__(self):
        self.paths = {
            "users": "db_users.txt",
            "stats": "db_stats.json",
            "admins": "db_admins.json",
            "subs": "db_subs.json",
            "vault": "db_vault.json",
            "settings": "db_settings.json",
            "blacklist": "db_blacklist.txt"
        }
        self.build_environment()

    def build_environment(self):
        monitor.log_action("SYSTEM", "Building Database Environment...")
        # إنشاء الملفات النصية
        for key in ["users", "blacklist"]:
            if not os.path.exists(self.paths[key]):
                with open(self.paths[key], "w") as f: f.write("")
        
        # إنشاء ملفات JSON
        self._init_json("stats", {"receives": 0, "broadcasts": 0, "total_messages": 0})
        self._init_json("vault", [])
        self._init_json("subs", [])
        self._init_json("settings", {"maintenance": False, "welcome_msg": "أهلاً بك في النظام"})
        self._init_json("admins", {
            str(MASTER_ADMIN_ID): {
                "name": "SELVA ZOLDEK",
                "perms": {"upload": True, "publish": True, "stats": True, "clean": True, "reset": True, "broadcast": True}
            }
        })

    def _init_json(self, key, default):
        if not os.path.exists(self.paths[key]):
            self.save_json(key, default)

    def save_json(self, key, data):
        try:
            with open(self.paths[key], 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e: monitor.log_error(f"Save Failed: {e}")

    def get_json(self, key):
        try:
            with open(self.paths[key], 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}

    def register_user(self, uid):
        with open(self.paths["users"], "r") as f:
            if str(uid) not in f.read():
                with open(self.paths["users"], "a") as fa:
                    fa.write(str(uid) + "\n")
                return True
        return False

    def is_blacklisted(self, uid):
        with open(self.paths["blacklist"], "r") as f:
            return str(uid) in f.read()

db = DatabaseArchitect()

# -------------------------------------------------------------------------
# [ القسم 5: مدير الصلاحيات والأمان - SECURITY MANAGER ]
# -------------------------------------------------------------------------

class SecurityManager:
    """نظام فحص الرتب والتحقق من الهوية برمجياً"""
    @staticmethod
    def is_master(uid):
        return int(uid) == MASTER_ADMIN_ID

    @staticmethod
    def has_permission(uid, permission):
        if SecurityManager.is_master(uid): return True
        admins = db.get_json("admins")
        if str(uid) in admins:
            return admins[str(uid)]["perms"].get(permission, False)
        return False

security = SecurityManager()

# -------------------------------------------------------------------------
# [ القسم 6: مهندس واجهات المستخدم - UI & KEYBOARDS ]
# -------------------------------------------------------------------------

class InterfaceEngineer:
    """تصميم الأزرار بأسلوب مطول جداً لضمان عدم حدوث تداخل"""
    
    @staticmethod
    def main_menu(uid):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        if str(uid) in db.get_json("admins") or security.is_master(uid):
            markup.add(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"))
        else:
            markup.add(types.KeyboardButton("استلام الملفات 📥"))
            markup.add(types.KeyboardButton("تواصل مع المطور 👨‍💻"))
        return markup

    @staticmethod
    def admin_panel(uid):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        # تنظيم الأزرار في صفوف منفصلة لزيادة الحجم
        btn1 = types.KeyboardButton("إضافة ملفات 📤")
        btn2 = types.KeyboardButton("نشر في القناة 📣")
        btn3 = types.KeyboardButton("الإحصائيات 📊")
        btn4 = types.KeyboardButton("قسم الإذاعة 📡")
        
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        
        if security.is_master(uid):
            btn5 = types.KeyboardButton("صلاحيات أدمن ⚙️")
            btn6 = types.KeyboardButton("إدارة الاشتراك 🔗")
            btn7 = types.KeyboardButton("تنظيف بيانات 🧹")
            btn8 = types.KeyboardButton("تصفير ملفات 🗑️")
            markup.add(btn5, btn6)
            markup.add(btn7, btn8)
            
        markup.add(types.KeyboardButton("🔙 العودة للمنزل"))
        return markup

    @staticmethod
    def broadcast_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(
            types.KeyboardButton("إذاعة مستخدمين 👤"),
            types.KeyboardButton("إذاعة قناة 📣"),
            types.KeyboardButton("إذاعة الجميع 🌍"),
            types.KeyboardButton("لوحة تحكم الأدمن 🛠️")
        )
        return markup

    @staticmethod
    def admin_management_inline(target_id):
        # بناء لوحة الصلاحيات الستة الشهيرة
        markup = types.InlineKeyboardMarkup(row_width=2)
        perms = db.get_json("admins")[str(target_id)]["perms"]
        
        keys = {
            "upload": "رفع ملف 📤",
            "publish": "نشر 📣",
            "stats": "إحصائيات 📊",
            "clean": "تنظيف 🧹",
            "reset": "تصفير 🗑️",
            "broadcast": "إذاعة 📡"
        }
        
        for k, v in keys.items():
            status = "✅" if perms[k] else "❌"
            markup.add(types.InlineKeyboardButton(f"{v}: {status}", callback_data=f"PERM_{target_id}_{k}"))
            
        markup.add(types.InlineKeyboardButton("❌ طرد من الإدارة", callback_data=f"KICK_{target_id}"))
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة", callback_data="REFRESH_ADMINS"))
        return markup

ui = InterfaceEngineer()

# -------------------------------------------------------------------------
# [ القسم 7: قلب النظام - TELEGRAM BOT CORE ]
# -------------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=10)

# --- [ معالجة البداية ] ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    if db.is_blacklisted(uid): return
    
    db.register_user(uid)
    monitor.log_action(uid, "Triggered /start")
    
    if security.is_master(uid):
        msg = (
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "😈 **مرحباً بك يا سيد SELVA ZOLDEK** 😈\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "تم تشغيل 'نظام الوحش العملاق'.\n"
            "كل الأنظمة الفرعية تعمل بكفاءة 100%.\n"
            "الإصدار الحالي: 99.0.0 💎"
        )
    else:
        msg = f"أهلاً بك في نظام {SYSTEM_IDENTITY_NAME} المتكامل ⚡\nهذا البوت مخصص للإدارة والنشر الآلي."
        
    bot.send_message(uid, msg, reply_markup=ui.main_menu(uid), parse_mode="Markdown")

# --- [ الموزع المركزي للأوامر ] ---
@bot.message_handler(func=lambda m: True)
def router(message):
    uid, txt = message.from_user.id, message.text
    if db.is_blacklisted(uid): return

    # التحقق من الرتبة
    is_admin = str(uid) in db.get_json("admins") or security.is_master(uid)
    
    if not is_admin:
        if txt == "تواصل مع المطور 👨‍💻":
            bot.send_message(uid, "للتواصل مع المطور: @Uchiha75")
        return

    # --- منطق الأدمنية والمطور ---
    if txt == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(uid, "🛠️ غرفة التحكم المركزية جاهزة:", reply_markup=ui.admin_panel(uid))

    elif txt == "الإحصائيات 📊" and security.has_permission(uid, "stats"):
        st = db.get_json("stats")
        with open(db.paths["users"], "r") as f: u_count = len(f.readlines())
        uptime = datetime.datetime.now() - START_TIME
        
        report = (
            "📊 **تقرير النظام الإحصائي**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 عدد المستخدمين: `{u_count}`\n"
            f"📥 ملفات مستلمة: `{st.get('receives',0)}`\n"
            f"📡 إذاعات منجزة: `{st.get('broadcasts',0)}`\n"
            f"🕒 مدة التشغيل: `{str(uptime).split('.')[0]}`\n"
            f"🖥️ البيئة: `{platform.system()} ({platform.machine()})`"
        )
        bot.send_message(uid, report, parse_mode="Markdown")

    elif txt == "قسم الإذاعة 📡" and security.has_permission(uid, "broadcast"):
        bot.send_message(uid, "📡 اختر نوع الإذاعة المطلوبة:", reply_markup=ui.broadcast_menu())

    elif txt == "نشر في القناة 📣" and security.has_permission(uid, "publish"):
        m = bot.send_message(uid, "📣 أرسل المنشور (نص، صورة، فيديو) لنشره في القناة فوراً:")
        bot.register_next_step_handler(m, exec_publish)

    elif txt == "إضافة ملفات 📤" and security.has_permission(uid, "upload"):
        m = bot.send_message(uid, "📤 أرسل الملف الآن لحفظه في السجل:")
        bot.register_next_step_handler(m, exec_save_file)

    elif txt == "صلاحيات أدمن ⚙️" and security.is_master(uid):
        manage_admins_list(uid)

    elif txt == "🔙 العودة للمنزل":
        handle_start(message)

# -------------------------------------------------------------------------
# [ القسم 8: منطق التنفيذ العميق - EXECUTION LOGIC ]
# -------------------------------------------------------------------------

def exec_publish(message):
    try:
        bot.copy_message(OFFICIAL_CHANNEL_USERNAME, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ تم النشر بنجاح في القناة!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ فشل النشر: {e}")

def exec_save_file(message):
    # تحديث إحصائيات الاستلام
    st = db.get_json("stats")
    st["receives"] = st.get("receives", 0) + 1
    db.save_json("stats", st)
    bot.send_message(message.chat.id, "✅ تم استلام الملف وتوثيقه في الإحصائيات.")

def manage_admins_list(uid, mid=None):
    ads = db.get_json("admins")
    markup = types.InlineKeyboardMarkup()
    for aid, info in ads.items():
        if int(aid) != MASTER_ADMIN_ID:
            markup.add(types.InlineKeyboardButton(f"👤 {info['name']} ({aid})", callback_data=f"MNG_{aid}"))
    markup.add(types.InlineKeyboardButton("➕ إضافة أدمن جديد", callback_data="ADD_NEW_ADMIN"))
    
    text = "⚙️ إدارة طاقم العمل الصلاحيات:"
    if mid: bot.edit_message_text(text, uid, mid, reply_markup=markup)
    else: bot.send_message(uid, text, reply_markup=markup)

# -------------------------------------------------------------------------
# [ القسم 9: معالجة الـ Callback Queries ]
# -------------------------------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid, mid, data = call.from_user.id, call.message.message_id, call.data
    
    if data == "ADD_NEW_ADMIN" and security.is_master(uid):
        m = bot.edit_message_text("🆔 أرسل آيدي الأدمن الجديد الآن:", uid, mid)
        bot.register_next_step_handler(m, add_admin_logic)
        
    elif data.startswith("MNG_"):
        tid = data.split("_")[1]
        bot.edit_message_text(f"⚙️ إدارة صلاحيات `{tid}`:", uid, mid, reply_markup=ui.admin_management_inline(tid), parse_mode="Markdown")
        
    elif data.startswith("PERM_"):
        parts = data.split("_")
        tid, key = parts[1], parts[2]
        ads = db.get_json("admins")
        ads[tid]["perms"][key] = not ads[tid]["perms"][key]
        db.save_json("admins", ads)
        bot.edit_message_reply_markup(uid, mid, reply_markup=ui.admin_management_inline(tid))

    elif data == "REFRESH_ADMINS":
        manage_admins_list(uid, mid)

def add_admin_logic(message):
    new_id = message.text
    if new_id.isdigit():
        ads = db.get_json("admins")
        ads[new_id] = {
            "name": f"Admin_{new_id}",
            "perms": {k: False for k in ["upload", "publish", "stats", "clean", "reset", "broadcast"]}
        }
        db.save_json("admins", ads)
        bot.send_message(message.chat.id, f"✅ تم إضافة `{new_id}` للطاقم بنجاح.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ خطأ في الآيدي.")

# -------------------------------------------------------------------------
# [ القسم 10: محرك الحماية والتشغيل الأبدي - REIGN IGNITION ]
# -------------------------------------------------------------------------

def start_engine():
    """تشغيل البوت مع نظام استعادة تلقائي عند الانهيار"""
    monitor.log_action("SYSTEM", "IGNITING UCHIHA ENGINE...")
    print(f"[*] MASTER ID: {MASTER_ADMIN_ID}")
    print(f"[*] SYSTEM VERSION: 99.0.0")
    
    # إرسال إشعار تشغيل للمطور
    try:
        bot.send_message(MASTER_ADMIN_ID, "🚀 **نظام الوحش العملاق قيد العمل الآن**", parse_mode="Markdown")
    except: pass

    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=120)
        except Exception as e:
            monitor.log_error(f"ENGINE CRASH: {e}")
            monitor.log_action("SYSTEM", "RESTARTING IN 10 SECONDS...")
            time.sleep(10)
            continue

if __name__ == "__main__":
    start_engine()

# =========================================================================
# END OF GIGANTIC SUPREME SOURCE CODE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# تم تصميم هذا الكود ليكون مهيباً، منظماً، وقوياً جداً في الإدارة.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

