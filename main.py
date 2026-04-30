# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (ULTRA-LONG & DETAILED) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 2000.0.0 (NO COMPRESSION - RAW SOURCE CODE)
# 🛡️ Status: FULLY STABLE | ENVIRONMENT: TERMUX / LINUX / ANDROID
# =========================================================================

import telebot
from telebot import types
import os
import json
import time
import sys

# --- [ 1. تعريف الثوابت والإعدادات الأولية ] ---

# توكن البوت (سرية للغاية)
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"

# معرف المطور (SELVA ZOLDEK)
DEVELOPER_ID = 8611300267 

# معرف القناة الرسمية للنشر
OFFICIAL_CHANNEL_ID = "@Uchiha75"

# إنشاء كائن البوت مع دعم تعدد المهام
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# --- [ 2. نظام إدارة ملفات النظام وقاعدة البيانات ] ---

def get_system_file(file_name, default_value):
    """دالة مطولة لقراءة الملفات مع التحقق من السلامة"""
    file_path = os.path.join(os.getcwd(), file_name)
    
    if not os.path.exists(file_path):
        # إنشاء ملف جديد في حالة عدم الوجود
        with open(file_path, "w", encoding="utf-8") as file_handle:
            json.dump(default_value, file_handle, indent=4, ensure_ascii=False)
        return default_value
    
    # محاولة قراءة البيانات
    try:
        with open(file_path, "r", encoding="utf-8") as file_handle:
            content = json.load(file_handle)
            return content
    except Exception as error_msg:
        print(f"Error reading {file_name}: {error_msg}")
        return default_value

def set_system_file(file_name, data_to_save):
    """دالة مطولة لحفظ البيانات لضمان عدم التلف"""
    file_path = os.path.join(os.getcwd(), file_name)
    try:
        with open(file_path, "w", encoding="utf-8") as file_handle:
            json.dump(data_to_save, file_handle, indent=4, ensure_ascii=False)
        return True
    except Exception as error_msg:
        print(f"Error saving {file_name}: {error_msg}")
        return False

