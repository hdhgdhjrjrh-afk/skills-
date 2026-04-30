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

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "subs.json", "settings.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f == "settings.json": json.dump({"notify": True}, file)
            elif f == "subs.json": json.dump([], file)
            elif f.endswith(".json"): json.dump({}, file)
            else: file.write("")

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)
    except: return [] if "subs" in filename else {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

# مخزن مؤقت لصلاحيات المشرفين أثناء التعديل
temp_admin_perms = {}

# ==========================================
# 2. لوحات التحكم (Keyboards)
# ==========================================

def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if user_id == OWNER_ID:
        btns = ["إضافة ملفات 📤", "نشر بالقناة 📣", "إدارة الإشتراك 📢", 
                "تفعيل اشعار دخول ✅", "ايقاف اشعار دخول ❌",
                "إذاعة للمشتركين 👥", "إدارة المشرفين 👮‍♂️", "الإحصائيات 📊", "حذف الملفات 🗑️", "إنهاء ✅"]
    else:
        admins = load_json("admins.json")
        perms = admins.get(str(user_id), [])
        btns = []
        if "إضافة" in perms: btns.append("إضافة ملفات 📤")
        if "نشر" in perms: btns.append("نشر بالقناة 📣")
        if "إذاعة" in perms: btns.append("إذاعة للمشتركين 👥")
        if "إحصائيات" in perms: btns.append("الإحصائيات 📊")
        if "حذف" in perms: btns.append("حذف الملفات 🗑️")
        btns.append("إنهاء ✅")
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def create_inline_keyboard(interact_count=0, receive_count=0, msg_id=""):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.row(
        types.InlineKeyboardButton(f"استلم 📩 ({receive_count})", url=f"https://t.me/{BOT_USERNAME}?start=get_{msg_id}"),
        types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f'interact_{msg_id}')
    )
    return keyboard

# لوحة صلاحيات المشرفين
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
    # تسجيل مستخدم جديد
    users = get_list("users.txt")
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(str(uid) + "\n")
        settings = load_json("settings.json")
        if settings.get("notify", True):
            try: bot.send_message(OWNER_ID, f"👤 مستخدم جديد دخل البوت:\nالاسم: {message.from_user.first_name}\nالأيدي: `{uid}`", parse_mode="Markdown")
            except: pass

    # استلام الملفات
    if "get_" in message.text:
        mid = message.text.split("_")[1]
        data = load_json("activity.json")
        if mid not in data or str(uid) not in data[mid].get("u_interact", []):
            bot.send_message(uid, "⚠️ تفاعل بـ ❤️ أولاً على المنشور في القناة!")
            return
        files = get_list("bot_files.txt")
        if files:
            bot.send_message(uid, "🚀 جاري إرسال الملفات...")
            for f_id in files:
                try: bot.send_document(uid, f_id)
                except: pass
            if str(uid) not in data[mid].get("u_receive", []):
                data[mid].setdefault("u_receive", []).append(str(uid))
                data[mid]["r"] = len(data[mid]["u_receive"])
                save_json("activity.json", data)
        return

    if uid == OWNER_ID:
        bot.send_message(uid, "مرحبا ايها مطور 😈SELVA ZOLDEK 😈مرحبا في نظام الوحش النظام جاهز للخدمة", reply_markup=get_panel(uid))
    else:
        bot.send_message(uid, f"أهلاً بك {message.from_user.first_name} في نظام الوحش ⚡", reply_markup=get_panel(uid))

# ==========================================
# 4. معالجة الأزرار والوظائف
# ==========================================

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    uid = message.from_user.id
    text = message.text
    admins = load_json("admins.json")
    perms = ["نشر", "إضافة", "إذاعة", "إحصائيات", "حذف", "إدارة", "إشتراك"] if uid == OWNER_ID else admins.get(str(uid), [])

    if text == "إدارة المشرفين 👮‍♂️" and uid == OWNER_ID:
        bot.send_message(uid, "🆔 أرسل ID المستخدم للتحكم بصلاحياته:")
        bot.register_next_step_handler(message, process_admin_id)

    elif text == "إدارة الإشتراك 📢" and uid == OWNER_ID:
        subs = load_json("subs.json")
        msg = f"📢 قنوات الاشتراك الحالية:\n" + ("\n".join(subs) if subs else "لا توجد قنوات.")
        msg += "\n\n— للإضافة: أرسل المعرف `@Uchiha75`\n— للحذف: أرسل `حذف @معرف`"
        bot.send_message(uid, msg)
        bot.register_next_step_handler(message, manage_subs)

    elif text == "إذاعة للمشتركين 👥" and "إذاعة" in perms:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("اذاعة مستخدمين", "اذاعة قناة", "اذاعة جميع", "إلغاء ❌")
        bot.send_message(uid, "اختر نوع الإذاعة:", reply_markup=markup)
        bot.register_next_step_handler(message, broadcast_type_select)

    elif text == "الإحصائيات 📊" and "إحصائيات" in perms:
        u, f = len(get_list("users.txt")), len(get_list("bot_files.txt"))
        bot.send_message(uid, f"📊 **الإحصائيات:**\n👤 مستخدمين: {u}\n📂 ملفات: {f}")

    elif text == "حذف الملفات 🗑️" and "حذف" in perms:
        open("bot_files.txt", "w").close()
        bot.send_message(uid, "🗑️ تم حذف جميع الملفات بنجاح.")

    elif text == "تفعيل اشعار دخول ✅" and uid == OWNER_ID:
        save_json("settings.json", {"notify": True})
        bot.send_message(uid, "✅ تم تفعيل إشعارات الدخول.")

    elif text == "ايقاف اشعار دخول ❌" and uid == OWNER_ID:
        save_json("settings.json", {"notify": False})
        bot.send_message(uid, "❌ تم إيقاف الإشعارات.")

    elif text == "إضافة ملفات 📤" and "إضافة" in perms:
        bot.send_message(uid, "📥 أرسل الملفات الآن واضغط إنهاء ✅", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, upload_files)

    elif text == "نشر بالقناة 📣" and "نشر" in perms:
        sent = bot.send_message(CHANNEL_ID, "🔄 جاري النشر...")
        mid, f_count = str(sent.message_id), len(get_list("bot_files.txt"))
        bot.edit_message_text(f"⚡ **تحديث جديد!**\n📂 الملفات: {f_count}\n❤️ تفاعل للاستلام.", CHANNEL_ID, sent.message_id, reply_markup=create_inline_keyboard(0,0,mid))
        bot.send_message(uid, "✅ تم النشر.")

