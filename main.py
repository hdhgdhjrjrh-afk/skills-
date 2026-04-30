# =========================================================================
# ⚡ Uchiha Dz - Ultimate Power Administration System ⚡
# 🛠️ Master Architect: SELVA ZOLDEK
# 🆔 Developer ID: 8611300267
# 🔄 Version: 10.0.0 (The Massive Architecture Edition)
# 🚫 NO CONTACT BUTTON | ✅ MANUAL BATCH SAVE | ✅ REPAIRED BUTTONS
# =========================================================================

import telebot
from telebot import types
import os
import json
import time
import logging
import datetime
import sys
import threading
import traceback
import platform

# --- [ 1. الهوية والاتصال ] ---

# توكن البوت
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
# هوية المطور الملكية
OWNER_ID = 8611300267 

# تهيئة البوت مع تفعيل تعدد المهام (Multi-threading)
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=25)

# الذاكرة المؤقتة (Buffer) للملفات التي لم تُحفظ بعد
# تضمن هذه الذاكرة عدم ضياع الملفات أثناء الجلسة
FILE_SESSION_BUFFER = {}

# --- [ 2. نظام السجلات المتقدم ] ---

def setup_uchiha_logger():
    """تجهيز نظام تسجيل العمليات لمراقبة البوت في ترمكس بدقة"""
    log_format = '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("uchiha_master_log.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("UchihaSystem")

uchiha_logger = setup_uchiha_logger()

# --- [ 3. محرك إدارة قواعد البيانات ] ---

def read_database_json(file_name):
    """دالة قراءة البيانات مع فحص الأخطاء الهيكلية"""
    try:
        if not os.path.exists(file_name):
            if "json" in file_name:
                if file_name == "admins.json": return {}
                return []
        with open(file_name, "r", encoding="utf-8") as file_handler:
            return json.load(file_handler)
    except Exception as error:
        uchiha_logger.error(f"Error reading {file_name}: {error}")
        return [] if "json" in file_name else {}

def write_database_json(file_name, data_payload):
    """دالة حفظ البيانات مع تنسيق طويل ومنظم"""
    try:
        with open(file_name, "w", encoding="utf-8") as file_handler:
            json.dump(data_payload, file_handler, indent=4, ensure_ascii=False)
        return True
    except Exception as error:
        uchiha_logger.error(f"Error writing {file_name}: {error}")
        return False

def initialize_all_core_files():
    """تأكيد وجود كافة ملفات النظام الضرورية وتجهيزها"""
    system_schema = {
        "users.txt": "",
        "bot_files.json": "[]",
        "admins.json": "{}",
        "subs.json": "[]",
        "settings.json": json.dumps({"channel_id": "@Uchiha75", "maintenance": False}),
        "stats.json": json.dumps({"total_likes": 0, "total_dls": 0, "history": []})
    }
    
    for filename, initial_content in system_schema.items():
        if not os.path.exists(filename):
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(initial_content)
                uchiha_logger.info(f"System File Initialized: {filename}")
            except Exception as e:
                uchiha_logger.critical(f"Critical Boot Error: {e}")

# تشغيل التهيئة عند الإقلاع
initialize_all_core_files()

# --- [ 4. نظام فحص الصلاحيات والاشتراك ] ---

def is_main_developer(user_id):
    """التحقق من هوية SELVA ZOLDEK"""
    return int(user_id) == OWNER_ID

def check_admin_permission(user_id, permission_type):
    """فحص صلاحيات الأدمن الفرعية"""
    if is_main_developer(user_id):
        return True
    
    admins_database = read_database_json("admins.json")
    user_key = str(user_id)
    
    if user_key in admins_database:
        return admins_database[user_key].get(permission_type, False)
    return False

def check_forced_subscription_status(user_id):
    """محرك فحص قنوات الاشتراك الـ 15"""
    if is_main_developer(user_id):
        return True
        
    subscription_list = read_database_json("subs.json")
    if not subscription_list:
        return True
        
    for channel in subscription_list:
        try:
            chat_member = bot.get_chat_member(channel['chat_id'], user_id)
            if chat_member.status in ['left', 'kicked', 'restricted']:
                return False
        except:
            continue
    return True

# --- [ 5. مصنع الواجهات والأزرار ] ---

