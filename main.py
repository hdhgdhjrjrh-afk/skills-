import telebot
from telebot import types
import os, json, time, threading

# --- [ الإعدادات الأساسية ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# متغيرات الجلسة (لعدم ضياع البيانات)
pending_files = {}

# --- [ نظام إدارة قواعد البيانات - بدون اختصار ] ---
def setup_databases():
    """إنشاء كافة ملفات البيانات إذا كانت غير موجودة لضمان عدم حدوث كراش"""
    if not os.path.exists("users.txt"): open("users.txt", "w").close()
    
    files = {
        "bot_files.json": [],
        "admins.json": {},
        "stats.json": {
            "downloads": 0, 
            "likes": 0, 
            "likes_log": [], 
            "downloads_log": []
        },
        "settings.json": {
            "notifications": True, 
            "channel_id": "@Uchiha75", 
            "sub_link": "https://t.me/Uchiha75",
            "force_sub": True
        }
    }
    for filename, content in files.items():
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4, ensure_ascii=False)

setup_databases()

def get_data(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def check_permission(uid, perm_name):
    if int(uid) == OWNER_ID: return True
    admins = get_data("admins.json")
    return admins.get(str(uid), {}).get(perm_name, False)

# --- [ لوحات التحكم - تفصيلية جداً ] ---

def get_main_keyboard(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_data("settings.json")
    
    # أزرار الصلاحيات (للأدمن والمطور)
    if check_permission(uid, "can_add"): markup.insert("إضافة ملفات 📤")
    if check_permission(uid, "can_post"): markup.insert("نشر في القناة 📣")
    if check_permission(uid, "can_stats"): markup.insert("الإحصائيات 📊")
    
    # أزرار المطور الأساسي فقط
    if int(uid) == OWNER_ID:
        notif_btn = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
        markup.row("قسم الإذاعة 📢", "إضافة أدمن ➕")
        markup.row("صلاحيات أدمن ⚙️", "إضافة اشتراك 🔗")
        markup.row(notif_btn, "تنظيف البيانات 🧹")
        markup.row("تصفير الملفات 🗑️")
    
    return markup

def get_admin_perms_markup(admin_id):
    admins = get_data("admins.json")
    p = admins.get(str(admin_id), {
        "can_add": False, "can_post": False, 
        "can_stats": False, "can_clean": False, "can_reset": False
    })
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton(f"إضافة ملف: {'✅' if p.get('can_add') else '❌'}", callback_data=f"adm_add_{admin_id}"),
        types.InlineKeyboardButton(f"النشر: {'✅' if p.get('can_post') else '❌'}", callback_data=f"adm_post_{admin_id}"),
        types.InlineKeyboardButton(f"إحصائيات: {'✅' if p.get('can_stats') else '❌'}", callback_data=f"adm_stats_{admin_id}"),
        types.InlineKeyboardButton(f"تنظيف: {'✅' if p.get('can_clean') else '❌'}", callback_data=f"adm_clean_{admin_id}"),
        types.InlineKeyboardButton(f"تصفير: {'✅' if p.get('can_reset') else '❌'}", callback_data=f"adm_reset_{admin_id}"),
        types.InlineKeyboardButton("🗑️ حذف هذا الأدمن", callback_data=f"adm_del_{admin_id}"),
        types.InlineKeyboardButton("💾 حفظ النهائي", callback_data="adm_close")
    )
    return mk

def channel_post_markup():
    st = get_data("stats.json")
    try: bot_user = bot.get_me().username
    except: bot_user = "Bot"
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton(f"❤️ تفاعل | {st.get('likes', 0)}", callback_data="like_hit"),
        types.InlineKeyboardButton(f"📩 استلم | {st.get('downloads', 0)}", url=f"https://t.me/{bot_user}?start=get_files")
    )
    return mk

