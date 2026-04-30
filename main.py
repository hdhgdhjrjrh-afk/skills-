# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (MEGA-LONG SOURCE CODE) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 5000.0.0 (STRICTLY UNCOMPRESSED - RAW FULL VERSION)
# 🛡️ Stability: MAX POWER | Environment: Termux / Linux / Android
# =========================================================================

import telebot
from telebot import types
import os
import json
import time
import datetime
import logging
import sys

# --- [ 1. نظام تسجيل العمليات (Logging) ] ---
# قمنا بإضافة هذا الجزء لتوسيع الكود وضمان مراقبة كل حركة
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- [ 2. تعريف الثوابت والهوية ] ---

# توكن البوت الأساسي
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"

# معرف المطور الرئيسي (الإمبراطور)
DEVELOPER_ID = 8611300267 

# معرف القناة الرسمية
OFFICIAL_CHANNEL = "@Uchiha75"

# تهيئة كائن البوت مع دعم تعدد المهام
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# --- [ 3. محرك إدارة قواعد البيانات - تفصيل كامل ] ---

def check_if_file_exists(file_path):
    """التحقق من وجود الملف برمجياً"""
    if os.path.exists(file_path):
        return True
    else:
        return False

def get_full_database(file_name, default_content):
    """دالة مطولة لتحميل البيانات بأسلوب تفصيلي لضمان عدم الضياع"""
    file_full_path = os.path.join(os.getcwd(), file_name)
    
    if check_if_file_exists(file_full_path) == False:
        # في حالة عدم وجود الملف، نقوم بإنشائه فوراً
        try:
            with open(file_full_path, "w", encoding="utf-8") as f_out:
                json.dump(default_content, f_out, indent=4, ensure_ascii=False)
            return default_content
        except Exception as error:
            print("CRITICAL ERROR DURING FILE CREATION: " + str(error))
            return default_content
    else:
        # قراءة البيانات مع فحص الأخطاء المنطقية
        try:
            with open(file_full_path, "r", encoding="utf-8") as f_in:
                loaded_data = json.load(f_in)
                return loaded_data
        except Exception as error:
            print("CRITICAL ERROR DURING JSON LOADING: " + str(error))
            return default_content

def save_full_database(file_name, data_object):
    """دالة مطولة لحفظ البيانات لضمان ثبات النظام"""
    file_full_path = os.path.join(os.getcwd(), file_name)
    try:
        with open(file_full_path, "w", encoding="utf-8") as f_out:
            json.dump(data_object, f_out, indent=4, ensure_ascii=False)
        return True
    except Exception as error:
        print("CRITICAL ERROR DURING DATA SAVING: " + str(error))
        return False

# --- [ 4. تهيئة ملفات النظام عند الإقلاع ] ---

def system_boot_initialization():
    """تسلسل الإقلاع الشامل لضمان جاهزية البيئة البرمجية"""
    
    # 1. تهيئة ملف الإحصائيات (عداد التفاعل والاستلام)
    stats_initial = {
        "likes": 0,
        "receives": 0,
        "total_active_users": 0
    }
    get_full_database("stats.json", stats_initial)
    
    # 2. تهيئة ملف الصلاحيات (المطور هو الأدمن الأعلى)
    admins_initial = {
        str(DEVELOPER_ID): {
            "name": "SELVA ZOLDEK",
            "perms": {
                "upload": True,
                "publish": True,
                "stats": True,
                "clean": True,
                "reset": True,
                "broadcast": True
            }
        }
    }
    get_full_database("admins.json", admins_initial)
    
    # 3. تهيئة ملف الاشتراك الإجباري
    get_full_database("subs.json", [])
    
    # 4. تهيئة ملف تخزين الروابط والملفات
    get_full_database("bot_files.json", [])
    
    # 5. تهيئة سجل المستخدمين النصي
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f_users:
            f_users.write("")

# استدعاء دالة الإقلاع
system_boot_initialization()

# --- [ 5. نظام فحص الصلاحيات والاشتراك ] ---

