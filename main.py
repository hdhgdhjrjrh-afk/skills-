# ============================================================
# ⚡ Uchiha Dz - The Ultimate Administration & Files System ⚡
# 🛠️ Main Architect: SELVA ZOLDEK
# 🆔 Developer Identity: 8611300267
# 🔄 Version: 4.0.0 (Extended Stability Edition)
# ============================================================

import telebot
from telebot import types
import os
import json
import time
import logging
import datetime
import sys
import threading

# --- [ 1. إعدادات الهوية والاتصال ] ---

# توكن البوت الأساسي
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
# آيدي المطور الأساسي SELVA ZOLDEK
OWNER_ID = 8611300267 

# تهيئة كائن البوت مع تفعيل ميزة تعدد الخيوط (Threading)
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=4)

# --- [ 2. نظام السجلات والرقابة - Logging System ] ---

def setup_logger():
    """تهيئة نظام تسجيل العمليات لمراقبة كل حركة في الترمكس"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("system_core.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("UchihaSystem")

logger = setup_logger()

# --- [ 3. إدارة مخازن البيانات المؤقتة والدائمة ] ---

# مخزن مؤقت للملفات (Session Data) لمنع الحفظ العشوائي
# يتم تخزين الملفات هنا حتى يضغط الأدمن على "إنهاء وحفظ"
SESSION_UPLOADS = {} 

def ensure_database_files():
    """
    سلسلة فحص سلامة الملفات: تضمن وجود كل قاعدة بيانات 
    بشكل مستقل وتمنع انهيار البوت عند فقدان أي ملف.
    """
    logger.info("Checking database integrity...")
    
    # قائمة بجميع الملفات المطلوبة وهيكليتها الافتراضية
    db_map = {
        "users.txt": "",
        "bot_files.json": "[]",
        "admins.json": "{}",
        "subs.json": "[]",
        "settings.json": json.dumps({
            "notifications": True, 
            "channel_id": "@Uchiha75",
            "maintenance_mode": False
        }),
        "stats.json": json.dumps({
            "total_system_likes": 0,
            "total_system_downloads": 0,
            "posts_stats": {}
        })
    }
    
    for file_name, default_content in db_map.items():
        if not os.path.exists(file_name):
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(default_content)
                logger.info(f"Initialized missing database: {file_name}")
            except Exception as e:
                logger.critical(f"Failed to create {file_name}: {e}")

# تشغيل الفحص الأولي
ensure_database_files()

# --- [ 4. دوال معالجة البيانات (IO Operations) ] ---

def read_json(path):
    """قراءة بيانات JSON بدقة مع معالجة الأخطاء"""
    try:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Read Error [{path}]: {e}")
        return {}

def write_json(path, data):
    """حفظ البيانات بشكل منسق وطويل لسهولة المراجعة"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Write Error [{path}]: {e}")
        return False

def get_all_users():
    """جلب قائمة المستخدمين كـ List"""
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# --- [ 5. طبقة التحقق من الصلاحيات (Security Layer) ] ---

def is_main_dev(uid):
    """هل المستخدم هو SELVA ZOLDEK؟"""
    return int(uid) == OWNER_ID

def check_admin_permission(uid, permission_type):
    """
    التحقق من صلاحية الأدمن لنوع معين من العمليات.
    الصلاحيات المتاحة: upload, post, broadcast, stats, reset, clean
    """
    if is_main_dev(uid):
        return True
        
    admins_db = read_json("admins.json")
    uid_str = str(uid)
    
    if uid_str in admins_db:
        # فحص الصلاحية المحددة
        return admins_db[uid_str].get(permission_type, False)
    
    return False

def check_forced_subscription(uid):
    """
    فحص الاشتراك الإجباري في القنوات (حتى 15 قناة).
    البوت لن يعمل إلا إذا كان المستخدم مشتركاً في الجميع.
    """
    if is_main_dev(uid):
        return True
        
    subs_list = read_json("subs.json")
    if not subs_list:
        return True
        
    for channel in subs_list:
        try:
            member = bot.get_chat_member(channel['chat_id'], uid)
            if member.status in ['left', 'kicked', 'restricted']:
                return False
        except Exception:
            # تخطي القناة إذا كان هناك خطأ في الوصول
            continue
    return True

