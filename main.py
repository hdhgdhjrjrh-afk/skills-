# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (ULTRA LONG EDITION) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 30.0.0 (FULL DETAILED SOURCE CODE)
# 🛡️ Designed for Performance and GitHub Documentation
# =========================================================================

import telebot
from telebot import types
import os
import json
import time
import sys
import datetime

# --- [ 1. CONFIGURATION SECTION ] ---
# وضع الإعدادات في متغيرات واضحة لتسهيل التعديل
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
DEVELOPER_ID = 8611300267 
OFFICIAL_CHANNEL = "@Uchiha75"  

# إنشاء كائن البوت مع إعدادات الخيوط المتعددة للسرعة
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=100)

# ذاكرة الجلسة (Session Storage) لإدارة العمليات المعقدة
# نستخدم هذا الهيكل لتجنب تداخل البيانات بين المستخدمين
GLOBAL_SESSIONS = {
    "upload_buffer": {},    # لتخزين الملفات قبل التأكيد
    "broadcast_msg": {},    # لتخزين محتوى الإذاعة
    "admin_status": None,    # لتتبع حالة الأدمن الحالية
    "temp_sub_data": {}     # لتخزين بيانات القنوات الجديدة مؤقتاً
}

# --- [ 2. DATABASE MANAGEMENT SYSTEM ] ---

def load_database_file(file_path, default_structure):
    """دالة لقراءة البيانات من ملفات JSON بذكاء"""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_structure, f, indent=4, ensure_ascii=False)
        return default_structure
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default_structure

def save_database_file(file_path, data_to_save):
    """دالة لحفظ البيانات وضمان عدم ضياعها"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

# تهيئة الملفات الأساسية عند إقلاع البوت
def initialize_system_files():
    """التأكد من وجود كل ملفات البيانات اللازمة قبل التشغيل"""
    # ملف الإحصائيات والعدادات
    load_database_file("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
    # ملف تخزين معرفات الملفات
    load_database_file("bot_files.json", [])
    # ملف القنوات للاشتراك الإجباري
    load_database_file("subs.json", [])
    # ملف قائمة الأدمنية (المطور أولهم)
    load_database_file("admins.json", [DEVELOPER_ID])
    # ملف نصي لتخزين معرفات كل من استخدم البوت
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.close()

# تنفيذ التهيئة
initialize_system_files()

# --- [ 3. DYNAMIC KEYBOARD GENERATORS ] ---

def generate_channel_markup():
    """إنشاء أزرار القناة مع العدادات الحية"""
    # قراءة أحدث الإحصائيات
    stats_data = load_database_file("stats.json", {})
    like_count = stats_data.get("likes", 0)
    receive_count = stats_data.get("receives", 0)
    
    markup = types.InlineKeyboardMarkup()
    # زر التفاعل: يبقى في القناة ويزيد العداد
    like_btn = types.InlineKeyboardButton(f"تفاعل ❤️ ({like_count})", callback_data="ACTION_LIKE")
    # زر الاستلام: ينقل المستخدم للبوت مع بارامتر خاص للتحقق
    bot_username = bot.get_me().username
    get_btn = types.InlineKeyboardButton(f"استلم 📩 ({receive_count})", url=f"https://t.me/{bot_username}?start=verify_and_get")
    
    markup.row(like_btn, get_btn)
    return markup

def generate_admin_reply_keyboard():
    """إنشاء لوحة تحكم الأدمن الكبيرة والمفصلة"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # الصف الأول: العمليات الأساسية
    btn_upload = types.KeyboardButton("إضافة ملفات 📤")
    btn_publish = types.KeyboardButton("نشر في القناة 📣")
    
    # الصف الثاني: التواصل والإحصاء
    btn_bc = types.KeyboardButton("إذاعة متطورة 📡")
    btn_stats = types.KeyboardButton("الإحصائيات 📊")
    
    # الصف الثالث: التنظيف والإدارة
    btn_reset_f = types.KeyboardButton("تصفير ملفات 🗑️")
    btn_clean_d = types.KeyboardButton("تنظيف بيانات 🧹")
    
    # الصف الرابع: الإعدادات والعودة
    btn_subs = types.KeyboardButton("إدارة الاشتراك 🔗")
    btn_admins = types.KeyboardButton("صلاحيات أدمن ⚙️")
    btn_back = types.KeyboardButton("🔙 العودة")
    
    markup.add(btn_upload, btn_publish, btn_bc, btn_stats, btn_reset_f, btn_clean_d, btn_subs, btn_admins, btn_back)
    return markup

