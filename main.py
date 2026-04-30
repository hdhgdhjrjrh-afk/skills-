# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (ULTRA PRIVILEGES & SUBS) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 70.0.0 (NON-COMPRESSED & FULL DETAILED SOURCE)
# 🛡️ Designed for: GitHub, Termux, and Enterprise Management
# =========================================================================

import telebot
from telebot import types
import os
import json
import time
import sys
import datetime

# --- [ 1. CONFIGURATION & CONSTANTS ] ---

BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
DEVELOPER_ID = 8611300267 
OFFICIAL_CHANNEL = "@Uchiha75"  

# إنشاء كائن البوت مع دعم تعدد الخيوط للتعامل مع ضغط الإذاعة
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=150)

# ذاكرة الجلسات المؤقتة لإدارة تدفق العمليات (Runtime Buffer)
SESSION_DATA = {
    "upload": {},          # لتخزين الملفات أثناء الرفع المتعدد
    "bc_content": None,    # لتخزين محتوى الرسالة المراد إذاعتها
    "waiting_action": None, # تتبع الحالة (إضافة أدمن، إضافة قناة)
    "target_admin": None   # لتحديد أي أدمن نقوم بتعديل صلاحياته حالياً
}

# --- [ 2. DATABASE MANAGEMENT ENGINE ] ---

def database_load(file_path, default_structure):
    """محرك قراءة البيانات: يضمن استقرار البوت حتى في حالة فقدان الملفات"""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_structure, f, indent=4, ensure_ascii=False)
        return default_structure
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Critial DB Read Error ({file_path}): {e}")
        return default_structure

def database_save(file_path, data_to_write):
    """محرك حفظ البيانات: يقوم بتحديث ملفات JSON فوراً"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_write, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Critial DB Save Error ({file_path}): {e}")
        return False

# تهيئة ملفات النظام عند إقلاع البوت
def setup_initial_database():
    database_load("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
    database_load("bot_files.json", [])
    database_load("subs.json", []) # قائمة القنوات والروابط
    # تهيئة ملف الأدمنية مع صلاحيات المطور الكاملة
    admins_init = {
        str(DEVELOPER_ID): {
            "name": "SELVA ZOLDEK",
            "perms": {
                "upload": True, "publish": True, "stats": True, 
                "clean": True, "reset": True, "broadcast": True
            }
        }
    }
    database_load("admins.json", admins_init)
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()

setup_initial_database()

# --- [ 3. PERMISSIONS SYSTEM (SECURITY GATE) ] ---

def check_permission(user_id, permission_key):
    """فحص صلاحية محددة لأي أدمن؛ المطور يملك كل الصلاحيات دوماً"""
    if user_id == DEVELOPER_ID:
        return True
    
    admins_db = database_load("admins.json", {})
    uid_str = str(user_id)
    
    if uid_str in admins_db:
        # استرجاع قيمة الصلاحية من الملف (True أو False)
        return admins_db[uid_str]["perms"].get(permission_key, False)
    
    return False

# --- [ 4. DYNAMIC INTERFACE BUILDERS ] ---

def build_channel_buttons():
    """بناء أزرار القناة مع العدادات الحية المزامنة"""
    stats = database_load("stats.json", {})
    l_count = stats.get("likes", 0)
    r_count = stats.get("receives", 0)
    
    markup = types.InlineKeyboardMarkup()
    btn_like = types.InlineKeyboardButton(f"تفاعل ❤️ ({l_count})", callback_data="CHANNEL_LIKE")
    btn_get = types.InlineKeyboardButton(f"استلم 📩 ({r_count})", url=f"https://t.me/{bot.get_me().username}?start=verify_identity")
    
    markup.row(btn_like, btn_get)
    return markup

def build_admin_main_keyboard(user_id):
    """بناء كيبورد الأدمن بناءً على الصلاحيات التي منحها المطور"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # إضافة الأزرار فقط في حال كانت الصلاحية "مفعلة" للأدمن
    if check_permission(user_id, "upload"): markup.add("إضافة ملفات 📤")
    if check_permission(user_id, "publish"): markup.add("نشر في القناة 📣")
    if check_permission(user_id, "broadcast"): markup.add("إذاعة متطورة 📡")
    if check_permission(user_id, "stats"): markup.add("الإحصائيات 📊")
    
    # أزرار حصرية للمطور (الإدارة العليا)
    if user_id == DEVELOPER_ID:
        if check_permission(user_id, "clean"): markup.add("تنظيف بيانات 🧹")
        if check_permission(user_id, "reset"): markup.add("تصفير ملفات 🗑️")
        markup.row("إدارة الاشتراك 🔗", "صلاحيات أدمن ⚙️")
    
    markup.add("🔙 العودة للقائمة الرئيسية")
    return markup