# --- [ 6. بناء واجهات المستخدم (Keyboards) ] ---

def get_main_keyboard(uid):
    """بناء لوحة التحكم الرئيسية الكاملة"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # خيارات المطور الأساسي
    if is_main_dev(uid):
        markup.row(types.KeyboardButton("إدارة الاشتراك 🔗"), types.KeyboardButton("صلاحيات أدمن ⚙️"))
        markup.row(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"), types.KeyboardButton("إحصائيات النظام 📊"))
    
    # خيارات الأدمنية (لوحة التحكم فقط)
    elif str(uid) in read_json("admins.json"):
        markup.row(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"))
    
    # الأزرار العامة
    markup.row(types.KeyboardButton("استلام الملفات 📥"), types.KeyboardButton("تواصل معنا 📞"))
    return markup

def get_admin_tools_keyboard(uid):
    """لوحة الأدمن بناءً على الصلاحيات الممنوحة له"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    if check_admin_permission(uid, "upload"):
        markup.add(types.KeyboardButton("إضافة ملفات 📤"))
    
    if check_admin_permission(uid, "post"):
        markup.add(types.KeyboardButton("نشر في القناة 📣"))
        
    if check_admin_permission(uid, "broadcast"):
        markup.add(types.KeyboardButton("قسم الإذاعة 📢"))
        
    if check_admin_permission(uid, "stats"):
        markup.add(types.KeyboardButton("الإحصائيات 📊"))
        
    if check_admin_permission(uid, "reset"):
        markup.add(types.KeyboardButton("تصفير ملفات 🗑️"))
        
    if check_admin_permission(uid, "clean"):
        markup.add(types.KeyboardButton("تنظيف بيانات 🧹"))
        
    markup.row(types.KeyboardButton("🔙 العودة للقائمة الرئيسية"))
    return markup

def get_finish_upload_kb():
    """لوحة التحكم أثناء عملية الرفع المتعدد"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("✅ إنهاء وحفظ الملفات"))
    markup.add(types.KeyboardButton("❌ إلغاء العملية"))
    return markup

def get_subs_inline_kb():
    """لوحة إدارة الـ 15 قناة (Inline)"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    subs = read_json("subs.json")
    
    for i, s in enumerate(subs):
        markup.add(types.InlineKeyboardButton(f"❌ حذف: {s['title']}", callback_data=f"del_sub_{i}"))
        
    if len(subs) < 15:
        markup.add(types.InlineKeyboardButton("➕ إضافة قناة جديدة", callback_data="add_sub_trigger"))
        
    markup.add(types.InlineKeyboardButton("🔙 إغلاق", callback_data="close_p"))
    return markup

# --- [ 7. معالجة الأوامر الأساسية ] ---

@bot.message_handler(commands=['start'])
def welcome_manager(message):
    uid = message.from_user.id
    name = message.from_user.first_name
    
    # ترحيب المطور المخصص
    if is_main_dev(uid):
        bot.send_message(uid, "مرحبا ايها مطو😈 SELVA ZOLDEK 😈", reply_markup=get_main_keyboard(uid))
    else:
        # فحص الاشتراك للمستخدمين
        if not check_forced_subscription(uid):
            subs = read_json("subs.json")
            txt = "⚠️ **يجب الاشتراك في قنواتنا أولاً للاستفادة من البوت:**\n"
            mk = types.InlineKeyboardMarkup()
            for s in subs:
                mk.add(types.InlineKeyboardButton(s['title'], url=s['url']))
            bot.send_message(uid, txt, reply_markup=mk, parse_mode="Markdown")
            return
            
        bot.send_message(uid, f"أهلاً بك {name} في نظام Uchiha Dz ⚡", reply_markup=get_main_keyboard(uid))

    # تسجيل المستخدم الجديد
    all_users = get_all_users()
    if str(uid) not in all_users:
        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(f"{uid}\n")
        logger.info(f"User {uid} registered successfully.")