def generate_main_reply_keyboard(user_id):
    """الكيبورد الذي يظهر للمستخدم العادي أو المطور عند البداية"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    admin_list = load_database_file("admins.json", [DEVELOPER_ID])
    
    if user_id == DEVELOPER_ID or user_id in admin_list:
        markup.add(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"))
    else:
        markup.add(types.KeyboardButton("استلام الملفات 📥"))
    return markup

# --- [ 4. CORE HANDLERS: START & VERIFICATION ] ---

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    """معالجة أمر البداية والتحقق من التفاعل"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # تسجيل المستخدم في القائمة الشاملة (users.txt)
    with open("users.txt", "a+") as f:
        f.seek(0)
        content = f.read()
        if str(user_id) not in content:
            f.write(f"{user_id}\n")
    
    # التحقق إذا كان المستخدم ضغط "استلام" من القناة
    if "verify_and_get" in message.text:
        stats_data = load_database_file("stats.json", {})
        interacted_list = stats_data.get("interacted", [])
        
        # شرط التفاعل الصارم: يجب أن يكون ID المستخدم في قائمة من ضغطوا ❤️
        if user_id in interacted_list:
            received_list = stats_data.get("received", [])
            
            # إذا كان أول استلام له، نزيد العداد
            if user_id not in received_list:
                stats_data["receives"] += 1
                stats_data.setdefault("received", []).append(user_id)
                save_database_file("stats.json", stats_data)
            
            bot.send_message(user_id, f"✅ أهلاً {user_name}! تم التحقق من تفاعلك بنجاح.")
            
            # جلب الملفات من قاعدة البيانات وإرسالها
            all_files = load_database_file("bot_files.json", [])
            if not all_files:
                bot.send_message(user_id, "📂 قاعدة الملفات فارغة حالياً، انتظر النشر القادم.")
            else:
                for file_item in all_files:
                    try:
                        bot.send_document(user_id, file_item['file_id'], caption=file_item['caption'])
                    except Exception as send_err:
                        print(f"Error sending file: {send_err}")
        else:
            # رسالة الرفض إذا لم يتفاعل
            fail_msg = (f"⚠️ عذراً {user_name}!\n\n"
                        f"لقد ضغطت على زر الاستلام دون أن تضغط على (تفاعل ❤️) في القناة.\n\n"
                        f"فضلاً عد للقناة {OFFICIAL_CHANNEL} وتفاعل أولاً ثم حاول مجدداً.")
            bot.send_message(user_id, fail_msg)
        return

    # الترحيب العادي حسب الرتبة
    if user_id == DEVELOPER_ID:
        dev_welcome = (f"مرحبا ايها مطور 😈SELVA ZOLDEK 😈\n\n"
                       f"تم تشغيل نظام 'الوحش' بنجاح.\n"
                       f"الوقت الحالي: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        bot.send_message(user_id, dev_welcome, reply_markup=generate_main_reply_keyboard(user_id))
    else:
        user_welcome = "أهلاً بك في نظام Uchiha Dz ⚡\nاستخدم القائمة أدناه للبدء."
        bot.send_message(user_id, user_welcome, reply_markup=generate_main_reply_keyboard(user_id))

# --- [ 5. CALLBACK QUERY HANDLER: INTERACTIONS & DELETIONS ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callbacks(call):
    """معالجة جميع ضغطات الأزرار الشفافة (Inline Buttons)"""
    user_id = call.from_user.id
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    callback_data = call.data
    
    # 1. منطق عداد التفاعل (❤️)
    if callback_data == "ACTION_LIKE":
        stats_data = load_database_file("stats.json", {})
        interacted_list = stats_data.get("interacted", [])
        
        # منع التكرار: لا يمكن للمستخدم التفاعل أكثر من مرة لزيادة العداد
        if user_id not in interacted_list:
            stats_data["likes"] += 1
            stats_data.setdefault("interacted", []).append(user_id)
            save_database_file("stats.json", stats_data)
            
            # تحديث نص الأزرار في القناة فوراً لإظهار الرقم الجديد
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=generate_channel_markup())
            bot.answer_callback_query(call.id, "تم احتساب تفاعلك! ❤️ يمكنك الآن الاستلام من الزر الآخر.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "أنت متفاعل بالفعل يا وحش! 😈", show_alert=True)

    # 2. منطق حذف قنوات الاشتراك الإجباري (طلبك الأساسي)
    elif callback_data.startswith("REMOVE_SUB_"):
        index_to_remove = int(callback_data.split("_")[2])
        subs_list = load_database_file("subs.json", [])
        
        if index_to_remove < len(subs_list):
            removed_item = subs_list.pop(index_to_remove)
            save_database_file("subs.json", subs_list)
            bot.answer_callback_query(call.id, f"✅ تم حذف قناة: {removed_item['title']}")
            # مسح الرسالة لتنظيف الواجهة
            bot.delete_message(chat_id, message_id)

    # 3. أنواع الإذاعة
    elif callback_data.startswith("START_BC_"):
        GLOBAL_SESSIONS["broadcast_mode"] = callback_data
        prompt = bot.send_message(user_id, "📤 أرسل الآن محتوى الإذاعة (نص، صورة، فيديو، أو توجيه):")
        bot.register_next_step_handler(prompt, execute_broadcast_process)

# --- [ 6. ADMIN SYSTEM: CONTROL PANEL FUNCTIONS ] ---

@bot.message_handler(func=lambda m: True)
def handle_admin_commands(message):
    """الموجه الرئيسي لكل أوامر لوحة التحكم"""
    user_id = message.from_user.id
    text_input = message.text
    admin_list = load_database_file("admins.json", [DEVELOPER_ID])
    
    # حماية: الأدمن والمطور فقط من يمكنهم الوصول
    if user_id != DEVELOPER_ID and user_id not in admin_list:
        return

    # --- معالجة الأزرار ---
    if text_input == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(user_id, "🛠️ أهلاً بك في غرفة التحكم بالوحش:", reply_markup=generate_admin_reply_keyboard())

    elif text_input == "🔙 العودة":
        bot.send_message(user_id, "تمت العودة للقائمة السابقة.", reply_markup=generate_main_reply_keyboard(user_id))

    elif text_input == "نشر في القناة 📣":
        # تصميم رسالة النشر الفخمة
        publish_text = (f"┏━━━━━━━ ⚡ ━━━━━━━┓\n"
                        f"   🔥 **تحديث جديد من Uchiha Dz** 🔥\n"
                        f"┗━━━━━━━ ⚡ ━━━━━━━┛\n\n"
                        f"📢 تم رفع ملفات جديدة في القاعدة!\n\n"
                        f"⚠️ **ملاحظة:** لن تستطيع الاستلام إلا إذا تفاعلت مع هذا المنشور أولاً.\n\n"
                        f"👇 اضغط على الأزرار أدناه للاستلام:")
        bot.send_message(OFFICIAL_CHANNEL, publish_text, reply_markup=generate_channel_markup())
        bot.send_message(user_id, "✅ تم النشر بنجاح مع تفعيل العدادات الذكية.")

    elif text_input == "الإحصائيات 📊":
        stats_data = load_database_file("stats.json", {})
        with open("users.txt", "r") as f:
            total_users = len(f.readlines())
        
        report = (f"📊 **تقرير نظام Uchiha Dz:**\n\n"
                  f"👤 عدد أعضاء البوت: `{total_users}`\n"
                  f"❤️ إجمالي التفاعلات: `{stats_data['likes']}`\n"
                  f"📩 إجمالي الاستلامات: `{stats_data['receives']}`\n"
                  f"📂 عدد الملفات المرفوعة: `{len(load_database_file('bot_files.json', []))}`")
        bot.send_message(user_id, report, parse_mode="Markdown")

    elif text_input == "إضافة ملفات 📤":
        # تهيئة ذاكرة الرفع لهذا الأدمن
        GLOBAL_SESSIONS["upload_buffer"][user_id] = []
        upload_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).row("✅ إنهاء وحفظ", "❌ إلغاء العملية")
        bot.send_message(user_id, "📂 أرسل الملفات الآن (Documents).\nيمكنك إرسال ملفات متعددة، وعند الانتهاء اضغط حفظ.", reply_markup=upload_kb)
        bot.register_next_step_handler(message, process_multi_file_upload)

    elif text_input == "إدارة الاشتراك 🔗":
        subs_list = load_database_file("subs.json", [])
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, channel in enumerate(subs_list):
            markup.add(types.InlineKeyboardButton(f"🗑️ حذف: {channel['title']}", callback_data=f"REMOVE_SUB_{i}"))
        markup.add(types.InlineKeyboardButton("➕ إضافة قناة جديدة", callback_data="TRIGGER_ADD_SUB"))
        bot.send_message(user_id, "🔗 قائمة الاشتراك الإجباري الحالية:\nيمكنك حذف أي قناة بالضغط على زر الحذف بجانبها.", reply_markup=markup)

    elif text_input == "إذاعة متطورة 📡":
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("👥 مستخدمين البوت", callback_data="START_BC_USERS"),
                   types.InlineKeyboardButton("📢 القناة الرسمية", callback_data="START_BC_CHANNEL"))
        markup.add(types.InlineKeyboardButton("🌍 إذاعة شاملة (الكل)", callback_data="START_BC_ALL"))
        bot.send_message(user_id, "اختر الفئة المستهدفة للإذاعة:", reply_markup=markup)

    elif text_input == "تنظيف بيانات 🧹":
        # تصفير العدادات فقط دون مسح الملفات
        reset_stats = {"likes": 0, "receives": 0, "interacted": [], "received": []}
        save_database_file("stats.json", reset_stats)
        bot.send_message(user_id, "🧹 تم تنظيف الإحصائيات وتصفير العدادات بنجاح.")

    elif text_input == "تصفير ملفات 🗑️":
        # مسح قاعدة الملفات تماماً
        save_database_file("bot_files.json", [])
        bot.send_message(user_id, "🗑️ تم مسح جميع الملفات من قاعدة بيانات البوت.")

