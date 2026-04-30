# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (MASTER ARCHITECTURE) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 50.0.0 (NON-COMPRESSED SOURCE)
# 🛡️ Optimized for: GitHub, Termux, and High-Performance Deployment
# =========================================================================

import telebot
from telebot import types
import os
import json
import time
import sys
import datetime

# --- [ 1. الأساسيات والتعريفات ] ---

# توكن البوت الخاص بك
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
# معرفك الخاص كمطور (تملك التحكم الكامل)
DEVELOPER_ID = 8611300267 
# القناة التي يتم النشر فيها
OFFICIAL_CHANNEL = "@Uchiha75"  

# إنشاء كائن البوت مع دعم تعدد الخيوط لضمان عدم التهنيج
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=100)

# ذاكرة تخزين الجلسات الحية (Runtime Sessions)
# نستخدمها لإدارة العمليات التي تتطلب خطوات متعددة مثل الرفع والإذاعة
LIVE_SESSIONS = {
    "upload_buffer": {},     # تخزين الملفات قبل حفظها نهائياً
    "admin_request": {},     # انتظار إرسال ID الأدمن الجديد
    "sub_request": {},       # انتظار إرسال بيانات قناة الاشتراك
    "broadcast_content": {},  # محتوى الإذاعة الجارية
    "broadcast_mode": None    # نوع الإذاعة (مستخدمين/قناة/الكل)
}

# --- [ 2. محرك إدارة البيانات الشامل ] ---

def get_data(file_name, default_value):
    """دالة قراءة البيانات: تضمن استرجاع البيانات حتى لو الملف غير موجود"""
    file_path = f"{file_name}"
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_value, f, indent=4, ensure_ascii=False)
        return default_value
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        return default_value

def set_data(file_name, data_to_save):
    """دالة حفظ البيانات: تضمن تخزين التغييرات فوراً بشكل آمن"""
    file_path = f"{file_name}"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {file_name}: {e}")
        return False