# --- [ معالجة البدء والإشعارات والاشتراك ] ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    conf = get_data("settings.json")
    
    # تسجيل المستخدم وإرسال الإشعار
    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        if conf.get("notifications"):
            try:
                msg = f"🔔 **مستخدم جديد انضم!**\n👤 الاسم: {message.from_user.first_name}\n🆔 الآيدي: `{uid}`"
                bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
            except: pass

    # معالجة رابط استلام الملفات
    if "get_files" in message.text:
        st = get_data("stats.json")
        if uid in st.get("likes_log", []):
            files = get_data("bot_files.json")
            if not files: return bot.send_message(uid, "❌ لا توجد ملفات حالياً.")
            bot.send_message(uid, "🚀 تم التحقق من تفاعلك.. جاري إرسال الملفات:")
            for f in files:
                try: bot.send_document(uid, f['file_id'], caption=f.get('caption', ""))
                except: continue
            # تحديث عداد المستلمين (لمرة واحدة فقط)
            if uid not in st.get("downloads_log", []):
                st["downloads"] += 1
                st["downloads_log"].append(uid)
                save_data("stats.json", st)
        else:
            bot.send_message(uid, "⚠️ عذراً! يجب عليك التفاعل بـ (❤️) في القناة أولاً.")
        return

    welcome_text = "مرحبا بك في نظام إدارة ⚡ Uchiha Dz ⚡"
    bot.send_message(uid, welcome_text, reply_markup=get_main_keyboard(uid))

# --- [ قسم العمليات - الراوتر الدقيق ] ---