# --- [ 7. ADVANCED SUB-LOGIC: UPLOAD & BROADCAST ENGINES ] ---

def process_multi_file_upload(message):
    """محرك الرفع المتعدد الذي ينتظر أمر الحفظ النهائي"""
    user_id = message.from_user.id
    
    if message.text == "✅ إنهاء وحفظ":
        buffer = GLOBAL_SESSIONS["upload_buffer"].get(user_id, [])
        if buffer:
            main_files_db = load_database_file("bot_files.json", [])
            main_files_db.extend(buffer)
            save_database_file("bot_files.json", main_files_db)
            bot.send_message(user_id, f"✅ نجاح! تم حفظ {len(buffer)} ملفات في القاعدة.", reply_markup=generate_admin_reply_keyboard())
            GLOBAL_SESSIONS["upload_buffer"].pop(user_id)
        else:
            bot.send_message(user_id, "❌ لم تقم برفع أي ملفات لحفظها.", reply_markup=generate_admin_reply_keyboard())
        return
    
    elif message.text == "❌ إلغاء العملية":
        GLOBAL_SESSIONS["upload_buffer"].pop(user_id, None)
        bot.send_message(user_id, "🗑️ تم إلغاء عملية الرفع ومسح الذاكرة المؤقتة.", reply_markup=generate_admin_reply_keyboard())
        return

    # استلام الملفات وتخزينها في الـ Buffer
    if message.document:
        file_info = {
            "file_id": message.document.file_id,
            "caption": message.caption if message.caption else ""
        }
        GLOBAL_SESSIONS["upload_buffer"][user_id].append(file_info)
        count = len(GLOBAL_SESSIONS["upload_buffer"][user_id])
        bot.send_message(user_id, f"📥 تم استلام الملف رقم ({count}). أرسل المزيد أو اضغط حفظ.")
        bot.register_next_step_handler(message, process_multi_file_upload)
    else:
        bot.send_message(user_id, "⚠️ فضلاً أرسل (ملف/Document) فقط، أو اضغط حفظ.")
        bot.register_next_step_handler(message, process_multi_file_upload)