def build_main_keyboard_layout(user_id):
    """بناء الكيبورد الرئيسي بدون زر تواصل معنا"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    if is_main_developer(user_id):
        markup.row(types.KeyboardButton("إدارة الاشتراك 🔗"), types.KeyboardButton("صلاحيات أدمن ⚙️"))
        markup.row(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"), types.KeyboardButton("إحصائيات النظام 📊"))
    
    elif str(user_id) in read_database_json("admins.json"):
        markup.row(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"))
    
    markup.row(types.KeyboardButton("استلام الملفات 📥"))
    return markup

def build_admin_panel_layout(user_id):
    """بناء لوحة الأدمن بناءً على الصلاحيات المعطاة"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    available_buttons = []
    
    if check_admin_permission(user_id, "upload"):
        available_buttons.append(types.KeyboardButton("إضافة ملفات 📤"))
    
    if check_admin_permission(user_id, "post"):
        available_buttons.append(types.KeyboardButton("نشر في القناة 📣"))
        
    if check_admin_permission(user_id, "stats"):
        available_buttons.append(types.KeyboardButton("الإحصائيات 📊"))
        
    if check_admin_permission(user_id, "reset"):
        available_buttons.append(types.KeyboardButton("تصفير ملفات 🗑️"))
        
    if check_admin_permission(user_id, "clean"):
        available_buttons.append(types.KeyboardButton("تنظيف بيانات 🧹"))
    
    markup.add(*available_buttons)
    markup.row(types.KeyboardButton("🔙 العودة للقائمة الرئيسية"))
    return markup

