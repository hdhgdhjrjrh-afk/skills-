# ============================================================
# ⚡ Uchiha Dz - The Absolute Master System ⚡
# 🛠️ Architect: SELVA ZOLDEK
# 🆔 Developer ID: 8611300267
# 🚫 NO CONTACT BUTTON | ✅ MANUAL SESSION SAVE
# 🔄 Version: 6.0.1 (Stable & Long Edition)
# ============================================================

import telebot
from telebot import types
import os
import json
import time
import logging
import datetime
import sys
import shutil

# --- [ 1. إعدادات الهوية والاتصال ] ---

# توكن البوت
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
# آيدي المطور SELVA ZOLDEK
OWNER_ID = 8611300267 

# تهيئة كائن البوت
bot = telebot.TeleBot(TOKEN, parse_mode=None)

# مخزن الجلسات المؤقت (RAM) للملفات المنفصلة
# لن يتم الحفظ إلا عند ضغط "إنهاء وحفظ"
FILE_SESSIONS = {}

# --- [ 2. نظام السجلات المتقدم - Logging System ] ---

def initialize_logger():
    """تهيئة نظام تسجيل العمليات لمراقبة كل تفصيل في ترمكس"""
    logger = logging.getLogger("UchihaDz")
    logger.setLevel(logging.INFO)
    
    # تنسيق السجل
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # حفظ في ملف
    file_handler = logging.FileHandler("system_logs.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # عرض في الكونسول
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

log = initialize_logger()

# --- [ 3. إدارة قواعد البيانات - Data Management ] ---

def setup_databases():
    """تأكيد وجود كافة ملفات البيانات مع هيكلة أولية طويلة"""
    log.info("Starting database setup sequence...")
    
    databases = {
        "users.txt": "",
        "bot_files.json": "[]",
        "admins.json": "{}",
        "subs.json": "[]",
        "stats.json": json.dumps({
            "total_system_likes": 0,
            "total_system_downloads": 0,
            "posts_stats": {}
        }),
        "settings.json": json.dumps({
            "channel_id": "@Uchiha75",
            "maintenance": False,
            "dev_tag": "SELVA ZOLDEK"
        })
    }
    
    for filename, initial_data in databases.items():
        if not os.path.exists(filename):
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(initial_data)
                log.info(f"Database [{filename}] initialized successfully.")
            except Exception as e:
                log.error(f"Critical failure initializing [{filename}]: {e}")

setup_databases()

# --- [ 4. دوال الوصول للبيانات (Read/Write) ] ---

def get_json_content(file_path):
    """قراءة البيانات من ملفات JSON مع فحص الأخطاء"""
    try:
        if not os.path.exists(file_path):
            return [] if "json" in file_path else {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        log.warning(f"File {file_path} is corrupted. Resetting...")
        return []
    except Exception as e:
        log.error(f"Error reading {file_path}: {e}")
        return {}

def save_json_content(file_path, data_to_save):
    """حفظ البيانات في JSON مع تنسيق Indent 4 لزيادة الوضوح"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        log.error(f"Error writing to {file_path}: {e}")
        return False

def get_registered_users_list():
    """جلب قائمة المستخدمين من ملف النص"""
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# --- [ 5. طبقة الأمان والتحقق من الهوية ] ---

def is_owner(user_id):
    """هل المستخدم هو SELVA ZOLDEK؟"""
    return int(user_id) == OWNER_ID

def check_admin_privilege(user_id, privilege_name):
    """التحقق من صلاحية محددة للأدمن"""
    if is_owner(user_id):
        return True
    
    admins_map = get_json_content("admins.json")
    user_str = str(user_id)
    
    if user_str in admins_map:
        return admins_map[user_str].get(privilege_name, False)
    return False

def verify_forced_subscriptions(user_id):
    """فحص الاشتراك في الـ 15 قناة قبل السماح باستخدام البوت"""
    if is_owner(user_id):
        return True
        
    subscription_channels = get_json_content("subs.json")
    if not subscription_channels:
        return True
        
    for channel in subscription_channels:
        try:
            member_status = bot.get_chat_member(channel['chat_id'], user_id).status
            if member_status in ['left', 'kicked', 'restricted']:
                return False
        except Exception as e:
            log.debug(f"Subscription check error for {channel['chat_id']}: {e}")
            continue
    return True

# --- [ 6. بناء الواجهات والأزرار (Keyboards) ] ---

def build_main_keyboard(user_id):
    """بناء الكيبورد الرئيسي - تم حذف زر تواصل معنا نهائياً"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # أزرار المطور الأساسي
    if is_owner(user_id):
        markup.row(types.KeyboardButton("إدارة الاشتراك 🔗"), types.KeyboardButton("صلاحيات أدمن ⚙️"))
        markup.row(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"), types.KeyboardButton("إحصائيات النظام 📊"))
    
    # أزرار الأدمن العادي
    elif str(user_id) in get_json_content("admins.json"):
        markup.row(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"))
    
    # الأزرار العامة للمستخدمين
    markup.row(types.KeyboardButton("استلام الملفات 📥"))
    
    return markup

def build_admin_tools_keyboard(user_id):
    """بناء لوحة الأدمن الديناميكية بناءً على الصلاحيات"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    available_btns = []
    
    if check_admin_privilege(user_id, "upload"):
        available_btns.append(types.KeyboardButton("إضافة ملفات 📤"))
    
    if check_admin_privilege(user_id, "post"):
        available_btns.append(types.KeyboardButton("نشر في القناة 📣"))
        
    if check_admin_privilege(user_id, "broadcast"):
        available_btns.append(types.KeyboardButton("قسم الإذاعة 📢"))
        
    if check_admin_privilege(user_id, "stats"):
        available_btns.append(types.KeyboardButton("الإحصائيات 📊"))
        
    if check_admin_privilege(user_id, "reset"):
        available_btns.append(types.KeyboardButton("تصفير ملفات 🗑️"))
        
    if check_admin_privilege(user_id, "clean"):
        available_btns.append(types.KeyboardButton("تنظيف بيانات 🧹"))
        
    markup.add(*available_btns)
    markup.row(types.KeyboardButton("🔙 العودة للقائمة الرئيسية"))
    return markup

def build_save_control_keyboard():
    """كيبورد التحكم أثناء الرفع المتعدد"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("✅ إنهاء وحفظ الكل"),
        types.KeyboardButton("❌ إلغاء الحفظ")
    )
    return markup

# --- [ 7. معالجة البداية (Start Handler) ] ---

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    uid = message.from_user.id
    name = message.from_user.first_name
    
    # ترحيب المطور المخصص
    if is_owner(uid):
        bot.send_message(
            uid, 
            "مرحبا ايها مطو😈 SELVA ZOLDEK 😈\nتم تحديث النظام وحذف الأزرار غير المرغوبة.", 
            reply_markup=build_main_keyboard(uid)
        )
    else:
        # فحص الاشتراك الإجباري
        if not verify_forced_subscriptions(uid):
            subs = get_json_content("subs.json")
            text = "⚠️ **يجب عليك الاشتراك في القنوات التالية لاستخدام البوت:**\n"
            markup = types.InlineKeyboardMarkup()
            for s in subs:
                markup.add(types.InlineKeyboardButton(s['title'], url=s['url']))
            bot.send_message(uid, text, reply_markup=markup, parse_mode="Markdown")
            return
            
        bot.send_message(uid, f"أهلاً بك {name} في Uchiha Dz ⚡", reply_markup=build_main_keyboard(uid))

    # تسجيل آيدي المستخدم
    users = get_registered_users_list()
    if str(uid) not in users:
        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(f"{uid}\n")
        log.info(f"New user registered: {uid}")

# --- [ 8. موزع المهام الرئيسي (System Router) ] ---

@bot.message_handler(func=lambda m: True)
def system_router(message):
    uid = message.from_user.id
    txt = message.text

    # --- [ صلاحيات المطور فقط ] ---
    if txt == "صلاحيات أدمن ⚙️" and is_owner(uid):
        msg = bot.send_message(uid, "👤 أرسل آيدي الشخص المراد تعديل صلاحياته:")
        bot.register_next_step_handler(msg, process_set_admin_step)

    elif txt == "إدارة الاشتراك 🔗" and is_owner(uid):
        render_subscription_panel(uid)

    # --- [ لوحات التحكم ] ---
    elif txt == "لوحة تحكم الأدمن 🛠️":
        if is_owner(uid) or str(uid) in get_json_content("admins.json"):
            bot.send_message(uid, "🛠️ الأدوات البرمجية المتاحة:", reply_markup=build_admin_tools_keyboard(uid))
        else:
            bot.send_message(uid, "❌ ليس لديك صلاحية الوصول لهذا القسم.")

    elif txt == "🔙 العودة للقائمة الرئيسية":
        bot.send_message(uid, "تم الرجوع.", reply_markup=build_main_keyboard(uid))

    # --- [ نظام إضافة الملفات (المحسن والمشروط) ] ---
    elif txt == "إضافة ملفات 📤" and check_admin_privilege(uid, "upload"):
        # فتح جلسة جديدة في الرام
        FILE_SESSIONS[uid] = [] 
        bot.send_message(
            uid, 
            "📤 أرسل ملفاتك الآن بشكل منفصل.\nلن يتم الحفظ الفعلي إلا عند ضغط 'إنهاء وحفظ الكل'.", 
            reply_markup=build_save_control_keyboard()
        )
        bot.register_next_step_handler(message, step_collect_files_session)

    elif txt == "✅ إنهاء وحفظ الكل":
        finalize_and_commit_save(uid)

    elif txt == "❌ إلغاء الحفظ":
        if uid in FILE_SESSIONS:
            FILE_SESSIONS.pop(uid)
        bot.send_message(uid, "🗑️ تم إلغاء العملية ومسح الذاكرة المؤقتة.", reply_markup=build_main_keyboard(uid))

    # --- [ المهام الإدارية الأخرى ] ---
    elif txt == "نشر في القناة 📣" and check_admin_privilege(uid, "post"):
        execute_controlled_post(uid)
        
    elif txt == "إحصائيات النظام 📊" or (txt == "الإحصائيات 📊" and check_admin_privilege(uid, "stats")):
        show_stats_detailed(uid)

# --- [ 9. منطق الرفع والحفظ اليدوي (Session Logic) ] ---

def step_collect_files_session(message):
    uid = message.from_user.id
    
    # فحص إذا ضغط المستخدم على الأزرار أثناء الرفع
    if message.text in ["✅ إنهاء وحفظ الكل", "❌ إلغاء الحفظ"]:
        system_router(message)
        return

    if message.content_type == 'document':
        if uid not in FILE_SESSIONS:
            FILE_SESSIONS[uid] = []
            
        # حفظ الملف في الجلسة المؤقتة فقط
        FILE_SESSIONS[uid].append({
            "file_id": message.document.file_id,
            "caption": message.caption if message.caption else "Uchiha File",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        current_batch_size = len(FILE_SESSIONS[uid])
        bot.send_message(
            uid, 
            f"📥 تم استلام الملف ({current_batch_size}).\nأرسل ملفاً آخر أو اضغط 'إنهاء وحفظ'.", 
            reply_markup=build_save_control_keyboard()
        )
        bot.register_next_step_handler(message, step_collect_files_session)
    else:
        bot.send_message(uid, "⚠️ خطأ: يرجى إرسال ملفات فقط (Documents).", reply_markup=build_save_control_keyboard())
        bot.register_next_step_handler(message, step_collect_files_session)

def finalize_and_commit_save(uid):
    """هنا يحدث الحفظ الحقيقي في قاعدة البيانات"""
    if uid in FILE_SESSIONS and FILE_SESSIONS[uid]:
        db_files = get_json_content("bot_files.json")
        new_batch = FILE_SESSIONS[uid]
        
        # دمج البيانات
        db_files.extend(new_batch)
        
        if save_json_content("bot_files.json", db_files):
            total_added = len(new_batch)
            FILE_SESSIONS.pop(uid) # إفراغ الرام
            bot.send_message(uid, f"✅ بنجاح! تم حفظ ({total_added}) ملفات في النظام.", reply_markup=build_main_keyboard(uid))
            log.info(f"Admin {uid} committed {total_added} files.")
    else:
        bot.send_message(uid, "❌ الجلسة فارغة! لا توجد ملفات لحفظها.", reply_markup=build_main_keyboard(uid))

# --- [ 10. نظام النشر والعدادات (Interaction System) ] ---

def execute_controlled_post(uid):
    settings = get_json_content("settings.json")
    post_id = str(int(time.time()))
    
    # تهيئة إحصائيات المنشور
    stats = get_json_content("stats.json")
    stats["posts_stats"][post_id] = {"likes": 0, "downloads": 0}
    save_json_content("stats.json", stats)
    
    markup = types.InlineKeyboardMarkup()
    btn_like = types.InlineKeyboardButton("❤️ (0)", callback_data=f"L_{post_id}")
    btn_dl = types.InlineKeyboardButton("📥 استلام (0)", callback_data=f"D_{post_id}")
    markup.row(btn_like, btn_dl)
    
    text = "⚡ **تحديث ملفات Uchiha Dz جديد!**\n━━━━━━━━━━━━━━\nتفاعل واستلم ملفاتك الحصرية الآن."
    
    try:
        bot.send_message(settings["channel_id"], text, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم إرسال المنشور إلى القناة بنجاح.")
    except Exception as e:
        bot.send_message(uid, f"❌ فشل النشر في القناة: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks_logic(call):
    uid = call.from_user.id
    data = call.data
    stats_db = get_json_content("stats.json")

    # معالجة عداد اللايك
    if data.startswith("L_"):
        pid = data.split("_")[1]
        if pid in stats_db["posts_stats"]:
            stats_db["posts_stats"][pid]["likes"] += 1
            stats_db["total_system_likes"] += 1
            save_json_content("stats.json", stats_db)
            
            # تحديث الواجهة
            mk = call.message.reply_markup
            mk.keyboard[0][0].text = f"❤️ ({stats_db['posts_stats'][pid]['likes']})"
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mk)
            bot.answer_callback_query(call.id, "تم تسجيل إعجابك ❤️")

    # معالجة عداد الاستلام
    elif data.startswith("D_"):
        pid = data.split("_")[1]
        if pid in stats_db["posts_stats"]:
            stats_db["posts_stats"][pid]["downloads"] += 1
            stats_db["total_system_downloads"] += 1
            save_json_content("stats.json", stats_db)
            
            # تحديث الواجهة
            mk = call.message.reply_markup
            mk.keyboard[0][1].text = f"📥 استلام ({stats_db['posts_stats'][pid]['downloads']})"
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mk)
            
            bot.answer_callback_query(call.id, "جاري إرسال الملفات المتاحة...")
            send_files_to_user(uid)

    # إدارة قنوات الاشتراك (حذف)
    elif data.startswith("kill_sub_"):
        if not is_owner(uid): return
        idx = int(data.split("_")[2])
        subs_list = get_json_content("subs.json")
        subs_list.pop(idx)
        save_json_content("subs.json", subs_list)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=render_subs_inline_kb())

    # إغلاق النوافذ
    elif data == "close_win":
        bot.delete_message(call.message.chat.id, call.message.message_id)

# --- [ 11. وظائف الإدارة الإضافية (Helper Functions) ] ---

def render_subscription_panel(uid):
    bot.send_message(uid, "🔗 إدارة قنوات الاشتراك الـ 15:", reply_markup=render_subs_inline_kb())

def render_subs_inline_kb():
    markup = types.InlineKeyboardMarkup(row_width=1)
    subs = get_json_content("subs.json")
    for i, s in enumerate(subs):
        markup.add(types.InlineKeyboardButton(f"🗑️ حذف: {s['title']}", callback_data=f"kill_sub_{i}"))
    
    if len(subs) < 15:
        markup.add(types.InlineKeyboardButton("➕ إضافة قناة جديدة", callback_data="trigger_add_sub"))
    
    markup.add(types.InlineKeyboardButton("🔙 إغلاق", callback_data="close_win"))
    return markup

def process_set_admin_step(message):
    if message.text.isdigit():
        target_id = message.text
        admins_db = get_json_content("admins.json")
        if target_id not in admins_db:
            admins_db[target_id] = {
                "upload": False, "post": False, "broadcast": False,
                "stats": False, "reset": False, "clean": False
            }
        save_json_content("admins.json", admins_db)
        display_admin_privileges_panel(message.chat.id, target_id)
    else:
        bot.send_message(message.chat.id, "❌ الآيدي يجب أن يتكون من أرقام فقط.")

def display_admin_privileges_panel(chat_id, target_id):
    admins = get_json_content("admins.json")
    p = admins[target_id]
    mk = types.InlineKeyboardMarkup(row_width=2)
    
    options = {
        "upload": "رفع 📤", "post": "نشر 📣", "broadcast": "إذاعة 📢",
        "stats": "📊", "reset": "تصفير 🗑️", "clean": "تنظيف 🧹"
    }
    
    btns = []
    for key, label in options.items():
        status = "✅" if p.get(key) else "❌"
        btns.append(types.InlineKeyboardButton(f"{label} {status}", callback_data=f"toggle_p_{target_id}_{key}"))
    
    mk.add(*btns)
    mk.add(types.InlineKeyboardButton("🔙 إنهاء", callback_data="close_win"))
    bot.send_message(chat_id, f"⚙️ إدارة صلاحيات الأدمن `{target_id}`:", reply_markup=mk, parse_mode="Markdown")

def send_files_to_user(uid):
    """إرسال كافة الملفات المخزنة للمستخدم"""
    files = get_json_content("bot_files.json")
    if not files:
        bot.send_message(uid, "❌ لا توجد ملفات متوفرة حالياً.")
        return
        
    for f in files:
        try:
            bot.send_document(uid, f['file_id'], caption=f['caption'])
            time.sleep(0.3)
        except:
            continue

def show_stats_detailed(uid):
    users = get_registered_users_list()
    files = get_json_content("bot_files.json")
    stats = get_json_content("stats.json")
    
    report = (
        f"📊 **تقرير نظام Uchiha Dz الاحترافي:**\n\n"
        f"👥 إجمالي المستخدمين: `{len(users)}` مستخدم\n"
        f"📂 إجمالي الملفات: `{len(files)}` ملف\n"
        f"❤️ إجمالي التفاعلات: `{stats.get('total_system_likes', 0)}` إعجاب\n"
        f"📥 إجمالي طلبات الاستلام: `{stats.get('total_system_downloads', 0)}` مرة\n"
        f"━━━━━━━━━━━━━━\n"
        f"🕒 التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    bot.send_message(uid, report, parse_mode="Markdown")

# --- [ 12. نقطة الانطلاق والتشغيل (Main Loop) ] ---

if __name__ == "__main__":
    log.info("------------------------------------------")
    log.info("⚡ UCHIHA DZ SYSTEM VERSION 6.0.1 IS ACTIVE")
    log.info(f"🛠️ MAIN DEVELOPER: SELVA ZOLDEK")
    log.info("------------------------------------------")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as critical_error:
            log.critical(f"System Crash: {critical_error}")
            time.sleep(15) # انتظار لإعادة المحاولة

