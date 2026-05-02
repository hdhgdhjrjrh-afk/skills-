import telebot
from telebot import types
import os
import json
import time
import threading

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = "8401184550:AAGAuRsvepOLeJKftFp46MAm6qvofbXA5dU" 
OWNER_ID = 8611300267 
CHANNEL_ID = "@Uchiha75"
BOT_USERNAME = "gudurjbot"

# تحسين الأداء عبر تعدد المسارات
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=50)
file_lock = threading.Lock()

# التأكد من وجود ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "subs.json", "settings.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f == "subs.json": json.dump([], file)
            elif f == "settings.json": json.dump({"notify": True, "custom_caption": "⚡ **تحديث جديد!**\n📂 الملفات: {count}\n\n⚠️ تفاعل ❤️ ثم اضغط استلم."}, file)
            elif f.endswith(".json"): json.dump({}, file)
            else: file.write("")

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_json(filename):
    with file_lock:
        try:
            with open(filename, "r", encoding="utf-8") as f: return json.load(f)
        except: return [] if "subs" in filename else {}

def save_json(filename, data):
    with file_lock:
        with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

temp_admin_perms = {}

# ==========================================
# 2. لوحات التحكم (Keyboards)
# ==========================================

def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if user_id == OWNER_ID:
        btns = [
            "إضافة ملفات 📤", "نشر بالقناة 📣", "تخصيص بوست 📝",
            "إدارة الإشتراك 📢", "تفعيل اشعار دخول ✅", "ايقاف اشعار دخول ❌",
            "إذاعة للمشتركين 👥", "إدارة المشرفين 👮‍♂️", "الإحصائيات 📊", 
            "تصفير الإحصائيات ⚠️", "حذف الملفات 🗑️", "الدعم الفني 🛠️", 
            "معلومات البوت ℹ️", "إنهاء ✅"
        ]
    else:
        admins = load_json("admins.json")
        perms = admins.get(str(user_id), [])
        btns = []
        if "إضافة" in perms: btns.append("إضافة ملفات 📤")
        if "نشر" in perms: btns.append("نشر بالقناة 📣")
        if "إذاعة" in perms: btns.append("إذاعة للمشتركين 👥")
        if "إحصائيات" in perms: btns.append("الإحصائيات 📊")
        if "حذف" in perms: btns.append("حذف الملفات 🗑️")
        btns.extend(["الدعم الفني 🛠️", "معلومات البوت ℹ️", "إنهاء ✅"])
        
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def create_inline_keyboard(interact_count=0, receive_count=0, msg_id=""):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.row(
        types.InlineKeyboardButton(f"استلم 📩 ({receive_count})", url=f"https://t.me/{BOT_USERNAME}?start=get_{msg_id}"),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f'interact_{msg_id}')
    )
    return keyboard

def create_perms_keyboard(admin_id):
    perms = temp_admin_perms.get(str(admin_id), [])
    markup = types.InlineKeyboardMarkup(row_width=2)
    options = {"نشر": "نشر 📣", "إضافة": "إضافة 📤", "إذاعة": "إذاعة 👥", "إحصائيات": "إحصائيات 📊", "حذف": "حذف 🗑️"}
    btns = [types.InlineKeyboardButton(f"{label} {'✅' if key in perms else '❌'}", callback_data=f"tg_{key}_{admin_id}") for key, label in options.items()]
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("حفظ الصلاحيات 💾", callback_data=f"sv_{admin_id}"))
    return markup

# ==========================================
# 3. معالجة الأوامر والترحيب
# ==========================================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    users = get_list("users.txt")
    
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(str(uid) + "\n")
        settings = load_json("settings.json")
        if settings.get("notify", True):
            try: bot.send_message(OWNER_ID, f"👤 مستخدم جديد دخل البوت:\nالاسم: {message.from_user.first_name}\nالأيدي: `{uid}`")
            except: pass

    if "get_" in message.text:
        mid = message.text.split("_")[1]
        act_data = load_json("activity.json")
        
        if mid not in act_data or str(uid) not in act_data[mid].get("u_interact", []):
            bot.send_message(uid, "⚠️ عذراً يا وحش! يجب أن تضغط على زر التفاعل (❤️) تحت المنشور في القناة أولاً لتتمكن من استلام الملفات.")
            return
        
        files = get_list("bot_files.txt")
        if not files:
            bot.send_message(uid, "❌ لا توجد ملفات في النظام حالياً.")
            return

        bot.send_message(uid, "✅ تم التحقق من تفاعلك.. جاري إرسال الملفات:")
        for line in files:
            try: 
                fid, cap = line.split("|", 1) if "|" in line else (line, "بدون وصف")
                bot.send_document(uid, fid, caption=f"📄 **وصف الملف:**\n{cap}")
            except: pass
        
        if str(uid) not in act_data[mid].get("u_receive", []):
            act_data[mid].setdefault("u_receive", []).append(str(uid))
            act_data[mid]["r"] = len(act_data[mid]["u_receive"])
            save_json("activity.json", act_data)
            try: bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=create_inline_keyboard(act_data[mid]["i"], act_data[mid]["r"], mid))
            except: pass
        return

    # رسائل الترحيب المحدثة لنظام Ghost of Sparta
    if uid == OWNER_ID:
        bot.send_message(uid, "مرحبا ايها مطور 😈SELVA ZOLDEK 😈تم تشغيل نظام 💎Ghost of Sparta💎", reply_markup=get_panel(uid))
    else:
        bot.send_message(uid, "تم تشغيل نظام 💎Ghost of Sparta💎", reply_markup=get_panel(uid))