# --- [ 8. نظام موزع العمليات (Main Router) ] ---

@bot.message_handler(func=lambda message: True)
def main_router(message):
    uid = message.from_user.id
    txt = message.text

    # --- [ صلاحيات المطور فقط ] ---
    if txt == "إدارة الاشتراك 🔗" and is_main_dev(uid):
        bot.send_message(uid, "🔗 إدارة قائمة الـ 15 قناة:", reply_markup=get_subs_inline_kb())

    elif txt == "صلاحيات أدمن ⚙️" and is_main_dev(uid):
        msg = bot.send_message(uid, "👤 أرسل آيدي (ID) الشخص المراد تعديل صلاحياته:")
        bot.register_next_step_handler(msg, step_set_admin_perms)

    # --- [ لوحات التحكم المشتركة ] ---
    elif txt == "لوحة تحكم الأدمن 🛠️":
        if is_main_dev(uid) or str(uid) in read_json("admins.json"):
            bot.send_message(uid, "🛠️ خيارات الإدارة المتاحة لك:", reply_markup=get_admin_tools_keyboard(uid))
        else:
            bot.send_message(uid, "❌ هذا القسم مخصص للمسؤولين فقط.")

    elif txt == "🔙 العودة للقائمة الرئيسية":
        bot.send_message(uid, "تم الرجوع.", reply_markup=get_main_keyboard(uid))

    # --- [ تنفيذ مهام الأدمن الممنوحة ] ---
    
    # 1. نظام الرفع المتعدد (مهم جداً)
    elif txt == "إضافة ملفات 📤" and check_admin_permission(uid, "upload"):
        SESSION_UPLOADS[uid] = [] # فتح جلسة جديدة في الرام
        bot.send_message(uid, "📤 أرسل ملفاتك الآن بشكل منفصل.\nبمجرد الانتهاء اضغط 'إنهاء وحفظ'.", reply_markup=get_finish_upload_kb())
        bot.register_next_step_handler(message, step_batch_upload)

    elif txt == "✅ إنهاء وحفظ الملفات":
        finalize_and_save_session(uid)

    elif txt == "❌ إلغاء العملية":
        if uid in SESSION_UPLOADS: SESSION_UPLOADS.pop(uid)
        bot.send_message(uid, "🗑️ تم إلغاء الجلسة وحذف التغييرات.", reply_markup=get_main_keyboard(uid))

    # 2. نظام النشر المطور
    elif txt == "نشر في القناة 📣" and check_admin_permission(uid, "post"):
        execute_controlled_post(uid)

    # 3. الإحصائيات
    elif txt == "الإحصائيات 📊" and check_admin_permission(uid, "stats"):
        generate_stats_report(uid)

# --- [ 9. دوال نظام الرفع المتعدد (Batch Upload) ] ---