def build_user_keyboard(user_id):
    """الكيبورد الذي يراه المستخدم العادي أو الأدمن عند البداية"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    admins_list = database_load("admins.json", {})
    
    if str(user_id) in admins_list or user_id == DEVELOPER_ID:
        markup.add(types.KeyboardButton("لوحة تحكم الأدمن 🛠️"))
    else:
        markup.add(types.KeyboardButton("استلام الملفات 📥"))
    return markup

# --- [ 5. START & VERIFICATION HANDLERS ] ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    name = message.from_user.first_name
    
    # تسجيل المستخدم في ملف الأرشيف
    with open("users.txt", "a+") as f:
        f.seek(0)
        if str(uid) not in f.read():
            f.write(f"{uid}\n")
    
    # فحص طلب الاستلام القادم من القناة
    if "verify_identity" in message.text:
        stats = database_load("stats.json", {})
        if uid in stats.get("interacted", []):
            if uid not in stats.get("received", []):
                stats["receives"] += 1
                stats.setdefault("received", []).append(uid)
                database_save("stats.json", stats)
            
            bot.send_message(uid, f"✅ تم التحقق من هويتك يا {name}! إليك ملفات الوحش:")
            files = database_load("bot_files.json", [])
            if not files:
                bot.send_message(uid, "📂 لا توجد ملفات في القاعدة حالياً.")
            else:
                for file_obj in files:
                    try: bot.send_document(uid, file_obj['id'], caption=file_obj['cap'])
                    except: pass
        else:
            bot.send_message(uid, f"⚠️ يا {name}، لن تستلم شيئاً بدون تفاعل!\n\nعد للقناة {OFFICIAL_CHANNEL} واضغط (تفاعل ❤️) أولاً.")
        return

    # الترحيب العادي
    txt = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈" if uid == DEVELOPER_ID else "أهلاً بك في نظام Uchiha Dz ⚡"
    bot.send_message(uid, txt, reply_markup=build_user_keyboard(uid))

# --- [ 6. CALLBACK ROUTING (LIKE, PERMS, SUBS) ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid, mid, data = call.from_user.id, call.message.message_id, call.data
    cid = call.message.chat.id
    
    # 1. التفاعل في القناة
    if data == "CHANNEL_LIKE":
        st = database_load("stats.json", {})
        if uid not in st.get("interacted", []):
            st["likes"] += 1
            st.setdefault("interacted", []).append(uid)
            database_save("stats.json", st)
            bot.edit_message_reply_markup(cid, mid, reply_markup=build_channel_buttons())
            bot.answer_callback_query(call.id, "شكراً لتفاعلك! ❤️ اذهب للبوت الآن للاستلام.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "متفاعل بالفعل يا وحش! 😈", show_alert=True)

    # 2. إدارة الصلاحيات (للمطور فقط)
    elif data.startswith("TOGGLE_PERM_") and uid == DEVELOPER_ID:
        # الهيكل: TOGGLE_PERM_[ADM_ID]_[PERMISSION_NAME]
        parts = data.split("_")
        adm_id, perm_key = parts[2], parts[3]
        admins = database_load("admins.json", {})
        
        if adm_id in admins:
            current_val = admins[adm_id]["perms"].get(perm_key, False)
            admins[adm_id]["perms"][perm_key] = not current_val
            database_save("admins.json", admins)
            bot.answer_callback_query(call.id, "✅ تم التحديث.")
            bot.edit_message_reply_markup(uid, mid, reply_markup=build_perms_keyboard(adm_id))

    # 3. حذف اشتراك أو رابط
    elif data.startswith("REMOVE_SUB_") and uid == DEVELOPER_ID:
        idx = int(data.split("_")[2])
        subs = database_load("subs.json", [])
        if idx < len(subs):
            subs.pop(idx)
            database_save("subs.json", subs)
            bot.answer_callback_query(call.id, "🗑️ تم الحذف بنجاح.")
            bot.delete_message(uid, mid)

    # 4. فتح واجهة تعديل الصلاحيات
    elif data.startswith("VIEW_ADMIN_") and uid == DEVELOPER_ID:
        target_id = data.split("_")[2]
        bot.send_message(uid, f"⚙️ تحكم في صلاحيات الأدمن: `{target_id}`", 
                         reply_markup=build_perms_keyboard(target_id), parse_mode="Markdown")

    # 5. أوامر الإضافة (أدمن/اشتراك)
    elif data == "TRIGGER_ADD_ADMIN" and uid == DEVELOPER_ID:
        msg = bot.send_message(uid, "🆔 أرسل الـ ID الخاص بالأدمن الجديد:")
        bot.register_next_step_handler(msg, process_new_admin_id)

    elif data == "TRIGGER_ADD_SUB" and uid == DEVELOPER_ID:
        msg = bot.send_message(uid, "🔗 أرسل (الرابط أو المعرف) ثم مسافة ثم (اسم القناة):\nمثال: @test قناة التجربة")
        bot.register_next_step_handler(msg, process_new_sub_data)

    # 6. اختيار نوع الإذاعة
    elif data.startswith("BC_MODE_"):
        SESSION_DATA["waiting_action"] = data
        bot.send_message(uid, "📤 أرسل الآن الرسالة المراد إذاعتها (نص، صورة، فيديو، توجيه):")
        bot.register_next_step_handler(call.message, process_broadcast_execution)

# --- [ 7. ADMIN PANEL & PRIVILEGE LOGIC ] ---

@bot.message_handler(func=lambda m: True)
def handle_admin_panel(message):
    uid, txt = message.from_user.id, message.text
    admins_db = database_load("admins.json", {})
    
    # منع الدخول لغير الأدمنية المسجلين
    if str(uid) not in admins_db and uid != DEVELOPER_ID:
        return

    # --- القائمة الرئيسية ---
    if txt == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(uid, "🛠️ أهلاً بك في غرفة التحكم بالوحش:", reply_markup=build_admin_main_keyboard(uid))

    # --- صلاحية: نشر في قناة ---
    elif txt == "نشر في القناة 📣" and check_permission(uid, "publish"):
        bot.send_message(OFFICIAL_CHANNEL, "⚡ **UCHIHA DZ - UPDATE**\n\nتفاعل للاستلام 👇", reply_markup=build_channel_buttons())
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    # --- صلاحية: إضافة ملفات ---
    elif txt == "إضافة ملفات 📤" and check_permission(uid, "upload"):
        SESSION_DATA["upload"][uid] = []
        up_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).row("✅ إنهاء وحفظ", "❌ إلغاء العملية")
        bot.send_message(uid, "📤 أرسل الملفات الآن، وعند الانتهاء اضغط حفظ.", reply_markup=up_kb)
        bot.register_next_step_handler(message, process_file_upload_step)

    # --- صلاحية: إحصائيات ---
    elif txt == "الإحصائيات 📊" and check_permission(uid, "stats"):
        st = database_load("stats.json", {})
        with open("users.txt", "r") as f: u_count = len(f.readlines())
        report = (f"📊 **تقرير النظام:**\n\n"
                  f"👥 المستخدمين: `{u_count}`\n"
                  f"❤️ التفاعلات: `{st['likes']}`\n"
                  f"📩 الاستلامات: `{st['receives']}`")
        bot.send_message(uid, report, parse_mode="Markdown")

    # --- صلاحية: إذاعة ---
    elif txt == "إذاعة متطورة 📡" and check_permission(uid, "broadcast"):
        bc_kb = types.InlineKeyboardMarkup()
        bc_kb.row(types.InlineKeyboardButton("👥 إذاعة مستخدمين", callback_data="BC_MODE_USERS"),
                  types.InlineKeyboardButton("📢 إذاعة قناة", callback_data="BC_MODE_CHAN"))
        bc_kb.add(types.InlineKeyboardButton("🌍 إذاعة جميع", callback_data="BC_MODE_ALL"))
        bot.send_message(uid, "اختر نوع الإذاعة المطلوبة:", reply_markup=bc_kb)

    # --- أوامر المطور الحصرية ---
    if uid == DEVELOPER_ID:
        if txt == "صلاحيات أدمن ⚙️":
            current_admins = database_load("admins.json", {})
            mk = types.InlineKeyboardMarkup(row_width=1)
            for aid, data in current_admins.items():
                if int(aid) != DEVELOPER_ID:
                    mk.add(types.InlineKeyboardButton(f"⚙️ {data['name']} ({aid})", callback_data=f"VIEW_ADMIN_{aid}"))
            mk.add(types.InlineKeyboardButton("➕ إضافة أدمن جديد", callback_data="TRIGGER_ADD_ADMIN"))
            bot.send_message(uid, "⚙️ التحكم في طاقم العمل وتوزيع الصلاحيات:", reply_markup=mk)

        elif txt == "إدارة الاشتراك 🔗":
            subs = database_load("subs.json", [])
            mk = types.InlineKeyboardMarkup(row_width=1)
            for i, s in enumerate(subs):
                mk.add(types.InlineKeyboardButton(f"🗑️ حذف: {s['title']}", callback_data=f"REMOVE_SUB_{i}"))
            mk.add(types.InlineKeyboardButton("➕ إضافة اشتراك/رابط", callback_data="TRIGGER_ADD_SUB"))
            bot.send_message(uid, "🔗 إدارة قائمة الاشتراكات والروابط الخارجية:", reply_markup=mk)

        elif txt == "تنظيف بيانات 🧹" and check_permission(uid, "clean"):
            database_save("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
            bot.send_message(uid, "🧹 تم تنظيف الإحصائيات وتصفير العدادات.")

        elif txt == "تصفير ملفات 🗑️" and check_permission(uid, "reset"):
            database_save("bot_files.json", [])
            bot.send_message(uid, "🗑️ تم تصفير قاعدة بيانات الملفات تماماً.")

    if txt == "🔙 العودة للقائمة الرئيسية":
        bot.send_message(uid, "تمت العودة.", reply_markup=build_user_keyboard(uid))

# --- [ 8. SUB-SYSTEM ENGINES (LOGIC) ] ---

def build_perms_keyboard(adm_id):
    """توليد كيبورد الصلاحيات للأدمن المختار (خاص بالمطور)"""
    admins = database_load("admins.json", {})
    perms = admins[str(adm_id)]["perms"]
    mk = types.InlineKeyboardMarkup(row_width=2)
    
    # خريطة الصلاحيات بالترتيب المطلوب
    p_map = {
        "upload": "إضافة ملف", 
        "publish": "نشر في قناة", 
        "stats": "إحصائيات", 
        "clean": "تنظيف بيانات", 
        "reset": "تصفير", 
        "broadcast": "إذاعة"
    }
    
    for key, label in p_map.items():
        status = "✅" if perms.get(key, False) else "❌"
        mk.add(types.InlineKeyboardButton(f"{label}: {status}", callback_data=f"TOGGLE_PERM_{adm_id}_{key}"))
    
    return mk

def process_new_admin_id(message):
    try:
        new_id = str(message.text)
        admins = database_load("admins.json", {})
        if new_id not in admins:
            # إضافة الأدمن الجديد بصلاحيات مغلقة افتراضياً
            admins[new_id] = {
                "name": f"Admin_{new_id[:5]}",
                "perms": {p: False for p in ["upload", "publish", "stats", "clean", "reset", "broadcast"]}
            }
            database_save("admins.json", admins)
            bot.send_message(message.chat.id, f"✅ تم إضافة {new_id}. اذهب لـ 'صلاحيات أدمن' لتفعيل ميزاته.")
        else:
            bot.send_message(message.chat.id, "⚠️ هذا المعرف مسجل كأدمن بالفعل.")
    except:
        bot.send_message(message.chat.id, "❌ خطأ في المعرف.")

def process_new_sub_data(message):
    try:
        data = message.text.split(" ", 1)
        link, title = data[0], data[1]
        subs = database_load("subs.json", [])
        subs.append({"link": link, "title": title})
        database_save("subs.json", subs)
        bot.send_message(message.chat.id, f"✅ تمت إضافة الاشتراك: {title}")
    except:
        bot.send_message(message.chat.id, "❌ خطأ: التنسيق يجب أن يكون (الرابط مسافة الاسم).")

def process_file_upload_step(message):
    uid = message.from_user.id
    if message.text == "✅ إنهاء وحفظ":
        buffer = SESSION_DATA["upload"].get(uid, [])
        if buffer:
            db_files = database_load("bot_files.json", [])
            db_files.extend(buffer)
            database_save("bot_files.json", db_files)
            bot.send_message(uid, f"✅ تم حفظ {len(buffer)} ملفات بنجاح!", reply_markup=build_admin_main_keyboard(uid))
            SESSION_DATA["upload"].pop(uid)
        else:
            bot.send_message(uid, "❌ لم ترفع أي شيء.", reply_markup=build_admin_main_keyboard(uid))
        return
    elif message.text == "❌ إلغاء العملية":
        SESSION_DATA["upload"].pop(uid, None)
        bot.send_message(uid, "🗑️ تم الإلغاء.", reply_markup=build_admin_main_keyboard(uid))
        return

    if message.document:
        SESSION_DATA["upload"][uid].append({"id": message.document.file_id, "cap": message.caption or ""})
        bot.send_message(uid, f"📥 استلمت الملف ({len(SESSION_DATA['upload'][uid])}). تابع أو احفظ.")
        bot.register_next_step_handler(message, process_file_upload_step)

def process_broadcast_execution(message):
    mode = SESSION_DATA["waiting_action"]
    bot.send_message(message.chat.id, "🚀 جاري معالجة الإذاعة... قد يستغرق هذا وقتاً حسب عدد المشتركين.")
    
    with open("users.txt", "r") as f:
        users = f.readlines()
    
    count = 0
    for user in users:
        try:
            u_id = user.strip()
            if message.content_type == 'text': bot.send_message(u_id, message.text)
            elif message.content_type == 'photo': bot.send_photo(u_id, message.photo[-1].file_id, caption=message.caption)
            elif message.document: bot.send_document(u_id, message.document.file_id, caption=message.caption)
            elif message.forward_from or message.forward_from_chat: bot.forward_message(u_id, message.chat.id, message.message_id)
            count += 1
            time.sleep(0.05)
        except: continue
    
    bot.send_message(message.chat.id, f"✅ اكتملت الإذاعة بنجاح لـ {count} مستخدم.")

# --- [ 9. RUNTIME ] ---
if __name__ == "__main__":
    print("-" * 30)
    print("😈 Uchiha Dz SUPREME SYSTEM IS ONLINE")
    print(f"🛠️ Master Architect: SELVA ZOLDEK")
    print("-" * 30)
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"CRASH: {e}")
        os.execv(sys.executable, ['python'] + sys.argv)