# ==========================================
# 4. معالجة الوظائف والأزرار
# ==========================================

@bot.message_handler(func=lambda m: True)
def handle_all_logic(message):
    uid, text = message.from_user.id, message.text
    admins = load_json("admins.json")
    perms = ["نشر", "إضافة", "إذاعة", "إحصائيات", "حذف", "إدارة", "إشتراك"] if uid == OWNER_ID else admins.get(str(uid), [])

    if text == "الإحصائيات 📊" and "إحصائيات" in perms:
        u, f = len(get_list("users.txt")), len(get_list("bot_files.txt"))
        act = load_json("activity.json")
        t_i = sum(v.get('i', 0) for v in act.values())
        t_r = sum(v.get('r', 0) for v in act.values())
        msg = f"📊 **إحصائيات Ghost of Sparta:**\n\n👥 المشتركين: {u}\n📂 الملفات: {f}\n❤️ التفاعلات: {t_i}\n📩 الاستلامات: {t_r}"
        bot.send_message(uid, msg)

    elif text == "تصفير الإحصائيات ⚠️" and uid == OWNER_ID:
        save_json("activity.json", {})
        bot.send_message(uid, "✅ تم مسح جميع بيانات الإحصائيات والتفاعلات القديمة بنجاح.")

    elif text == "تخصيص بوست 📝" and uid == OWNER_ID:
        bot.send_message(uid, "📝 أرسل الآن الوصف الجديد الذي سيظهر عند النشر (استخدم {count} لمكان عدد الملفات):")
        bot.register_next_step_handler(message, save_post_caption)

    elif text == "نشر بالقناة 📣" and "نشر" in perms:
        sent = bot.send_message(CHANNEL_ID, "🔄 جاري النشر...")
        mid, f_count = str(sent.message_id), len(get_list("bot_files.txt"))
        settings = load_json("settings.json")
        caption = settings.get("custom_caption", "").replace("{count}", str(f_count))
        bot.edit_message_text(caption, CHANNEL_ID, sent.message_id, reply_markup=create_inline_keyboard(0, 0, mid))
        bot.send_message(uid, "✅ تم النشر بالوصف المخصص.")

    elif text == "إدارة الإشتراك 📢" and uid == OWNER_ID:
        subs = load_json("subs.json")
        msg = "📢 قنوات الاشتراك:\n" + ("\n".join(subs) if subs else "لا توجد.")
        bot.send_message(uid, msg + "\n\nأرسل @المعرف للإضافة أو 'حذف @المعرف'")
        bot.register_next_step_handler(message, manage_subs_logic)

    elif text == "إذاعة للمشتركين 👥" and "إذاعة" in perms:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("اذاعة مستخدمين", "اذاعة قناة", "اذاعة جميع", "إنهاء ✅")
        bot.send_message(uid, "اختر نوع الإذاعة:", reply_markup=markup)
        bot.register_next_step_handler(message, broadcast_flow)

    elif text == "إدارة المشرفين 👮‍♂️" and uid == OWNER_ID:
        bot.send_message(uid, "🆔 أرسل ID المستخدم:")
        bot.register_next_step_handler(message, process_admin_id)

    elif text == "حذف الملفات 🗑️" and "حذف" in perms:
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم تصفير سجل الملفات.")

    elif text == "إضافة ملفات 📤" and "إضافة" in perms:
        bot.send_message(uid, "📥 أرسل الملفات الآن واضغط إنهاء ✅", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, upload_worker_with_cap)

    elif text in ["تفعيل اشعار دخول ✅", "ايقاف اشعار دخول ❌"] and uid == OWNER_ID:
        notify = "تفعيل" in text
        s = load_json("settings.json"); s["notify"] = notify; save_json("settings.json", s)
        bot.send_message(uid, f"✅ تم تحديث الإشعار.")

    elif text == "الدعم الفني 🛠️":
        bot.send_message(uid, "🛠️ للتواصل مع الدعم الفني: @Uchiha75")

    elif text == "معلومات البوت ℹ️":
        bot.send_message(uid, "ℹ️ نظام 💎Ghost of Sparta💎\nالمطور: SELVA ZOLDEK\nنظام إدارة قنوات متكامل.")

    elif text == "إنهاء ✅":
        bot.send_message(uid, "🏠 القائمة الرئيسية.", reply_markup=get_panel(uid))