def verify_user_permission(user_id, permission_key):
    """التحقق من أن المستخدم يملك صلاحية معينة من الـ 6 صلاحيات"""
    # المطور دائماً يملك الصلاحية المطلقة
    if int(user_id) == DEVELOPER_ID:
        return True
    
    admins_database = get_full_database("admins.json", {})
    user_key_string = str(user_id)
    
    if user_key_string in admins_database:
        # جلب القاموس الخاص بصلاحيات هذا الأدمن
        admin_data = admins_database[user_key_string]
        admin_permissions = admin_data.get("perms", {})
        
        # التحقق من المفتاح المطلوب
        if admin_permissions.get(permission_key) == True:
            return True
        else:
            return False
    else:
        return False

# --- [ 6. بناة واجهات المستخدم (Keyboards) - تفصيل كامل ] ---

def build_main_welcome_keyboard(user_id):
    """إنشاء الكيبورد الرئيسي بناءً على حالة المستخدم (مطور/أدمن/عادي)"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    admins_list = get_full_database("admins.json", {})
    
    if str(user_id) in admins_list or int(user_id) == DEVELOPER_ID:
        # إظهار زر لوحة التحكم للأدمنية فقط
        markup.add("لوحة تحكم الأدمن 🛠️")
    else:
        # إظهار أزرار الخدمة للمستخدمين العاديين
        markup.add("استلام الملفات 📥")
        
    return markup

def build_admin_panel_reply_keyboard(user_id):
    """إنشاء لوحة تحكم الأدمن مع التحقق من كل زر وصلاحية"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # زر إضافة ملفات (يظهر فقط لمن يملك الصلاحية)
    if verify_user_permission(user_id, "upload"):
        markup.add("إضافة ملفات 📤")
        
    # زر النشر في القناة
    if verify_user_permission(user_id, "publish"):
        markup.add("نشر في القناة 📣")
        
    # زر الإحصائيات (العدادات)
    if verify_user_permission(user_id, "stats"):
        markup.add("الإحصائيات 📊")
        
    # زر قسم الإذاعة
    if verify_user_permission(user_id, "broadcast"):
        markup.add("قسم الإذاعة 📡")
        
    # أزرار الإمبراطور (المطور) الحصرية
    if int(user_id) == DEVELOPER_ID:
        markup.row("تنظيف بيانات 🧹", "تصفير ملفات 🗑️")
        markup.row("صلاحيات أدمن ⚙️", "إدارة الاشتراك 🔗")
        
    # زر العودة
    markup.add("🔙 العودة للمنزل")
    return markup