@bot.message_handler(func=lambda m: True)
def router(message):
    uid, text = message.from_user.id, message.text
    conf = get_data("settings.json")

    # 1. إضافة اشتراك (إصلاح كامل)
    if text == "إضافة اشتراك 🔗" and uid == OWNER_ID:
        m = bot.send_message(uid, "🔗 أرسل رابط القناة الجديد (يجب أن يبدأ بـ https://t.me/):")
        bot.register_next_step_handler(m, process_new_sub)

    # 2. قسم الإذاعة (إصلاح كامل)
    elif text == "قسم الإذاعة 📢" and uid == OWNER_ID:
        m = bot.send_message(uid, "أرسل الرسالة التي تريد إذاعتها (نص، ميديا، ملف):")
        bot.register_next_step_handler(m, process_broadcast)

    # 3. تنظيف البيانات (إصلاح كامل)
    elif text == "تنظيف البيانات 🧹" and check_permission(uid, "can_clean"):
        new_stats = {"downloads": 0, "likes": 0, "likes_log": [], "downloads_log": []}
        save_data("stats.json", new_stats)
        bot.send_message(uid, "✅ تم تصفير سجلات التفاعل والعدادات بنجاح.")

    # 4. تفعيل/إيقاف الإشعارات
    elif text in ["تفعيل الإشعارات ✅", "إيقاف الإشعارات ❌"] and uid == OWNER_ID:
        conf["notifications"] = not conf.get("notifications", True)
        save_data("settings.json", conf)
        bot.send_message(uid, "⚙️ تم تحديث إعدادات الإشعارات.", reply_markup=get_main_keyboard(uid))

    # 5. صلاحيات الأدمن
    elif text == "صلاحيات أدمن ⚙️" and uid == OWNER_ID:
        admins = get_data("admins.json")
        if not admins: return bot.send_message(uid, "❌ لا يوجد أدمنية حالياً.")
        for aid in admins:
            bot.send_message(uid, f"👤 إعدادات الصلاحيات للأدمن: `{aid}`", reply_markup=get_admin_perms_markup(aid), parse_mode="Markdown")

    # 6. إضافة ملفات
    elif text == "إضافة ملفات 📤" and check_permission(uid, "can_add"):
        pending_files[uid] = []
        mk = types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء الحفظ ✅")
        bot.send_message(uid, "📤 أرسل الملفات الآن، ثم اضغط 'إنهاء الحفظ'.", reply_markup=mk)
        bot.register_next_step_handler(message, process_file_upload)

    # 7. نشر في القناة
    elif text == "نشر في القناة 📣" and check_permission(uid, "can_post"):
        all_files = get_data("bot_files.json")
        if not all_files: return bot.send_message(uid, "❌ قاعدة البيانات فارغة.")
        caption = f"⚡ **Uchiha Dz Update** ⚡\n\n📁 عدد الملفات: {len(all_files)}\n🚀 السرعة: فائقة جداً\n━━━━━━━━━━━━━━"
        bot.send_message(conf["channel_id"], caption, reply_markup=channel_post_markup(), parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر في القناة بنجاح.")

# --- [ دوال المعالجة المتقدمة ] ---

def process_new_sub(message):
    if "t.me/" in message.text:
        conf = get_data("settings.json")
        conf["sub_link"] = message.text
        try: conf["channel_id"] = "@" + message.text.split("t.me/")[1]
        except: pass
        save_data("settings.json", conf)
        bot.send_message(message.chat.id, "✅ تم حفظ رابط القناة والآيدي الجديد.")
    else: bot.send_message(message.chat.id, "❌ خطأ! الرابط غير صحيح.")

def process_broadcast(message):
    with open("users.txt", "r") as f: users = f.read().splitlines()
    bot.send_message(message.chat.id, f"🚀 بدأت الإذاعة لـ {len(users)} مستخدم...")
    count = 0
    for u in users:
        try:
            bot.copy_message(u, message.chat.id, message.message_id)
            count += 1
            time.sleep(0.05)
        except: continue
    bot.send_message(message.chat.id, f"✅ تم الانتهاء! استلم الرسالة {count} مستخدم.")

def process_file_upload(message):
    uid = message.from_user.id
    if message.text == "إنهاء الحفظ ✅":
        db = get_data("bot_files.json")
        db.extend(pending_files[uid])
        save_data("bot_files.json", db)
        bot.send_message(uid, f"✅ تم حفظ {len(pending_files[uid])} ملف بنجاح.", reply_markup=get_main_keyboard(uid))
        del pending_files[uid]; return

    fid = None
    if message.document: fid = message.document.file_id
    elif message.video: fid = message.video.file_id
    elif message.photo: fid = message.photo[-1].file_id

    if fid:
        pending_files.setdefault(uid, []).append({"file_id": fid, "caption": message.caption or ""})
        bot.send_message(uid, f"📥 تم استلام الملف رقم ({len(pending_files[uid])})...")
    
    bot.register_next_step_handler(message, process_file_upload)

# --- [ معالجة Callback - دقيقة جداً ] ---

@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid, data = call.from_user.id, call.data
    
    if data.startswith("adm_"):
        if uid != OWNER_ID: return
        admins = get_data("admins.json")
        parts = data.split("_") # adm_post_ID
        action, target = parts[1], parts[2]
        
        if action == "close": 
            bot.delete_message(call.message.chat.id, call.message.message_id)
        elif action == "del":
            if target in admins: del admins[target]
            save_data("admins.json", admins)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            p_map = {"add": "can_add", "post": "can_post", "stats": "can_stats", "clean": "can_clean", "reset": "can_reset"}
            p_key = p_map[action]
            admins[target][p_key] = not admins[target].get(p_key, False)
            save_data("admins.json", admins)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_admin_perms_markup(target))

    elif data == "like_hit":
        st = get_data("stats.json")
        if uid not in st.get("likes_log", []):
            st["likes"] += 1
            st.setdefault("likes_log", []).append(uid)
            save_data("stats.json", st)
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=channel_post_markup())
            except: pass
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
        else:
            bot.answer_callback_query(call.id, "⚠️ أنت متفاعل بالفعل!", show_alert=True)

# --- [ التشغيل النهائي مع حماية الاستمرارية ] ---
if __name__ == "__main__":
    print("🔥 SELVA ULTIMATE BOT IS STARTING...")
    while True:
        try:
            bot.infinity_polling(timeout=15, long_polling_timeout=5)
        except Exception as e:
            print(f"Connection lost, retrying... Error: {e}")
            time.sleep(5)