def build_batch_save_keyboard():
    """كيبورد التحكم في جلسة الرفع اليدوي"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("✅ إنهاء وحفظ الكل"),
        types.KeyboardButton("❌ إلغاء الحفظ")
    )
    return markup

# --- [ 6. معالج الرسائل الرئيسي (الراوتر) ] ---

@bot.message_handler(commands=['start'])
def handle_start_sequence(message):
    uid = message.from_user.id
    name = message.from_user.first_name
    
    if is_main_developer(uid):
        bot.send_message(
            uid, 
            "مرحبا ايها مطو😈 SELVA ZOLDEK 😈\nتم إصلاح كافة الأزرار المعطلة وتوسيع الكود ليكون الوحش الكامل.", 
            reply_markup=build_main_keyboard_layout(uid)
        )
    else:
        if not check_forced_subscription_status(uid):
            subs = read_database_json("subs.json")
            markup = types.InlineKeyboardMarkup()
            for s in subs:
                markup.add(types.InlineKeyboardButton(s['title'], url=s['url']))
            bot.send_message(uid, "⚠️ **يجب الاشتراك في القنوات التالية للمتابعة:**", reply_markup=markup, parse_mode="Markdown")
            return
            
        bot.send_message(uid, f"أهلاً بك {name} في Uchiha Dz ⚡", reply_markup=build_main_keyboard_layout(uid))

    # تسجيل المستخدم في القواعد النصية
    try:
        with open("users.txt", "a+", encoding="utf-8") as f:
            f.seek(0)
            if str(uid) not in f.read():
                f.write(f"{uid}\n")
    except Exception as e:
        uchiha_logger.error(f"User logging error: {e}")

@bot.message_handler(func=lambda m: True)
def central_logic_router(message):
    uid = message.from_user.id
    text = message.text

    # --- [ لوحة التحكم ] ---
    if text == "لوحة تحكم الأدمن 🛠️":
        if is_main_developer(uid) or str(uid) in read_database_json("admins.json"):
            bot.send_message(uid, "🛠️ قائمة الأدوات الإدارية الفعالة:", reply_markup=build_admin_panel_layout(uid))
        else:
            bot.send_message(uid, "❌ ليس لديك صلاحية الوصول لهذا القسم.")

    elif text == "🔙 العودة للقائمة الرئيسية":
        bot.send_message(uid, "تم العودة.", reply_markup=build_main_keyboard_layout(uid))

    # --- [ ميزة الإضافة المنفصلة والحفظ اليدوي ] ---
    elif text == "إضافة ملفات 📤" and check_admin_permission(uid, "upload"):
        FILE_SESSION_BUFFER[uid] = []
        bot.send_message(
            uid, 
            "📤 أرسل ملفاتك الآن بشكل منفصل.\nلاحظ: لن يتم الحفظ الفعلي إلا عند الضغط على 'إنهاء وحفظ الكل'.", 
            reply_markup=build_batch_save_keyboard()
        )
        bot.register_next_step_handler(message, collect_batch_files_handler)

    elif text == "✅ إنهاء وحفظ الكل":
        execute_permanent_save(uid)

    elif text == "❌ إلغاء الحفظ":
        if uid in FILE_SESSION_BUFFER:
            FILE_SESSION_BUFFER.pop(uid)
        bot.send_message(uid, "🗑️ تم إلغاء جلسة الرفع ومسح الذاكرة المؤقتة.", reply_markup=build_main_keyboard_layout(uid))

    # --- [ تفعيل الأزرار التي كانت معطلة ] ---
    elif text == "تصفير ملفات 🗑️" and check_admin_permission(uid, "reset"):
        write_database_json("bot_files.json", [])
        bot.send_message(uid, "✅ تم تصفير كافة الملفات من قاعدة البيانات بنجاح.")

    elif text == "تنظيف بيانات 🧹" and check_admin_permission(uid, "clean"):
        if os.path.exists("uchiha_master_log.log"):
            with open("uchiha_master_log.log", "w") as f: f.write("")
        bot.send_message(uid, "🧹 تم تنظيف سجلات النظام وتفريغ الكاش.")

    # --- [ ميزة النشر المزخرفة المطلوبة ] ---
    elif text == "نشر في القناة 📣" and check_admin_permission(uid, "post"):
        execute_ornamental_channel_post(uid)

    # --- [ إدارة الاشتراك 🔗 ] ---
    elif text == "إدارة الاشتراك 🔗" and is_main_developer(uid):
        render_subscription_management_panel(uid)

    # --- [ صلاحيات الأدمن ] ---
    elif text == "صلاحيات أدمن ⚙️" and is_main_developer(uid):
        msg = bot.send_message(uid, "👤 أرسل آيدي الشخص المراد تفعيله كأدمن:")
        bot.register_next_step_handler(msg, process_admin_privileges_assignment)

    elif text == "إحصائيات النظام 📊":
        if is_main_developer(uid) or check_admin_permission(uid, "stats"):
            display_system_statistics_report(uid)

# --- [ 7. منطق معالجة الملفات والجلسة ] ---

def collect_batch_files_handler(message):
    uid = message.from_user.id
    
    # التحقق إذا كان المستخدم قد ضغط على أزرار التحكم
    if message.text in ["✅ إنهاء وحفظ الكل", "❌ إلغاء الحفظ"]:
        central_logic_router(message)
        return

    if message.content_type == 'document':
        if uid not in FILE_SESSION_BUFFER:
            FILE_SESSION_BUFFER[uid] = []
        
        # تخزين في الرام فقط
        FILE_SESSION_BUFFER[uid].append({
            "file_id": message.document.file_id,
            "caption": message.caption if message.caption else "Uchiha File",
            "time": str(datetime.datetime.now())
        })
        
        count = len(FILE_SESSION_BUFFER[uid])
        bot.send_message(
            uid, 
            f"📥 تم استلام الملف رقم ({count}).\nيمكنك إرسال المزيد أو الضغط على إنهاء وحفظ.", 
            reply_markup=build_batch_save_keyboard()
        )
        bot.register_next_step_handler(message, collect_batch_files_handler)
    else:
        bot.send_message(uid, "⚠️ خطأ! يرجى إرسال ملف (Document) فقط.")
        bot.register_next_step_handler(message, collect_batch_files_handler)

def execute_permanent_save(uid):
    """نقل الملفات من الرام إلى ملف JSON الدائم"""
    if uid in FILE_SESSION_BUFFER and FILE_SESSION_BUFFER[uid]:
        permanent_files = read_database_json("bot_files.json")
        batch_to_add = FILE_SESSION_BUFFER[uid]
        
        permanent_files.extend(batch_to_add)
        if write_database_json("bot_files.json", permanent_files):
            total = len(batch_to_add)
            FILE_SESSION_BUFFER.pop(uid)
            bot.send_message(uid, f"✅ بنجاح! تم حفظ {total} ملفات في النظام.", reply_markup=build_main_keyboard_layout(uid))
    else:
        bot.send_message(uid, "❌ الجلسة فارغة، لا توجد ملفات لحفظها.")

# --- [ 8. نظام النشر المزخرف ] ---

def execute_ornamental_channel_post(uid):
    config = read_database_json("settings.json")
    post_id = str(int(time.time()))
    
    # الرسالة المزخرفة كما طلبتها يا مطور
    ornamental_text = (
        "┏━━━━━━━━━━━━━━━━━━━━━┓\n"
        "      ⚡ **UCHIHA DZ UPDATE** ⚡\n"
        "┗━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "🔥 **تفاعل**\n"
        "📥 **استلام**\n"
        "      🚀 **سرعة**\n"
        "      💪 **قوة**\n"
        "      ⏳ **مدة طويلة**\n\n"
        "⚠️ **سارع قبل انتهاء مدة!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("❤️ تفاعل", callback_data=f"LIKE_{post_id}"),
        types.InlineKeyboardButton("📥 استلام", callback_data=f"GET_{post_id}")
    )
    
    try:
        bot.send_message(config["channel_id"], ornamental_text, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بالزخرفة الجديدة والمطلوبة.")
    except Exception as e:
        bot.send_message(uid, f"❌ فشل النشر: تأكد من أن البوت أدمن في القناة {config['channel_id']}")

# --- [ 9. معالج الأوامر التفاعلية (Callbacks) ] ---

@bot.callback_query_handler(func=lambda call: True)
def global_callback_manager(call):
    uid, data = call.from_user.id, call.data
    
    if data.startswith("LIKE_"):
        bot.answer_callback_query(call.id, "شكراً لتفاعلك يا وحش! ❤️")
        
    elif data.startswith("GET_"):
        bot.answer_callback_query(call.id, "🚀 جاري تحضير الملفات بأقصى سرعة وقوة...")
        deliver_files_to_user_safe(uid)

    elif data.startswith("KILL_SUB_"):
        if not is_main_developer(uid): return
        idx = int(data.split("_")[2])
        subs = read_database_json("subs.json")
        subs.pop(idx)
        write_database_json("subs.json", subs)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=generate_subs_inline_markup())

    elif data == "TRIGGER_NEW_SUB":
        msg = bot.send_message(uid, "ارسل يوزر القناة ثم مسافة ثم اسم القناة (مثال: @Uchiha75 القوة):")
        bot.register_next_step_handler(msg, process_final_sub_addition)

def deliver_files_to_user_safe(uid):
    """إرسال كافة الملفات المخزنة للمستخدم"""
    all_files = read_database_json("bot_files.json")
    if not all_files:
        bot.send_message(uid, "❌ المعذرة، لا توجد ملفات متوفرة في النظام حالياً.")
        return
        
    for file_data in all_files:
        try:
            bot.send_document(uid, file_data['file_id'], caption=file_data['caption'])
            time.sleep(0.3) # تجنب الحظر من تليجرام
        except:
            continue

# --- [ 10. إدارة الاشتراك والصلاحيات ] ---

def render_subscription_management_panel(uid):
    bot.send_message(uid, "🔗 إدارة قنوات الاشتراك (15 قناة كحد أقصى):", reply_markup=generate_subs_inline_markup())

def generate_subs_inline_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    subs_list = read_database_json("subs.json")
    for i, s in enumerate(subs_list):
        markup.add(types.InlineKeyboardButton(f"🗑️ حذف: {s['title']}", callback_data=f"KILL_SUB_{i}"))
    
    if len(subs_list) < 15:
        markup.add(types.InlineKeyboardButton("➕ إضافة قناة جديدة", callback_data="TRIGGER_NEW_SUB"))
    return markup

def process_final_sub_addition(message):
    try:
        parts = message.text.split(" ", 1)
        user_tag = parts[0]
        title_tag = parts[1]
        subs = read_database_json("subs.json")
        subs.append({
            "chat_id": user_tag,
            "title": title_tag,
            "url": f"https://t.me/{user_tag[1:]}"
        })
        write_database_json("subs.json", subs)
        bot.send_message(message.chat.id, "✅ تمت إضافة القناة للقائمة بنجاح.")
    except:
        bot.send_message(message.chat.id, "❌ خطأ في التنسيق! أرسل اليوزر ثم مسافة ثم الاسم.")

def process_admin_privileges_assignment(message):
    target_id = message.text
    if target_id.isdigit():
        admins_db = read_database_json("admins.json")
        # منح كافة الصلاحيات بشكل تلقائي
        admins_db[target_id] = {
            "upload": True, "post": True, "stats": True, 
            "reset": True, "clean": True, "broadcast": True
        }
        write_database_json("admins.json", admins_db)
        bot.send_message(message.chat.id, f"✅ تم تعيين {target_id} كأدمن بصلاحيات كاملة.")
    else:
        bot.send_message(message.chat.id, "❌ يرجى إرسال آيدي رقمي.")

def display_system_statistics_report(uid):
    users_count = len(open("users.txt").readlines()) if os.path.exists("users.txt") else 0
    files_count = len(read_database_json("bot_files.json"))
    
    report = (
        f"📊 **تقرير نظام Uchiha Dz الاحترافي:**\n\n"
        f"👥 إجمالي المستخدمين: `{users_count}`\n"
        f"📂 إجمالي الملفات المرفوعة: `{files_count}`\n"
        f"⚙️ بيئة التشغيل: `{platform.system()}`\n"
        f"🕒 وقت التقرير: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(uid, report, parse_mode="Markdown")

# --- [ 11. نظام مكافحة الانهيار (Anti-Crash) ] ---

if __name__ == "__main__":
    uchiha_logger.info("-------------------------------------------")
    uchiha_logger.info("UCHIHA DZ SYSTEM BOOT SEQUENCE INITIATED")
    uchiha_logger.info(f"OS: {platform.system()} | MASTER: SELVA ZOLDEK")
    uchiha_logger.info("-------------------------------------------")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as critical_crash:
            uchiha_logger.critical(f"System Crash: {critical_crash}")
            uchiha_logger.error(traceback.format_exc())
            time.sleep(10) # انتظار قبل إعادة المحاولة لضمان استقرار ترمكس