# تهيئة ملفات النظام عند الإقلاع
def initialize_all_files():
    # ملف الإحصائيات والعدادات
    get_system_file("stats.json", {"likes": 0, "receives": 0})
    
    # ملف الأدمنية والصلاحيات
    initial_admin_setup = {
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
    get_system_file("admins.json", initial_admin_setup)
    
    # ملف تخزين الروابط
    get_system_file("subs.json", [])
    
    # ملف قائمة المستخدمين (نصي)
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()

initialize_all_files()

# --- [ 3. نظام التحقق من الصلاحيات والاشتراك ] ---

def check_permission(user_id, perm_key):
    """التحقق مما إذا كان المستخدم يملك صلاحية معينة"""
    if user_id == DEVELOPER_ID:
        return True
    
    all_admins = get_system_file("admins.json", {})
    user_str_id = str(user_id)
    
    if user_str_id in all_admins:
        admin_perms = all_admins[user_str_id].get("perms", {})
        if admin_perms.get(perm_key) == True:
            return True
            
    return False

# --- [ 4. بناة واجهات المستخدم (Keyboards) ] ---

def build_main_admin_kb(uid):
    """بناء الكيبورد الرئيسي للأدمن مع التحقق من كل زر"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # إضافة الأزرار بناءً على الصلاحيات الممنوحة
    if check_permission(uid, "upload"):
        markup.add("إضافة ملفات 📤")
    
    if check_permission(uid, "publish"):
        markup.add("نشر في القناة 📣")
        
    if check_permission(uid, "stats"):
        markup.add("الإحصائيات 📊")
        
    if check_permission(uid, "broadcast"):
        markup.add("قسم الإذاعة 📡")
        
    # أزرار الإمبراطور (المطور) فقط
    if uid == DEVELOPER_ID:
        markup.row("تنظيف بيانات 🧹", "تصفير ملفات 🗑️")
        markup.row("صلاحيات أدمن ⚙️", "إدارة الاشتراك 🔗")
        
    markup.add("🔙 العودة للمنزل")
    return markup

def build_broadcast_kb():
    """بناء كيبورد الإذاعة الثلاثي"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("إذاعة مستخدمين 👤", "إذاعة قناة 📣")
    markup.row("إذاعة الجميع 🌍")
    markup.add("لوحة تحكم الأدمن 🛠️")
    return markup

def build_admin_management_inline(admin_id):
    """بناء لوحة التحكم في الصلاحيات (أزرار شفافة)"""
    db = get_system_file("admins.json", {})
    target_perms = db[str(admin_id)]["perms"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # مسميات الصلاحيات الستة التي طلبتها
    labels = {
        "upload": "إضافة ملف 📤",
        "publish": "نشر 📣",
        "stats": "إحصائيات 📊",
        "reset": "تصفير 🗑️",
        "clean": "تنظيف 🧹",
        "broadcast": "إذاعة 📡"
    }
    
    for key, text in labels.items():
        status = "✅" if target_perms.get(key) else "❌"
        # توليد Callback: TOGGLE_ID_KEY
        markup.add(types.InlineKeyboardButton(f"{text}: {status}", callback_data=f"TOG_{admin_id}_{key}"))
        
    markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة", callback_data="BACK_LIST"))
    return markup

# --- [ 5. معالج الأوامر (Command Handlers) ] ---

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    uid = message.from_user.id
    username = message.from_user.first_name
    
    # تسجيل المستخدم في ملف users.txt
    with open("users.txt", "a+") as f:
        f.seek(0)
        users_list = f.read()
        if str(uid) not in users_list:
            f.write(str(uid) + "\n")

    # الرسالة الترحيبية الفخمة للمطور
    if uid == DEVELOPER_ID:
        welcome_text = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
    else:
        welcome_text = f"أهلاً بك {username} في نظام Uchiha Dz ⚡"

    # عرض الأزرار المناسبة
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if str(uid) in get_system_file("admins.json", {}) or uid == DEVELOPER_ID:
        main_kb.add("لوحة تحكم الأدمن 🛠️")
    else:
        main_kb.add("استلام الملفات 📥")
        
    bot.send_message(uid, welcome_text, reply_markup=main_kb)

# --- [ 6. الراوتر الرئيسي لمعالجة الأزرار (The Engine) ] ---

@bot.message_handler(func=lambda message: True)
def main_router_engine(message):
    uid = message.from_user.id
    text = message.text
    
    # فحص الرتبة
    admins_db = get_system_file("admins.json", {})
    is_admin = str(uid) in admins_db or uid == DEVELOPER_ID
    
    if not is_admin:
        return

    # --- [ أزرار التحكم الرئيسية ] ---
    
    if text == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(uid, "🛠️ غرفة التحكم بالوحش مفتوحة:", reply_markup=build_main_admin_kb(uid))

    elif text == "الإحصائيات 📊":
        if check_permission(uid, "stats"):
            stats = get_system_file("stats.json", {"likes":0, "receives":0})
            msg = "📊 إحصائيات النظام الشاملة:\n\n"
            msg += f"💎 عدد التفاعلات: {stats.get('likes')}\n"
            msg += f"📥 عدد الملفات المستلمة: {stats.get('receives')}"
            bot.send_message(uid, msg)

    elif text == "قسم الإذاعة 📡":
        if check_permission(uid, "broadcast"):
            bot.send_message(uid, "📡 اختر المسار المطلوب للإذاعة:", reply_markup=build_broadcast_kb())

    # --- [ منطق الإذاعة المتقدم ] ---
    
    elif text == "إذاعة مستخدمين 👤":
        if check_permission(uid, "broadcast"):
            msg = bot.send_message(uid, "📝 أرسل الآن المنشور المخصص للمستخدمين:")
            bot.register_next_step_handler(msg, perform_broadcast, "users")

    elif text == "إذاعة قناة 📣":
        if check_permission(uid, "broadcast"):
            msg = bot.send_message(uid, "📝 أرسل الآن المنشور المخصص للقناة:")
            bot.register_next_step_handler(msg, perform_broadcast, "channel")

    elif text == "إذاعة الجميع 🌍":
        if check_permission(uid, "broadcast"):
            msg = bot.send_message(uid, "📝 أرسل الآن المنشور المخصص للجميع (قناة + مستخدمين):")
            bot.register_next_step_handler(msg, perform_broadcast, "all")

    # --- [ أزرار الإمبراطور فقط ] ---

    elif text == "تنظيف بيانات 🧹":
        if uid == DEVELOPER_ID:
            set_system_file("stats.json", {"likes": 0, "receives": 0})
            bot.send_message(uid, "🧹 تم تصفير جميع العدادات وسجلات الإحصائيات.")

    elif text == "تصفير ملفات 🗑️":
        if uid == DEVELOPER_ID:
            set_system_file("bot_files.json", [])
            bot.send_message(uid, "🗑️ تم مسح قاعدة بيانات الملفات بالكامل.")

    elif text == "صلاحيات أدمن ⚙️" and uid == DEVELOPER_ID:
        markup = types.InlineKeyboardMarkup()
        for admin_id, info in admins_db.items():
            if int(admin_id) != DEVELOPER_ID:
                markup.add(types.InlineKeyboardButton(f"👤 {info['name']}", callback_data=f"MNG_{admin_id}"))
        bot.send_message(uid, "⚙️ قائمة الأدمنية (اختر لتعديل الصلاحيات):", reply_markup=markup)

    elif text == "🔙 العودة للمنزل":
        handle_start_command(message)

# --- [ 7. دالة تنفيذ الإذاعة (Broadcast Execution) ] ---

def perform_broadcast(message, target_type):
    admin_id = message.from_user.id
    done_count = 0
    
    # إذاعة للمستخدمين
    if target_type in ["users", "all"]:
        with open("users.txt", "r") as f:
            for user_line in f.readlines():
                target_uid = user_line.strip()
                try:
                    bot.copy_message(target_uid, admin_id, message.message_id)
                    done_count += 1
                except:
                    continue
                    
    # إذاعة للقناة
    if target_type in ["channel", "all"]:
        try:
            bot.copy_message(OFFICIAL_CHANNEL_ID, admin_id, message.message_id)
            if target_type == "channel": done_count = 1
        except Exception as e:
            bot.send_message(admin_id, f"❌ فشل النشر في القناة: {e}")

    bot.send_message(admin_id, f"✅ تم الانتهاء من الإذاعة!\n🎯 الأهداف الناجحة: {done_count}")

# --- [ 8. معالجة التفاعلات الخلفية (Callback Logic) ] ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler_engine(call):
    uid, mid, cid, data = call.from_user.id, call.message.message_id, call.message.chat.id, call.data

    if data.startswith("MNG_"):
        target_aid = data.split("_")[1]
        bot.edit_message_text(f"⚙️ إدارة صلاحيات الأدمن: `{target_aid}`", cid, mid, reply_markup=build_admin_management_inline(target_aid))

    elif data.startswith("TOG_"):
        # TOG_ID_KEY
        parts = data.split("_")
        target_aid = parts[1]
        perm_key = parts[2]
        
        db = get_system_file("admins.json", {})
        if target_aid in db:
            # عكس القيمة (Toggle)
            db[target_aid]["perms"][perm_key] = not db[target_aid]["perms"].get(perm_key, False)
            set_system_file("admins.json", db)
            
            # تحديث الواجهة فوراً
            bot.edit_message_reply_markup(cid, mid, reply_markup=build_admin_management_inline(target_aid))
            bot.answer_callback_query(call.id, "✅ تم التحديث بنجاح")

    elif data == "BACK_LIST":
        db = get_system_file("admins.json", {})
        markup = types.InlineKeyboardMarkup()
        for aid, info in db.items():
            if int(aid) != DEVELOPER_ID:
                markup.add(types.InlineKeyboardButton(f"👤 {info['name']}", callback_data=f"MNG_{aid}"))
        bot.edit_message_text("⚙️ قائمة الأدمنية:", cid, mid, reply_markup=markup)

# --- [ 9. نظام العداد التلقائي للاستلام ] ---

@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice'])
def increment_receive_counter(message):
    # تحديث ملف الإحصائيات
    stats_data = get_system_file("stats.json", {"likes": 0, "receives": 0})
    
    # زيادة العداد بمقدار 1
    stats_data["receives"] = stats_data.get("receives", 0) + 1
    
    # حفظ البيانات
    set_system_file("stats.json", stats_data)
    
    # رد فعل للبوت
    if check_permission(message.from_user.id, "upload"):
        bot.reply_to(message, "📥 تم استلام الملف وتحديث العداد في الإحصائيات بنجاح.")

# --- [ 10. تشغيل النظام ومراقبة الأخطاء ] ---

if __name__ == "__main__":
    # إشعار المطور بالبدء
    try:
        startup_msg = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
        bot.send_message(DEVELOPER_ID, startup_msg)
    except:
        pass
        
    print(">>> Uchiha Dz Supreme System is running...")
    
    # منع البوت من التوقف (Infinite Polling)
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=40)
        except Exception as e:
            print(f">>> Crash detected: {e}. Restarting in 5 seconds...")
            time.sleep(5)
            continue