def execute_broadcast_process(message):
    """تنفيذ عملية الإذاعة بدقة لجميع المستخدمين"""
    mode = GLOBAL_SESSIONS.get("broadcast_mode")
    bot.send_message(message.chat.id, "🚀 جاري معالجة الإذاعة وإرسالها للجميع... انتظر قليلاً.")
    
    with open("users.txt", "r") as f:
        user_list = f.readlines()
    
    success_count = 0
    fail_count = 0
    
    for u_id in user_list:
        try:
            target_id = u_id.strip()
            # دعم جميع أنواع المحتوى في الإذاعة
            if message.content_type == 'text':
                bot.send_message(target_id, message.text)
            elif message.content_type == 'photo':
                bot.send_photo(target_id, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                bot.send_video(target_id, message.video.file_id, caption=message.caption)
            elif message.forward_from or message.forward_from_chat:
                bot.forward_message(target_id, message.chat.id, message.message_id)
            
            success_count += 1
            time.sleep(0.05) # تأخير بسيط لتجنب حظر التلجرام (Flood Wait)
        except:
            fail_count += 1
            continue
            
    summary = (f"✅ اكتملت الإذاعة!\n\n"
               f"👥 تم الإرسال لـ: `{success_count}`\n"
               f"❌ فشل الإرسال لـ: `{fail_count}`")
    bot.send_message(message.chat.id, summary, parse_mode="Markdown")

# --- [ 8. SYSTEM BOOTSTRAP ] ---
if __name__ == "__main__":
    # طباعة شعار البداية في الكونسول (ترمكس)
    print("=" * 40)
    print("😈 Uchiha Dz SUPREME SYSTEM IS ONLINE")
    print(f"📅 Started at: {datetime.datetime.now()}")
    print(f"🛠️ Developer: SELVA ZOLDEK")
    print("=" * 40)
    
    try:
        # تشغيل البوت بنظام infinity_polling لضمان عدم توقفه عند الأخطاء
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as fatal_error:
        print(f"🔥 FATAL ERROR: {fatal_error}")
        # إعادة التشغيل تلقائياً في حالة الانهيار
        os.execv(sys.executable, ['python'] + sys.argv)