def step_batch_upload(message):
    uid = message.from_user.id
    
    # الخروج من الجلسة في حال ضغط الأزرار
    if message.text in ["✅ إنهاء وحفظ الملفات", "❌ إلغاء العملية"]:
        main_router(message)
        return

    if message.content_type == 'document':
        if uid not in SESSION_UPLOADS:
            SESSION_UPLOADS[uid] = []
            
        # تخزين الملف مؤقتاً
        file_info = {
            "file_id": message.document.file_id,
            "caption": message.caption if message.caption else "Uchiha File",
            "added_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        SESSION_UPLOADS[uid].append(file_info)
        
        current_count = len(SESSION_UPLOADS[uid])
        bot.send_message(uid, f"📥 تم استلام الملف رقم ({current_count}).\nيمكنك إرسال المزيد أو الحفظ.", reply_markup=get_finish_upload_kb())
        bot.register_next_step_handler(message, step_batch_upload)
    else:
        bot.send_message(uid, "⚠️ خطأ! يجب إرسال ملف (Document) فقط.", reply_markup=get_finish_upload_kb())
        bot.register_next_step_handler(message, step_batch_upload)

def finalize_and_save_session(uid):
    """حفظ كافة الملفات المجمعة في قاعدة البيانات الدائمة"""
    if uid in SESSION_UPLOADS and SESSION_UPLOADS[uid]:
        all_files = read_json("bot_files.json")
        new_batch = SESSION_UPLOADS[uid]
        
        # دمج القائمة الجديدة مع القديمة
        all_files.extend(new_batch)
        
        if write_json("bot_files.json", all_files):
            count = len(new_batch)
            SESSION_UPLOADS.pop(uid)
            bot.send_message(uid, f"✅ تم حفظ ({count}) ملفات بنجاح في قاعدة البيانات!", reply_markup=get_main_keyboard(uid))
            logger.info(f"Admin {uid} saved a batch of {count} files.")
    else:
        bot.send_message(uid, "❌ لا توجد ملفات في الجلسة لحفظها!", reply_markup=get_main_keyboard(uid))

# --- [ 10. نظام النشر والعدادات المستقلة ] ---

def execute_controlled_post(uid):
    """إنشاء منشور قناة مع نظام تعقب مستقل"""
    conf = read_json("settings.json")
    post_timestamp = str(int(time.time()))
    
    # تهيئة إحصائيات المنشور الجديد في stats.json
    stats = read_json("stats.json")
    stats["posts_stats"][post_timestamp] = {"likes": 0, "downloads": 0}
    write_json("stats.json", stats)
    
    # بناء أزرار التفاعل
    markup = types.InlineKeyboardMarkup()
    btn_l = types.InlineKeyboardButton("❤️ (0)", callback_data=f"LIKE_{post_timestamp}")
    btn_d = types.InlineKeyboardButton("📥 استلام (0)", callback_data=f"GET_{post_timestamp}")
    markup.row(btn_l, btn_d)
    
    msg_text = "⚡ **تحديث ملفات جديد متاح الآن!**\n\nتفاعل بـ (❤️) واستلم الملفات فوراً.\n━━━━━━━━━━━━━━"
    
    try:
        bot.send_message(conf["channel_id"], msg_text, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم إرسال المنشور إلى القناة بنجاح.")
    except Exception as e:
        bot.send_message(uid, f"❌ فشل النشر في القناة: {e}")

# --- [ 11. نظام إدارة الصلاحيات والـ Callbacks ] ---

@bot.callback_query_handler(func=lambda call: True)
def process_callbacks(call):
    uid = call.from_user.id
    data = call.data
    stats_db = read_json("stats.json")

    # 1. عداد التفاعل ❤️
    if data.startswith("LIKE_"):
        pid = data.split("_")[1]
        if pid in stats_db["posts_stats"]:
            stats_db["posts_stats"][pid]["likes"] += 1
            stats_db["total_system_likes"] += 1
            write_json("stats.json", stats_db)
            
            # تحديث الزر
            current_likes = stats_db["posts_stats"][pid]["likes"]
            mk = call.message.reply_markup
            mk.keyboard[0][0].text = f"❤️ ({current_likes})"
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mk)
            bot.answer_callback_query(call.id, "شكراً لتفاعلك! ❤️")

    # 2. عداد الاستلام 📥
    elif data.startswith("GET_"):
        pid = data.split("_")[1]
        if pid in stats_db["posts_stats"]:
            stats_db["posts_stats"][pid]["downloads"] += 1
            stats_db["total_system_downloads"] += 1
            write_json("stats.json", stats_db)
            
            # تحديث الزر
            current_dls = stats_db["posts_stats"][pid]["downloads"]
            mk = call.message.reply_markup
            mk.keyboard[0][1].text = f"📥 استلام ({current_dls})"
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mk)
            
            # توجيه المستخدم للبوت
            bot.answer_callback_query(call.id, "جاري فتح الملفات...")
            bot.send_message(uid, "🚀 تفضل، هذه هي الملفات المتاحة لهذا المنشور:")
            send_all_available_files(uid)

    # 3. إدارة الصلاحيات للأدمن (المطور فقط)
    elif data.startswith("edit_p_"):
        if not is_main_dev(uid): return
        _, _, target_id, p_key = data.split("_")
        admins = read_json("admins.json")
        admins[target_id][p_key] = not admins[target_id].get(p_key, False)
        write_json("admins.json", admins)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_perms_inline_kb(target_id))

    # 4. حذف قناة اشتراك
    elif data.startswith("del_sub_"):
        if not is_main_dev(uid): return
        idx = int(data.split("_")[2])
        subs = read_json("subs.json")
        subs.pop(idx)
        write_json("subs.json", subs)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_subs_inline_kb())

    elif data == "close_p":
        bot.delete_message(call.message.chat.id, call.message.message_id)