# تهيئة ملفات النظام لضمان عمل البوت بدون أخطاء "الملف غير موجود"
def initialize_database():
    """تجهيز ملفات JSON والقوائم عند تشغيل البوت لأول مرة"""
    get_data("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
    get_data("bot_files.json", [])
    get_data("subs.json", [])
    get_data("admins.json", [DEVELOPER_ID]) # المطور هو الأدمن الأول دائماً
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f: f.close()

initialize_database()

# --- [ 3. منشئ الواجهات والأزرار (GUI Builder) ] ---

def build_channel_markup():
    """توليد أزرار القناة مع العدادات التي تمنع التكرار وتحدث نفسها"""
    stats = get_data("stats.json", {})
    likes = stats.get("likes", 0)
    gets = stats.get("receives", 0)
    
    markup = types.InlineKeyboardMarkup()
    # زر التفاعل: يسجل ID المستخدم ويمنع تكراره
    btn_like = types.InlineKeyboardButton(f"تفاعل ❤️ ({likes})", callback_data="OP_LIKE")
    # زر الاستلام: رابط ذكي ينقل المستخدم للبوت للتحقق
    btn_get = types.InlineKeyboardButton(f"استلم 📩 ({gets})", url=f"https://t.me/{bot.get_me().username}?start=verify_access")
    
    markup.row(btn_like, btn_get)
    return markup

def build_admin_keyboard(uid):
    """توليد لوحة تحكم الأدمن بناءً على مستوى الصلاحية (مطور أو أدمن)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # الصلاحيات الممنوحة لكل من الأدمن والمطور
    markup.row("إضافة ملفات 📤", "نشر في القناة 📣")
    markup.row("إذاعة متطورة 📡", "الإحصائيات 📊")
    
    # الصلاحيات المحصورة بالمطور فقط (أنت SELVA ZOLDEK)
    if uid == DEVELOPER_ID:
        markup.row("تصفير ملفات 🗑️", "تنظيف بيانات 🧹")
        markup.row("إدارة الاشتراك 🔗", "صلاحيات أدمن ⚙️")
    
    markup.row("🔙 العودة")
    return markup

def build_main_keyboard(uid):
    """الكيبورد الافتراضي الذي يظهر عند كتابة /start"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    admins = get_data("admins.json", [DEVELOPER_ID])
    
    if uid == DEVELOPER_ID or uid in admins:
        markup.add(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"))
    else:
        markup.add(types.KeyboardButton("استلام الملفات 📥"))
    return markup

# --- [ 4. المنطق الرئيسي: الاستلام والتحقق ] ---

@bot.message_handler(commands=['start'])
def start_logic(message):
    uid = message.from_user.id
    first_name = message.from_user.first_name
    
    # تسجيل المستخدم في قاعدة البيانات العامة
    with open("users.txt", "a+") as f:
        f.seek(0)
        if str(uid) not in f.read():
            f.write(f"{uid}\n")

    # معالجة طلب الاستلام القادم من القناة
    if "verify_access" in message.text:
        stats = get_data("stats.json", {})
        interacted_users = stats.get("interacted", [])
        
        # الفحص الصارم: هل ضغط المستخدم على زر التفاعل في القناة؟
        if uid in interacted_users:
            received_users = stats.get("received", [])
            
            # تحديث عداد الاستلام إذا كانت هذه المرة الأولى
            if uid not in received_users:
                stats["receives"] += 1
                stats.setdefault("received", []).append(uid)
                set_data("stats.json", stats)
                # ملاحظة: سيتم تحديث العداد في القناة عند النشر القادم
            
            bot.send_message(uid, f"✅ أهلاً {first_name}! لقد تم التحقق من تفاعلك بنجاح. جاري إرسال الملفات...")
            
            files_db = get_data("bot_files.json", [])
            if not files_db:
                bot.send_message(uid, "📂 عذراً، لا توجد ملفات مرفوعة في قاعدة البيانات حالياً.")
            else:
                for file_entry in files_db:
                    try:
                        bot.send_document(uid, file_entry['id'], caption=file_entry['cap'])
                    except Exception as e:
                        print(f"Failed to send file: {e}")
        else:
            # رسالة في حالة عدم التفاعل
            bot.send_message(uid, f"⚠️ عذراً يا {first_name}، لن تستطيع الاستلام بدون تفاعل!\n\nعد للقناة {OFFICIAL_CHANNEL} واضغط على زر (تفاعل ❤️) أولاً.")
        return

    # رسالة الترحيب العادية
    if uid == DEVELOPER_ID:
        bot.send_message(uid, "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nأنت الآن في وضع التحكم المطلق.", reply_markup=build_main_keyboard(uid))
    else:
        bot.send_message(uid, "أهلاً بك في نظام Uchiha Dz ⚡\nالبوت جاهز لتسليمك الملفات بعد التفاعل في القناة.", reply_markup=build_main_keyboard(uid))

# --- [ 5. معالجة العمليات التفاعلية (Callbacks) ] ---

@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = call.from_user.id
    mid = call.message.message_id
    cid = call.message.chat.id
    data = call.data
    
    stats = get_data("stats.json", {})
    admins = get_data("admins.json", [DEVELOPER_ID])

    # 1. منطق عداد التفاعل في القناة
    if data == "OP_LIKE":
        interacted = stats.get("interacted", [])
        if uid not in interacted:
            stats["likes"] += 1
            stats.setdefault("interacted", []).append(uid)
            set_data("stats.json", stats)
            # تحديث الأزرار فوراً في القناة
            bot.edit_message_reply_markup(cid, mid, reply_markup=build_channel_markup())
            bot.answer_callback_query(call.id, "شكراً لتفاعلك! ❤️ يمكنك الآن التوجه للبوت لاستلام ملفاتك.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "لقد قمت بالتفاعل مسبقاً يا وحش! 😈", show_alert=True)

    # 2. إدارة الأدمنية (للمطور فقط)
    elif uid == DEVELOPER_ID:
        if data == "ADD_ADMIN_REQ":
            prompt = bot.send_message(uid, "🆔 من فضلك أرسل الـ ID الخاص بالأدمن الجديد:")
            bot.register_next_step_handler(prompt, process_add_admin)
            
        elif data.startswith("REM_ADM_"):
            target_id = int(data.split("_")[2])
            if target_id in admins:
                admins.remove(target_id)
                set_data("admins.json", admins)
                bot.answer_callback_query(call.id, "✅ تم سحب الصلاحيات بنجاح.")
                bot.delete_message(uid, mid)

        # 3. حذف قنوات الاشتراك الإجباري
        elif data.startswith("REM_SUB_"):
            sub_idx = int(data.split("_")[2])
            subs = get_data("subs.json", [])
            if sub_idx < len(subs):
                removed = subs.pop(sub_idx)
                set_data("subs.json", subs)
                bot.answer_callback_query(call.id, f"🗑️ تم حذف: {removed['title']}")
                bot.delete_message(uid, mid)

# --- [ 6. الموجه الإداري والصلاحيات ] ---

@bot.message_handler(func=lambda m: True)
def admin_router(message):
    uid = message.from_user.id
    txt = message.text
    admins = get_data("admins.json", [DEVELOPER_ID])
    
    # منع غير المصرح لهم من إكمال الكود
    if uid not in admins and uid != DEVELOPER_ID:
        return

    # --- القسم الأول: أوامر الأدمن والمطور ---
    if txt == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(uid, "🛠️ مرحباً بك في لوحة الإدارة الذكية:", reply_markup=build_admin_keyboard(uid))

    elif txt == "نشر في القناة 📣":
        publish_text = "┏━━━━━━━ ⚡ ━━━━━━━┓\n   🔥 **تحديث جديد من Uchiha Dz** 🔥\n┗━━━━━━━ ⚡ ━━━━━━━┛\n\nتفاعل للاستلام 👇"
        bot.send_message(OFFICIAL_CHANNEL, publish_text, reply_markup=build_channel_markup())
        bot.send_message(uid, "✅ تم النشر في القناة بنجاح.")

    elif txt == "إضافة ملفات 📤":
        LIVE_SESSIONS["upload_buffer"][uid] = []
        up_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).row("✅ إنهاء وحفظ", "❌ إلغاء")
        bot.send_message(uid, "📤 أرسل الملفات (Document) الآن، ثم اضغط إنهاء وحفظ.", reply_markup=up_kb)
        bot.register_next_step_handler(message, multi_upload_engine)

    elif txt == "الإحصائيات 📊":
        stats = get_data("stats.json", {})
        with open("users.txt", "r") as f:
            total_u = len(f.readlines())
        report = (f"📊 **إحصائيات نظام الوحش:**\n\n"
                  f"👥 المستخدمين: `{total_u}`\n"
                  f"❤️ التفاعلات: `{stats['likes']}`\n"
                  f"📩 الاستلامات: `{stats['receives']}`\n"
                  f"📂 الملفات: `{len(get_data('bot_files.json', []))}`")
        bot.send_message(uid, report, parse_mode="Markdown")

    elif txt == "إذاعة متطورة 📡":
        bc_kb = types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton("👥 للمستخدمين", callback_data="BC_USERS"),
            types.InlineKeyboardButton("🌍 للجميع", callback_data="BC_ALL")
        )
        bot.send_message(uid, "اختر نوع الإذاعة:", reply_markup=bc_kb)

    # --- القسم الثاني: أوامر المطور فقط (SELVA ZOLDEK) ---
    if uid == DEVELOPER_ID:
        if txt == "صلاحيات أدمن ⚙️":
            current_admins = get_data("admins.json", [DEVELOPER_ID])
            adm_kb = types.InlineKeyboardMarkup(row_width=1)
            for adm in current_admins:
                if adm != DEVELOPER_ID:
                    adm_kb.add(types.InlineKeyboardButton(f"🗑️ سحب صلاحية من: {adm}", callback_data=f"REM_ADM_{adm}"))
            adm_kb.add(types.InlineKeyboardButton("➕ إضافة أدمن جديد", callback_data="ADD_ADMIN_REQ"))
            bot.send_message(uid, "⚙️ إدارة طاقم الإشراف:", reply_markup=adm_kb)

        elif txt == "تنظيف بيانات 🧹":
            # تصفير العدادات
            set_data("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
            bot.send_message(uid, "🧹 تم تصفير جميع إحصائيات التفاعل والاستلام.")

        elif txt == "تصفير ملفات 🗑️":
            set_data("bot_files.json", [])
            bot.send_message(uid, "🗑️ تم حذف جميع الملفات من قاعدة البيانات.")

        elif txt == "إدارة الاشتراك 🔗":
            subs = get_data("subs.json", [])
            sub_kb = types.InlineKeyboardMarkup(row_width=1)
            for i, s in enumerate(subs):
                sub_kb.add(types.InlineKeyboardButton(f"🗑️ حذف: {s['title']}", callback_data=f"REM_SUB_{i}"))
            bot.send_message(uid, "🔗 إدارة الاشتراك الإجباري:", reply_markup=sub_kb)

    if txt == "🔙 العودة":
        bot.send_message(uid, "تمت العودة للقائمة الرئيسية.", reply_markup=build_main_keyboard(uid))

# --- [ 7. الأنظمة الفرعية: الرفع والإضافة ] ---

def process_add_admin(message):
    """حفظ ID الأدمن الجديد في قاعدة البيانات"""
    try:
        new_id = int(message.text)
        admins = get_data("admins.json", [DEVELOPER_ID])
        if new_id not in admins:
            admins.append(new_id)
            set_data("admins.json", admins)
            bot.send_message(message.chat.id, f"✅ تم تعيين {new_id} كأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "⚠️ هذا المستخدم موجود بالفعل في قائمة الأدمن.")
    except:
        bot.send_message(message.chat.id, "❌ خطأ: يرجى إرسال الـ ID بشكل صحيح (أرقام فقط).")

def multi_upload_engine(message):
    """محرك الرفع المتعدد الذي يجمع الملفات قبل الحفظ"""
    uid = message.from_user.id
    if message.text == "✅ إنهاء وحفظ":
        buffer = LIVE_SESSIONS["upload_buffer"].get(uid, [])
        if buffer:
            db_files = get_data("bot_files.json", [])
            db_files.extend(buffer)
            set_data("bot_files.json", db_files)
            bot.send_message(uid, f"✅ تم حفظ {len(buffer)} ملفات في قاعدة البيانات!", reply_markup=build_admin_keyboard(uid))
            LIVE_SESSIONS["upload_buffer"].pop(uid)
        else:
            bot.send_message(uid, "❌ لم يتم إرسال أي ملفات لحفظها.", reply_markup=build_admin_keyboard(uid))
        return
    elif message.text == "❌ إلغاء":
        LIVE_SESSIONS["upload_buffer"].pop(uid, None)
        bot.send_message(uid, "🗑️ تم إلغاء العملية ومسح الذاكرة المؤقتة.", reply_markup=build_admin_keyboard(uid))
        return

    if message.document:
        LIVE_SESSIONS["upload_buffer"][uid].append({"id": message.document.file_id, "cap": message.caption or ""})
        count = len(LIVE_SESSIONS["upload_buffer"][uid])
        bot.send_message(uid, f"📥 استلمت الملف رقم ({count}). تابع الإرسال أو اضغط حفظ.")
        bot.register_next_step_handler(message, multi_upload_engine)
    else:
        bot.send_message(uid, "⚠️ فضلاً أرسل ملفاً (Document) فقط.")
        bot.register_next_step_handler(message, multi_upload_engine)

# --- [ 8. بدء التشغيل الإمبراطوري ] ---
if __name__ == "__main__":
    print("=" * 45)
    print("😈 Uchiha Dz SUPREME ENGINE IS ACTIVE")
    print(f"🛠️ Master: SELVA ZOLDEK")
    print(f"🕒 Time: {datetime.datetime.now()}")
    print("=" * 45)
    
    try:
        # تشغيل البوت بنظام الاستجابة اللانهائية
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as fatal_error:
        print(f"🔥 FATAL CRASH: {fatal_error}")
        # محاولة إعادة التشغيل التلقائي في حالة الانهيار
        os.execv(sys.executable, ['python'] + sys.argv)