# --- وظائف الإذاعة المصلحة ---
def broadcast_flow(message):
    uid = message.from_user.id
    b_type = message.text
    if b_type == "إنهاء ✅":
        bot.send_message(uid, "🏠 تم الإلغاء.", reply_markup=get_panel(uid))
        return
    if b_type in ["اذاعة مستخدمين", "اذاعة قناة", "اذاعة جميع"]:
        msg = bot.send_message(uid, f"📣 أرسل الآن الرسالة التي تريد إذاعتها لـ ({b_type}):")
        bot.register_next_step_handler(msg, lambda m: start_broadcast(m, b_type))

def start_broadcast(message, b_type):
    uid = message.from_user.id
    if message.text == "إنهاء ✅":
        bot.send_message(uid, "تم الإلغاء.", reply_markup=get_panel(uid))
        return
    
    users = get_list("users.txt")
    count = 0
    wait_msg = bot.send_message(uid, "⏳ جاري الإذاعة...")

    if b_type in ["اذاعة مستخدمين", "اذاعة جميع"]:
        for u_id in users:
            try:
                bot.copy_message(u_id, message.chat.id, message.message_id)
                count += 1
                time.sleep(0.05)
            except: continue

    if b_type in ["اذاعة قناة", "اذاعة جميع"]:
        try: bot.copy_message(CHANNEL_ID, message.chat.id, message.message_id)
        except: pass

    bot.delete_message(uid, wait_msg.message_id)
    bot.send_message(uid, f"✅ تمت الإذاعة لـ {count} مستخدم.", reply_markup=get_panel(uid))

# --- وظائف فرعية أخرى ---
def save_post_caption(message):
    if message.text == "إنهاء ✅": 
        bot.send_message(message.from_user.id, "🏠 العودة..", reply_markup=get_panel(message.from_user.id))
        return
    s = load_json("settings.json"); s["custom_caption"] = message.text; save_json("settings.json", s)
    bot.send_message(message.from_user.id, "✅ تم حفظ الوصف الجديد بنجاح.", reply_markup=get_panel(message.from_user.id))

def manage_subs_logic(message):
    t, subs = message.text.strip(), load_json("subs.json")
    if t.startswith("حذف "):
        target = t.replace("حذف ", "").strip()
        if target in subs: subs.remove(target); save_json("subs.json", subs)
    elif t.startswith("@"):
        subs.append(t); save_json("subs.json", list(set(subs)))
    bot.send_message(OWNER_ID, "🏠 العودة...", reply_markup=get_panel(OWNER_ID))

def process_admin_id(message):
    if not message.text.isdigit(): bot.send_message(OWNER_ID, "❌ أرسل ID صحيح."); return
    temp_admin_perms[message.text] = load_json("admins.json").get(message.text, [])
    bot.send_message(OWNER_ID, f"⚙️ صلاحيات `{message.text}`:", reply_markup=create_perms_keyboard(message.text))

def upload_worker_with_cap(message):
    if message.text == "إنهاء ✅": bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=get_panel(message.from_user.id)); return
    fid = message.document.file_id if message.document else (message.photo[-1].file_id if message.photo else None)
    if fid:
        bot.send_message(message.from_user.id, "📝 أرسل وصفاً لهذا الملف:")
        bot.register_next_step_handler(message, lambda m: finalize_upload_logic(m, fid))
    else: bot.register_next_step_handler(message, upload_worker_with_cap)

def finalize_upload_logic(message, fid):
    cap = message.text if message.text else "بدون وصف"
    with open("bot_files.txt", "a", encoding="utf-8") as f: f.write(f"{fid}|{cap}\n")
    bot.send_message(message.from_user.id, "📥 تم الاستلام.. أرسل غيره أو اضغط إنهاء.")
    bot.register_next_step_handler(message, upload_worker_with_cap)

# ==========================================
# 5. معالجة الضغطات (Callbacks)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid, data = call.from_user.id, call.data
    if data.startswith("tg_"):
        _, p, aid = data.split("_")
        if p in temp_admin_perms.get(aid, []): temp_admin_perms[aid].remove(p)
        else: temp_admin_perms.setdefault(aid, []).append(p)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_perms_keyboard(aid))
    elif data.startswith("sv_"):
        aid = data.split("_")[1]
        admins = load_json("admins.json"); admins[aid] = temp_admin_perms.get(aid, []); save_json("admins.json", admins)
        bot.edit_message_text(f"✅ تم تحديث صلاحيات المشرف `{aid}`", call.message.chat.id, call.message.message_id)
    elif data.startswith("interact_"):
        mid = data.split("_")[1]; act = load_json("activity.json")
        if mid not in act: act[mid] = {"i": 0, "r": 0, "u_interact": [], "u_receive": []}
        if str(uid) not in act[mid]["u_interact"]:
            act[mid]["i"] += 1; act[mid]["u_interact"].append(str(uid)); save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            try: bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=create_inline_keyboard(act[mid]["i"], act[mid]["r"], mid))
            except: pass
        else: bot.answer_callback_query(call.id, "⚠️ تفاعلت مسبقاً.", show_alert=True)

print("😈 Ghost of Sparta SYSTEM IS ONLINE - OWNER: SELVA ZOLDEK")
bot.infinity_polling()