# --- [ 12. دوال مساعدة إضافية (تطويل الكود ودقته) ] ---

def step_set_admin_perms(message):
    """بدء عملية تحديد صلاحيات الأدمن الجديد"""
    if message.text.isdigit():
        target_id = message.text
        admins_db = read_json("admins.json")
        if target_id not in admins_db:
            admins_db[target_id] = {
                "upload": False, "post": False, "broadcast": False,
                "stats": False, "reset": False, "clean": False
            }
        write_json("admins.json", admins_db)
        bot.send_message(message.chat.id, f"⚙️ تحكم بصلاحيات الأدمن `{target_id}`:", reply_markup=get_perms_inline_kb(target_id), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ خطأ: الآيدي يجب أن يكون أرقام فقط.")

def get_perms_inline_kb(admin_id):
    """توليد أزرار الصلاحيات للأدمن"""
    mk = types.InlineKeyboardMarkup(row_width=2)
    db = read_json("admins.json").get(str(admin_id), {})
    
    keys = {
        "upload": "رفع 📤", "post": "نشر 📣", "broadcast": "إذاعة 📢",
        "stats": "📊", "reset": "🗑️", "clean": "🧹"
    }
    
    btns = []
    for k, v in keys.items():
        status = "✅" if db.get(k) else "❌"
        btns.append(types.InlineKeyboardButton(f"{v} {status}", callback_data=f"edit_p_{admin_id}_{k}"))
    
    mk.add(*btns)
    mk.add(types.InlineKeyboardButton("🔙 إنهاء التعديل", callback_data="close_p"))
    return mk

def send_all_available_files(uid):
    """إرسال كافة الملفات المخزنة للمستخدم"""
    files = read_json("bot_files.json")
    if not files:
        bot.send_message(uid, "❌ لا توجد ملفات متوفرة حالياً.")
        return
        
    for f in files:
        try:
            bot.send_document(uid, f['file_id'], caption=f['caption'])
            time.sleep(0.3)
        except: continue

def generate_stats_report(uid):
    """إنتاج تقرير إحصائي مفصل"""
    users = get_all_users()
    files = read_json("bot_files.json")
    stats = read_json("stats.json")
    
    report = (
        f"📊 **تقرير نظام Uchiha Dz الشامل:**\n\n"
        f"👥 عدد المشتركين: `{len(users)}` مستخدم\n"
        f"📂 إجمالي الملفات: `{len(files)}` ملف\n"
        f"❤️ إجمالي التفاعلات: `{stats['total_system_likes']}`\n"
        f"📥 إجمالي طلبات الاستلام: `{stats['total_system_downloads']}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"🕒 الوقت: {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    bot.send_message(uid, report, parse_mode="Markdown")

# --- [ 13. تشغيل النظام (Main Loop) ] ---

if __name__ == "__main__":
    logger.info("-------------------------------------------")
    logger.info("🚀 Uchiha Dz System Version 4.0.0 is Active")
    logger.info(f"🛠️ Master Developer ID: {OWNER_ID}")
    logger.info("-------------------------------------------")
    
    # ميزة الحماية من الانهيار وإعادة التشغيل التلقائي
    while True:
        try:
            bot.infinity_polling(timeout=40, long_polling_timeout=20)
        except Exception as critical_error:
            logger.critical(f"System Crash Detected: {critical_error}")
            time.sleep(10) # انتظار قبل إعادة التشغيل
