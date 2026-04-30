# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (ULTRA ARCHITECTURE) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 90.0.0 (NON-COMPRESSED & FULL DETAILED SOURCE)
# 🛡️ Features: Force Sub, Dynamic Perms, Advanced Broadcast, Multi-Upload
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

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=200)

# ذاكرة الجلسات المؤقتة (Runtime Memory)
SESSION = {
    "upload": {},          # ذاكرة الرفع المتعدد
    "bc_type": None,       # نوع الإذاعة
    "waiting_for": None,    # تتبع المدخلات القادمة
    "active_admin": None   # الأدمن الذي يتم تعديله حالياً
}

# --- [ 2. DATABASE MANAGEMENT ENGINE ] ---

def db_load(file, default):
    """تحميل البيانات من ملفات JSON مع ضمان الاستمرارية"""
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4, ensure_ascii=False)
        return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def db_save(file, data):
    """حفظ البيانات وتحديث الملفات فوراً"""
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False

# تهيئة قواعد البيانات عند الإقلاع
def bootstrap():
    db_load("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
    db_load("bot_files.json", [])
    db_load("subs.json", [])
    
    # تهيئة الأدمنية (المطور يملك كل شيء افتراضياً)
    dev_entry = {
        str(DEVELOPER_ID): {
            "name": "SELVA ZOLDEK",
            "perms": {
                "upload": True, "publish": True, "stats": True, 
                "clean": True, "reset": True, "broadcast": True
            }
        }
    }
    db_load("admins.json", dev_entry)
    
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()

bootstrap()

# --- [ 3. SECURITY & SUBSCRIPTION CHECK ] ---

def check_force_sub(user_id):
    """التأكد من أن المستخدم مشترك في كافة القنوات الإجبارية"""
    if user_id == DEVELOPER_ID: return True
    
    subs = db_load("subs.json", [])
    for sub in subs:
        link = sub['link']
        if link.startswith("@"):
            try:
                member = bot.get_chat_member(link, user_id)
                if member.status in ['left', 'kicked']:
                    return False
            except: continue
    return True

def check_permission(uid, perm_key):
    """فحص صلاحيات الأدمنية بشكل ديناميكي"""
    if uid == DEVELOPER_ID: return True
    admins = db_load("admins.json", {})
    if str(uid) in admins:
        return admins[str(uid)]["perms"].get(perm_key, False)
    return False

# --- [ 4. INTERFACE BUILDERS (GUI) ] ---

def get_subs_markup():
    """توليد أزرار الاشتراك الإجباري"""
    subs = db_load("subs.json", [])
    mk = types.InlineKeyboardMarkup(row_width=1)
    for s in subs:
        url = f"https://t.me/{s['link'].replace('@', '')}" if s['link'].startswith("@") else s['link']
        mk.add(types.InlineKeyboardButton(f"📢 اشترك: {s['title']}", url=url))
    mk.add(types.InlineKeyboardButton("✅ تم الاشتراك (اضغط للتحقق)", callback_data="VERIFY_SUBS"))
    return mk

def get_channel_kb():
    """توليد أزرار القناة مع العدادات الحية"""
    st = db_load("stats.json", {})
    mk = types.InlineKeyboardMarkup()
    mk.row(types.InlineKeyboardButton(f"تفاعل ❤️ ({st.get('likes', 0)})", callback_data="ACT_LIKE"),
           types.InlineKeyboardButton(f"استلم 📩 ({st.get('receives', 0)})", url=f"https://t.me/{bot.get_me().username}?start=verify"))
    return mk

def get_admin_main_kb(uid):
    """توليد لوحة تحكم الأدمن بناءً على صلاحياته المفعلة"""
    mk = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # الصلاحيات بالترتيب المطلوب
    if check_permission(uid, "upload"): mk.add("إضافة ملفات 📤")
    if check_permission(uid, "publish"): mk.add("نشر في القناة 📣")
    if check_permission(uid, "stats"): mk.add("الإحصائيات 📊")
    
    if uid == DEVELOPER_ID:
        # المطور يرى أدوات التنظيف والتصفير دوماً
        mk.row("تنظيف بيانات 🧹", "تصفير ملفات 🗑️")
    
    if check_permission(uid, "broadcast"): mk.add("إذاعة متطورة 📡")
    
    if uid == DEVELOPER_ID:
        mk.row("إدارة الاشتراك 🔗", "صلاحيات أدمن ⚙️")
        
    mk.add("🔙 العودة")
    return mk

# --- [ 5. CORE LOGIC: START & CALLBACKS ] ---

@bot.message_handler(commands=['start'])
def on_start(message):
    uid = message.from_user.id
    
    # الفحص الأول: الاشتراك الإجباري
    if not check_force_sub(uid):
        bot.send_message(uid, "⚠️ توقف! يجب الاشتراك في قنوات البوت أولاً لتتمكن من المتابعة.", reply_markup=get_subs_markup())
        return

    # تسجيل المستخدم
    with open("users.txt", "a+") as f:
        f.seek(0)
        if str(uid) not in f.read(): f.write(f"{uid}\n")

    # معالجة طلب الاستلام
    if "verify" in message.text:
        st = db_load("stats.json", {})
        if uid in st.get("interacted", []):
            if uid not in st.get("received", []):
                st["receives"] += 1
                st.setdefault("received", []).append(uid)
                db_save("stats.json", st)
            
            bot.send_message(uid, "✅ تم التحقق! استلم الملفات المرفوعة:")
            files = db_load("bot_files.json", [])
            for f in files: 
                try: bot.send_document(uid, f['id'], caption=f['cap'])
                except: pass
        else:
            bot.send_message(uid, f"⚠️ يجب التفاعل بـ (❤️) في القناة {OFFICIAL_CHANNEL} أولاً!")
        return

    welcome = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈" if uid == DEVELOPER_ID else "أهلاً بك في نظام Uchiha Dz ⚡"
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    admins = db_load("admins.json", {})
    if str(uid) in admins or uid == DEVELOPER_ID: mk.add("لوحة تحكم الأدمن 🛠️")
    else: mk.add("استلام الملفات 📥")
    bot.send_message(uid, welcome, reply_markup=mk)

@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    uid, mid, cid = call.from_user.id, call.message.message_id, call.message.chat.id
    data = call.data

    # 1. التفاعل والتحقق
    if data == "ACT_LIKE":
        st = db_load("stats.json", {})
        if uid not in st.get("interacted", []):
            st["likes"] += 1
            st.setdefault("interacted", []).append(uid)
            db_save("stats.json", st)
            bot.edit_message_reply_markup(cid, mid, reply_markup=get_channel_kb())
            bot.answer_callback_query(call.id, "شكراً لتفاعلك! ❤️")
        else: bot.answer_callback_query(call.id, "أنت متفاعل بالفعل! 😈")

    elif data == "VERIFY_SUBS":
        if check_force_sub(uid):
            bot.delete_message(uid, mid)
            bot.send_message(uid, "✅ تم التحقق بنجاح! أرسل /start الآن.")
        else: bot.answer_callback_query(call.id, "❌ لم تشترك في كل القنوات بعد!", show_alert=True)

    # 2. إدارة الصلاحيات (للمطور فقط)
    elif data.startswith("TOG_PERM_") and uid == DEVELOPER_ID:
        _, _, aid, pkey = data.split("_")
        admins = db_load("admins.json", {})
        if aid in admins:
            admins[aid]["perms"][pkey] = not admins[aid]["perms"].get(pkey, False)
            db_save("admins.json", admins)
            bot.edit_message_reply_markup(uid, mid, reply_markup=get_perms_keyboard(aid))

    # 3. إدارة الاشتراكات
    elif data == "ADD_SUB_ACTION" and uid == DEVELOPER_ID:
        msg = bot.send_message(uid, "🔗 أرسل (المعرف أو الرابط) ثم مسافة ثم (الاسم):")
        bot.register_next_step_handler(msg, add_sub_step)

    elif data.startswith("DEL_SUB_") and uid == DEVELOPER_ID:
        idx = int(data.split("_")[2])
        subs = db_load("subs.json", [])
        subs.pop(idx)
        db_save("subs.json", subs)
        bot.delete_message(uid, mid)

    # 4. إدارة الأدمنية
    elif data == "ADD_ADM_ACTION" and uid == DEVELOPER_ID:
        msg = bot.send_message(uid, "🆔 أرسل الـ ID الخاص بالأدمن الجديد:")
        bot.register_next_step_handler(msg, add_admin_step)

    elif data.startswith("VIEW_ADM_") and uid == DEVELOPER_ID:
        aid = data.split("_")[2]
        bot.send_message(uid, f"⚙️ صلاحيات الأدمن: `{aid}`", reply_markup=get_perms_keyboard(aid))

    # 5. خيارات الإذاعة
    elif data.startswith("BC_SET_"):
        SESSION["bc_type"] = data
        msg = bot.send_message(uid, "📤 أرسل الآن محتوى الإذاعة:")
        bot.register_next_step_handler(msg, run_broadcast)

# --- [ 6. ADMIN PANEL HANDLER ] ---

@bot.message_handler(func=lambda m: True)
def on_admin_panel(message):
    uid, txt = message.from_user.id, message.text
    if str(uid) not in db_load("admins.json", {}) and uid != DEVELOPER_ID: return

    if txt == "لوحة تحكم الأدمن 🛠️":
        bot.send_message(uid, "🛠️ غرفة التحكم:", reply_markup=get_admin_main_kb(uid))

    elif txt == "نشر في القناة 📣" and check_permission(uid, "publish"):
        bot.send_message(OFFICIAL_CHANNEL, "⚡ تحديث جديد من Uchiha Dz ⚡\nتفاعل للاستلام 👇", reply_markup=get_channel_kb())
        bot.send_message(uid, "✅ تم النشر.")

    elif txt == "إضافة ملفات 📤" and check_permission(uid, "upload"):
        SESSION["upload"][uid] = []
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True).row("✅ حفظ الكل", "❌ إلغاء")
        bot.send_message(uid, "📤 أرسل الملفات الآن، ثم اضغط حفظ.", reply_markup=kb)
        bot.register_next_step_handler(message, upload_engine)

    elif txt == "الإحصائيات 📊" and check_permission(uid, "stats"):
        st = db_load("stats.json", {})
        with open("users.txt", "r") as f: u = len(f.readlines())
        bot.send_message(uid, f"📊 التقرير:\n\n👥 مستخدمين: {u}\n❤️ تفاعل: {st['likes']}\n📩 استلام: {st['receives']}")

    elif txt == "إذاعة متطورة 📡" and check_permission(uid, "broadcast"):
        mk = types.InlineKeyboardMarkup()
        mk.row(types.InlineKeyboardButton("👥 مستخدمين", callback_data="BC_SET_USERS"),
               types.InlineKeyboardButton("📢 قناة", callback_data="BC_SET_CHAN"))
        mk.add(types.InlineKeyboardButton("🌍 جميع", callback_data="BC_SET_ALL"))
        bot.send_message(uid, "اختر نوع الإذاعة:", reply_markup=mk)

    # حصري للمطور
    if uid == DEVELOPER_ID:
        if txt == "صلاحيات أدمن ⚙️":
            admins = db_load("admins.json", {})
            mk = types.InlineKeyboardMarkup(row_width=1)
            for aid, d in admins.items():
                if int(aid) != DEVELOPER_ID:
                    mk.add(types.InlineKeyboardButton(f"⚙️ {d['name']} ({aid})", callback_data=f"VIEW_ADM_{aid}"))
            mk.add(types.InlineKeyboardButton("➕ إضافة أدمن جديد", callback_data="ADD_ADM_ACTION"))
            bot.send_message(uid, "⚙️ إدارة طاقم العمل:", reply_markup=mk)

        elif txt == "إدارة الاشتراك 🔗":
            subs = db_load("subs.json", [])
            mk = types.InlineKeyboardMarkup(row_width=1)
            for i, s in enumerate(subs):
                mk.add(types.InlineKeyboardButton(f"🗑️ حذف: {s['title']}", callback_data=f"DEL_SUB_{i}"))
            mk.add(types.InlineKeyboardButton("➕ إضافة اشتراك جديد", callback_data="ADD_SUB_ACTION"))
            bot.send_message(uid, "🔗 إدارة الاشتراكات:", reply_markup=mk)

        elif txt == "تنظيف بيانات 🧹":
            db_save("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
            bot.send_message(uid, "🧹 تم التنظيف.")

        elif txt == "تصفير ملفات 🗑️":
            db_save("bot_files.json", [])
            bot.send_message(uid, "🗑️ تم التصفير.")

    if txt == "🔙 العودة":
        bot.send_message(uid, "تمت العودة.", reply_markup=build_user_keyboard(uid))

# --- [ 7. HELPER FUNCTIONS: PERMS, SUBS, BROADCAST ] ---

def get_perms_keyboard(aid):
    """توليد كيبورد الصلاحيات (قفل/فتح)"""
    admins = db_load("admins.json", {})
    p = admins[str(aid)]["perms"]
    mk = types.InlineKeyboardMarkup(row_width=2)
    labels = {"upload":"إضافة ملف","publish":"نشر","stats":"إحصاء","clean":"تنظيف","reset":"تصفير","broadcast":"إذاعة"}
    for k, v in labels.items():
        status = "✅" if p.get(k) else "❌"
        mk.add(types.InlineKeyboardButton(f"{v}: {status}", callback_data=f"TOG_PERM_{aid}_{k}"))
    return mk

def add_admin_step(message):
    try:
        aid = str(message.text)
        admins = db_load("admins.json", {})
        admins[aid] = {"name": f"Admin_{aid[:5]}", "perms": {p:False for p in ["upload","publish","stats","clean","reset","broadcast"]}}
        db_save("admins.json", admins)
        bot.send_message(message.chat.id, "✅ تم الإضافة. عد للصلاحيات لتفعيلها.")
    except: bot.send_message(message.chat.id, "❌ خطأ.")

def add_sub_step(message):
    try:
        parts = message.text.split(" ", 1)
        subs = db_load("subs.json", [])
        subs.append({"link": parts[0], "title": parts[1]})
        db_save("subs.json", subs)
        bot.send_message(message.chat.id, "✅ تم إضافة الاشتراك.")
    except: bot.send_message(message.chat.id, "❌ خطأ تنسيق.")

def upload_engine(message):
    uid = message.from_user.id
    if message.text == "✅ حفظ الكل":
        db = db_load("bot_files.json", [])
        db.extend(SESSION["upload"].get(uid, []))
        db_save("bot_files.json", db)
        bot.send_message(uid, "✅ تم الحفظ.", reply_markup=get_admin_main_kb(uid))
        SESSION["upload"].pop(uid, None)
        return
    if message.document:
        SESSION["upload"][uid].append({"id": message.document.file_id, "cap": message.caption or ""})
        bot.send_message(uid, f"📥 استلمت ({len(SESSION['upload'][uid])}).")
        bot.register_next_step_handler(message, upload_engine)

def run_broadcast(message):
    bot.send_message(message.chat.id, "🚀 جاري الإذاعة...")
    with open("users.txt", "r") as f: users = f.readlines()
    for u in users:
        try: bot.copy_message(u.strip(), message.chat.id, message.message_id)
        except: continue
    bot.send_message(message.chat.id, "✅ اكتملت.")

# --- [ 8. SYSTEM BOOT ] ---
if __name__ == "__main__":
    print("😈 Uchiha Dz SUPREME SYSTEM IS ACTIVE")
    bot.infinity_polling()