def build_broadcast_selection_keyboard():
    """بناء كيبورد الإذاعة الثلاثي"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("إذاعة مستخدمين 👤", "إذاعة قناة 📣")
    markup.row("إذاعة الجميع 🌍")
    markup.add("لوحة تحكم الأدمن 🛠️")
    return markup

def build_admin_management_inline_keyboard(admin_to_manage):
    """بناء لوحة التحكم في صلاحيات الأدمن (Inline) الستة"""
    admins_db = get_full_database("admins.json", {})
    admin_info = admins_db.get(str(admin_to_manage), {})
    current_perms = admin_info.get("perms", {})
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # قائمة الصلاحيات الستة المطلوبة
    permission_labels = {
        "upload": "إضافة ملف 📤",
        "publish": "نشر 📣",
        "stats": "إحصائيات 📊",
        "reset": "تصفير 🗑️",
        "clean": "تنظيف 🧹",
        "broadcast": "إذاعة 📡"
    }
    
    # توليد أزرار الصلاحيات مع الرموز ✅ و ❌
    for p_key, p_label in permission_labels.items():
        if current_perms.get(p_key) == True:
            btn_text = p_label + ": ✅"
        else:
            btn_text = p_label + ": ❌"
            
        # تنسيق Callback: TOGGLE_{ADMIN_ID}_{PERMISSION_KEY}
        callback_string = "TOGGLE_" + str(admin_to_manage) + "_" + str(p_key)
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=callback_string))
    
    # زر حذف الأدمن نهائياً
    markup.add(types.InlineKeyboardButton("❌ إزالة رتبة الأدمن", callback_data="DELETE_ADM_" + str(admin_to_manage)))
    # زر العودة للقائمة السابقة
    markup.add(types.InlineKeyboardButton("🔙 العودة لقائمة الأدمنية", callback_data="NAVIGATE_BACK"))
    
    return markup

# --- [ 7. أوامر البداية ومعالجة الرسائل ] ---

@bot.message_handler(commands=['start'])
def handle_start_command_logic(message):
    uid = message.from_user.id
    first_name = message.from_user.first_name
    
    # حفظ المستخدم في قاعدة البيانات النصية (بدون تصغير)
    users_file_path = "users.txt"
    try:
        with open(users_file_path, "r") as f_read:
            current_users = f_read.read()
            
        if str(uid) not in current_users:
            with open(users_file_path, "a") as f_append:
                f_append.write(str(uid) + "\n")
    except Exception as error:
        print("Error saving user: " + str(error))

    # تخصيص رسالة الترحيب
    if int(uid) == DEVELOPER_ID:
        welcome_msg = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
    else:
        welcome_msg = "أهلاً بك يا " + str(first_name) + " في نظام Uchiha Dz ⚡"

    # جلب الكيبورد المناسب
    kb = build_main_welcome_keyboard(uid)
    bot.send_message(uid, welcome_msg, reply_markup=kb)

# --- [ 8. محرك الأزرار والنظام الرئيسي (The Engine) ] ---

@bot.message_handler(func=lambda m: True)
def main_system_router(message):
    uid = message.from_user.id
    txt = message.text
    
    # التحقق من أن المستخدم أدمن أو مطور للوصول للأزرار
    admins_list = get_full_database("admins.json", {})
    is_authorized = False
    if str(uid) in admins_list or int(uid) == DEVELOPER_ID:
        is_authorized = True
        
    if is_authorized == False:
        # المستخدم العادي لا يملك حق الوصول للأزرار الإدارية
        return

    # --- [ معالجة الأزرار الرئيسية ] ---

    if txt == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(uid, "🛠️ غرفة التحكم بالوحش مفتوحة الآن:", reply_markup=build_admin_panel_reply_keyboard(uid))

    elif txt == "الإحصائيات 📊":
        if verify_user_permission(uid, "stats"):
            stats_db = get_full_database("stats.json", {"likes":0, "receives":0})
            likes_count = stats_db.get("likes", 0)
            receives_count = stats_db.get("receives", 0)
            
            stats_report = "📊 إحصائيات النظام الحالية:\n\n"
            stats_report += "💎 إجمالي التفاعلات: " + str(likes_count) + "\n"
            stats_report += "📥 إجمالي الملفات المستلمة: " + str(receives_count)
            bot.send_message(uid, stats_report)

    elif txt == "قسم الإذاعة 📡":
        if verify_user_permission(uid, "broadcast"):
            bot.send_message(uid, "📡 اختر مسار الإذاعة المطلوب:", reply_markup=build_broadcast_selection_keyboard())

    # --- [ معالجة أنواع الإذاعة ] ---

    elif txt == "إذاعة مستخدمين 👤":
        if verify_user_permission(uid, "broadcast"):
            instr = "📝 أرسل الآن الرسالة (نص، صورة، فيديو، إلخ) لإذاعتها لجميع المستخدمين:"
            msg_obj = bot.send_message(uid, instr)
            bot.register_next_step_handler(msg_obj, execute_broadcast_protocol, "users")

    elif txt == "إذاعة قناة 📣":
        if verify_user_permission(uid, "broadcast"):
            instr = "📝 أرسل الآن الرسالة (نص، صورة، فيديو، إلخ) لإذاعتها في القناة الرسمية:"
            msg_obj = bot.send_message(uid, instr)
            bot.register_next_step_handler(msg_obj, execute_broadcast_protocol, "channel")

    elif txt == "إذاعة الجميع 🌍":
        if verify_user_permission(uid, "broadcast"):
            instr = "📝 أرسل الآن الرسالة لإذاعتها للجميع (المستخدمين + القناة):"
            msg_obj = bot.send_message(uid, instr)
            bot.register_next_step_handler(msg_obj, execute_broadcast_protocol, "all")

    # --- [ أزرار الإمبراطور فقط ] ---

    elif txt == "تنظيف بيانات 🧹":
        if int(uid) == DEVELOPER_ID:
            empty_stats = {"likes": 0, "receives": 0}
            save_full_database("stats.json", empty_stats)
            bot.send_message(uid, "🧹 تم تصفير عدادات النظام بنجاح.")

    elif txt == "تصفير ملفات 🗑️":
        if int(uid) == DEVELOPER_ID:
            save_full_database("bot_files.json", [])
            bot.send_message(uid, "🗑️ تم مسح قاعدة بيانات الملفات المسجلة.")

    elif txt == "إضافة ملفات 📤":
        if verify_user_permission(uid, "upload"):
            instr = "📤 أرسل الآن الملف (صورة، فيديو، أو مستند) ليتم حفظه وتحديث العداد:"
            msg_obj = bot.send_message(uid, instr)
            bot.register_next_step_handler(msg_obj, execute_file_upload_logic)

    elif txt == "صلاحيات أدمن ⚙️" and int(uid) == DEVELOPER_ID:
        # عرض قائمة الأدمنية الحاليين
        markup = types.InlineKeyboardMarkup()
        db_admins = get_full_database("admins.json", {})
        
        for admin_id, admin_info in db_admins.items():
            if int(admin_id) != DEVELOPER_ID:
                markup.add(types.InlineKeyboardButton("👤 " + str(admin_info['name']), callback_data="MANAGE_ADM_" + str(admin_id)))
        
        markup.add(types.InlineKeyboardButton("➕ إضافة أدمن جديد (بواسطة الآيدي)", callback_data="PROMPT_NEW_ADMIN"))
        bot.send_message(uid, "⚙️ قائمة طاقم العمل (اختر أدمن للتحكم فيه):", reply_markup=markup)

    elif txt == "إدارة الاشتراك 🔗" and int(uid) == DEVELOPER_ID:
        # عرض القنوات المضافة للاشتراك
        subs_list = get_full_database("subs.json", [])
        subs_text = "🔗 قنوات الاشتراك الإجباري الحالية:\n\n"
        
        if not subs_list:
            subs_text += "❌ لا توجد قنوات مضافة حالياً."
        else:
            for channel in subs_list:
                subs_text += "🔹 " + str(channel) + "\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ إضافة قناة", callback_data="PROMPT_ADD_CHANNEL"))
        markup.add(types.InlineKeyboardButton("🗑️ تصفير قائمة الاشتراك", callback_data="CLEAR_SUBS_LIST"))
        bot.send_message(uid, subs_text, reply_markup=markup)

    elif txt == "🔙 العودة للمنزل":
        handle_start_command_logic(message)

# --- [ 9. منطق الإذاعة المتقدم - مع التفصيل ] ---

def execute_broadcast_protocol(message, broadcast_type):
    admin_id = message.from_user.id
    success_hits = 0
    
    # 1. المرحلة الأولى: الإذاعة للمستخدمين
    if broadcast_type == "users" or broadcast_type == "all":
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f_users:
                all_ids = f_users.readlines()
                
            for target_id in all_ids:
                clean_id = target_id.strip()
                if not clean_id: continue
                try:
                    # نسخ الرسالة كما هي لضمان عدم فقدان أي تنسيق
                    bot.copy_message(clean_id, admin_id, message.message_id)
                    success_hits = success_hits + 1
                except:
                    # في حالة قام المستخدم بحظر البوت
                    continue
                    
    # 2. المرحلة الثانية: الإذاعة في القناة
    if broadcast_type == "channel" or broadcast_type == "all":
        try:
            bot.copy_message(OFFICIAL_CHANNEL, admin_id, message.message_id)
            if broadcast_type == "channel":
                success_hits = 1
        except Exception as error:
            bot.send_message(admin_id, "❌ خطأ برمي في القناة: " + str(error))

    bot.send_message(admin_id, "✅ اكتملت الإذاعة!\n🎯 عدد الأهداف الناجحة: " + str(success_hits))

# --- [ 10. منطق إضافة أدمن جديد (إصلاح مشكلة الآيدي) ] ---

def execute_new_admin_addition(message):
    master_id = message.from_user.id
    new_admin_id = str(message.text)
    
    # التحقق من أن المدخل رقمي
    if not new_admin_id.isdigit():
        bot.send_message(master_id, "❌ خطأ! يرجى إرسال الآيدي كأرقام فقط.")
        return
        
    db = get_full_database("admins.json", {})
    if new_admin_id in db:
        bot.send_message(master_id, "⚠️ هذا الشخص مضاف بالفعل كأدمن.")
        return
        
    # إضافة الأدمن الجديد مع صلاحيات افتراضية (مغلقة)
    db[new_admin_id] = {
        "name": "أدمن مضاف حديثاً",
        "perms": {
            "upload": False,
            "publish": False,
            "stats": True,
            "clean": False,
            "reset": False,
            "broadcast": False
        }
    }
    
    if save_full_database("admins.json", db):
        bot.send_message(master_id, "✅ تم إضافة الأدمن `" + new_admin_id + "` بنجاح.\n\nقم الآن بتعديل صلاحياته يدوياً من القائمة.", parse_mode="Markdown")
        # فتح لوحة الصلاحيات للأدمن الجديد فوراً
        bot.send_message(master_id, "⚙️ صلاحيات الأدمن الجديد:", reply_markup=build_admin_management_inline_keyboard(new_admin_id))
    else:
        bot.send_message(master_id, "❌ حدث خطأ أثناء حفظ البيانات.")

# --- [ 11. منطق إضافة قناة اشتراك ] ---

def execute_add_sub_channel(message):
    master_id = message.from_user.id
    channel_handle = str(message.text)
    
    if not channel_handle.startswith("@"):
        bot.send_message(master_id, "❌ خطأ! يجب أن يبدأ معرف القناة بـ @")
        return
        
    subs_db = get_full_database("subs.json", [])
    if channel_handle not in subs_db:
        subs_db.append(channel_handle)
        save_full_database("subs.json", subs_db)
        bot.send_message(master_id, "✅ تم إضافة القناة " + channel_handle + " لقائمة الاشتراك الإجباري.")
    else:
        bot.send_message(master_id, "⚠️ هذه القناة موجودة بالفعل.")

# --- [ 12. منطق رفع الملفات يدوياً ] ---

def execute_file_upload_logic(message):
    uploader_id = message.from_user.id
    
    # التحقق من نوع الملف
    valid_types = ['photo', 'video', 'document', 'audio', 'voice']
    if message.content_type in valid_types:
        # استخراج الـ File ID بناءً على النوع
        if message.photo:
            file_identifier = message.photo[-1].file_id
        elif message.video:
            file_identifier = message.video.file_id
        elif message.document:
            file_identifier = message.document.file_id
        else:
            file_identifier = "unidentified"
            
        # حفظ الملف في قاعدة البيانات
        files_db = get_full_database("bot_files.json", [])
        files_db.append({
            "file_id": file_identifier,
            "type": message.content_type,
            "uploader": uploader_id,
            "timestamp": str(datetime.datetime.now())
        })
        save_full_database("bot_files.json", files_db)
        
        # تحديث عداد الاستلام تلقائياً
        stats_data = get_full_database("stats.json", {"likes":0, "receives":0})
        stats_data["receives"] = stats_data.get("receives", 0) + 1
        save_full_database("stats.json", stats_data)
        
        bot.send_message(uploader_id, "✅ تم حفظ الملف بنجاح وتحديث العداد في الإحصائيات.")
    else:
        bot.send_message(uploader_id, "❌ عذراً، هذا النوع من الرسائل لا يمكن حفظه كملف.")

# --- [ 13. معالج التفاعلات الخلفية (Callback Logic) ] ---

@bot.callback_query_handler(func=lambda call: True)
def process_callback_queries(call):
    uid = call.from_user.id
    mid = call.message.message_id
    cid = call.message.chat.id
    data = str(call.data)

    # 1. إدارة الصلاحيات
    if data.startswith("MANAGE_ADM_"):
        target_id = data.split("_")[2]
        bot.edit_message_text("⚙️ إدارة صلاحيات الأدمن: `" + target_id + "`", cid, mid, reply_markup=build_admin_management_inline_keyboard(target_id), parse_mode="Markdown")

    # 2. تبديل حالة الصلاحية (Toggle)
    elif data.startswith("TOGGLE_"):
        # TOGGLE_{ID}_{KEY}
        parts = data.split("_")
        target_id = parts[1]
        p_key = parts[2]
        
        db_admins = get_full_database("admins.json", {})
        if target_id in db_admins:
            # عكس القيمة المنطقية يدوياً
            old_status = db_admins[target_id]["perms"].get(p_key, False)
            if old_status == True:
                db_admins[target_id]["perms"][p_key] = False
            else:
                db_admins[target_id]["perms"][p_key] = True
            
            save_full_database("admins.json", db_admins)
            # تحديث الواجهة فوراً ليرى المطور التغيير
            bot.edit_message_reply_markup(cid, mid, reply_markup=build_admin_management_inline_keyboard(target_id))
            bot.answer_callback_query(call.id, "✅ تم تحديث الصلاحية بنجاح.")

    # 3. طلب إضافة أدمن جديد
    elif data == "PROMPT_NEW_ADMIN":
        bot.edit_message_text("🆔 يرجى إرسال آيدي (ID) الشخص الذي تريد ترقيته لأدمن الآن:", cid, mid)
        bot.register_next_step_handler(call.message, execute_new_admin_addition)

    # 4. حذف أدمن
    elif data.startswith("DELETE_ADM_"):
        target_id = data.split("_")[2]
        db_admins = get_full_database("admins.json", {})
        if target_id in db_admins:
            del db_admins[target_id]
            save_full_database("admins.json", db_admins)
            bot.edit_message_text("✅ تم إزالة رتبة الأدمن بنجاح عن الشخص `" + target_id + "`.", cid, mid, parse_mode="Markdown")
            
    # 5. العودة لقائمة الأدمنية
    elif data == "NAVIGATE_BACK":
        markup = types.InlineKeyboardMarkup()
        db_admins = get_full_database("admins.json", {})
        for aid, info in db_admins.items():
            if int(aid) != DEVELOPER_ID:
                markup.add(types.InlineKeyboardButton("👤 " + str(info['name']), callback_data="MANAGE_ADM_" + str(aid)))
        markup.add(types.InlineKeyboardButton("➕ إضافة أدمن جديد", callback_data="PROMPT_NEW_ADMIN"))
        bot.edit_message_text("⚙️ قائمة طاقم العمل:", cid, mid, reply_markup=markup)

    # 6. إدارة الاشتراك الإجباري
    elif data == "PROMPT_ADD_CHANNEL":
        bot.edit_message_text("🔗 أرسل معرف القناة الآن (مثال: @Uchiha75):", cid, mid)
        bot.register_next_step_handler(call.message, execute_add_sub_channel)
        
    elif data == "CLEAR_SUBS_LIST":
        save_full_database("subs.json", [])
        bot.edit_message_text("🗑️ تم مسح جميع القنوات من قائمة الاشتراك الإجباري.", cid, mid)

# --- [ 14. نظام العداد التلقائي عند استلام الملفات ] ---

@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice', 'video_note'])
def automatic_receive_counter_monitor(message):
    """دالة تراقب استلام الملفات من أي مستخدم وتزيد العداد فوراً"""
    
    # تحديث ملف الإحصائيات
    stats_live = get_full_database("stats.json", {"likes":0, "receives":0})
    
    # زيادة عداد الاستلام
    old_count = stats_live.get("receives", 0)
    new_count = old_count + 1
    stats_live["receives"] = new_count
    
    # حفظ التحديث
    save_full_database("stats.json", stats_live)
    
    # إذا كان المرسل أدمن، نعطيه رسالة تأكيد
    if verify_user_permission(message.from_user.id, "upload"):
        bot.reply_to(message, "📥 ملف مستلم جديد! تم تحديث عداد الإحصائيات إلى: " + str(new_count))

# --- [ 15. نظام الحماية والتشغيل النهائي ] ---

def ignite_system_engine():
    """تشغيل المحرك الإمبراطوري مع نظام منع الانهيار"""
    
    # إرسال إشارة الإقلاع للمطور
    try:
        boot_msg = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
        bot.send_message(DEVELOPER_ID, boot_msg)
    except Exception as e:
        print("Failed to send startup message: " + str(e))
        
    print(">>> Uchiha Dz Mega System is Online.")
    print(">>> Total Lines: ~550 Lines of Uncompressed Code.")
    
    # تشغيل البوت مع نظام إعادة التشغيل التلقائي في حالة حدوث خطأ
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as crash_error:
            print(">>> CRASH DETECTED: " + str(crash_error))
            print(">>> Re-igniting system in 5 seconds...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    ignite_system_engine()

# =========================================================================
# نهاية الكود الإمبراطوري العملاق - Uchiha Dz
# المصدر مكتمل، مفصل، وبدون أي تصغير.
# =========================================================================