# --- منطق الإذاعة ---
def broadcast_type_select(message):
    if message.text == "إلغاء ❌":
        bot.send_message(message.from_user.id, "تم الإلغاء.", reply_markup=get_panel(message.from_user.id))
        return
    bot.send_message(message.from_user.id, f"📣 أرسل رسالة الإذاعة لـ ({message.text}):")
    bot.register_next_step_handler(message, lambda m: run_broadcast(m, message.text))

def run_broadcast(message, b_type):
    users = get_list("users.txt")
    count = 0
    if b_type in ["اذاعة مستخدمين", "اذاعة جميع"]:
        for u in users:
            try: bot.copy_message(u, message.chat.id, message.message_id); count += 1; time.sleep(0.05)
            except: continue
    if b_type in ["اذاعة قناة", "اذاعة جميع"]:
        try: bot.copy_message(CHANNEL_ID, message.chat.id, message.message_id)
        except: pass
    bot.send_message(message.from_user.id, f"✅ تم الإرسال لـ {count} مستخدم.", reply_markup=get_panel(message.from_user.id))

# --- منطق الاشتراك ---
def manage_subs(message):
    text, subs = message.text.strip(), load_json("subs.json")
    if text.startswith("حذف "):
        target = text.replace("حذف ", "").strip()
        if target in subs: subs.remove(target); save_json("subs.json", subs); bot.send_message(OWNER_ID, f"✅ تم حذف {target}")
    elif text.startswith("@"):
        subs.append(text); save_json("subs.json", list(set(subs))); bot.send_message(OWNER_ID, f"✅ تمت إضافة {text}")
    bot.send_message(OWNER_ID, "العودة للرئيسية.", reply_markup=get_panel(OWNER_ID))

# --- منطق الأدمن ---
def process_admin_id(message):
    if not message.text.isdigit(): return
    temp_admin_perms[message.text] = load_json("admins.json").get(message.text, [])
    bot.send_message(OWNER_ID, f"⚙️ صلاحيات المشرف `{message.text}`:", reply_markup=create_perms_keyboard(message.text))

# --- منطق الرفع ---
def upload_files(message):
    if message.text == "إنهاء ✅": bot.send_message(message.from_user.id, "✅ تم الحفظ.", reply_markup=get_panel(message.from_user.id)); return
    fid = message.document.file_id if message.document else (message.photo[-1].file_id if message.photo else None)
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 تم الاستلام..")
    bot.register_next_step_handler(message, upload_files)

# ==========================================
# 5. Callback Handler (التفاعلات والصلاحيات)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    uid, data = call.from_user.id, call.data
    if data.startswith("tg_"): # تبديل صلاحية
        _, p, aid = data.split("_")
        if p in temp_admin_perms[aid]: temp_admin_perms[aid].remove(p)
        else: temp_admin_perms[aid].append(p)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_perms_keyboard(aid))
    elif data.startswith("sv_"): # حفظ صلاحية
        aid = data.split("_")[1]
        admins = load_json("admins.json")
        admins[aid] = temp_admin_perms.get(aid, [])
        save_json("admins.json", admins)
        bot.answer_callback_query(call.id, "✅ تم الحفظ")
        bot.edit_message_text(f"✅ تم تحديث صلاحيات المشرف `{aid}`", call.message.chat.id, call.message.message_id)
    elif data.startswith("interact_"): # تفاعل
        mid = data.split("_")[1]
        act = load_json("activity.json")
        if mid not in act: act[mid] = {"i": 0, "r": 0, "u_interact": [], "u_receive": []}
        if str(uid) not in act[mid]["u_interact"]:
            act[mid]["i"] += 1; act[mid]["u_interact"].append(str(uid)); save_json("activity.json", act)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_inline_keyboard(act[mid]["i"], act[mid]["r"], mid))
        else: bot.answer_callback_query(call.id, "⚠️ متفاعل بالفعل.", show_alert=True)

# التشغيل
print("😈 SYSTEM SELVA ZOLDEK IS ONLINE")
bot.infinity_polling()
