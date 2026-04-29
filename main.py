import telebot
from telebot import types
import os
import json
import time
import threading

# ==========================================
# 1. الإعدادات الأساسية الجديدة
# ==========================================
TOKEN = "8665176617:AAFngE0bDW_aRpMP-9VIsGuWiSf2NCwqWl8" 
OWNER_ID = 8611300267  # معرفك كمالك
CHANNEL_ID = "@Uchiha75" # معرف القناة
BOT_USERNAME = "fountainsbot" # يوزر البوت بدون @

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود ملفات النظام
FILES = ["users.txt", "bot_files.txt", "activity.json", "admins.json", "subs.json"]
for f in FILES:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as file:
            if f.endswith(".json"): json.dump({} if f != "subs.json" else [], file)
            else: file.write("")

# --- دالات المساعدة ---
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return [] if "subs" in filename else {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_list(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def is_subscribed(user_id):
    subs = load_json("subs.json")
    for ch in subs:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status in ['left', 'kicked']: return False
        except: continue
    return True

# ==========================================
# 2. لوحات التحكم والصلاحيات
# ==========================================
def get_panel(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = []
    if user_id == OWNER_ID:
        btns = ["إضافة ملفات 📤", "نشر بالقناة 📣", "إدارة الإشتراك 📢", 
                "إذاعة للمشتركين 👥", "إدارة المشرفين 👮‍♂️", "الإحصائيات 📊", "حذف الملفات 🗑️", "إنهاء ✅"]
    else:
        admins = load_json("admins.json")
        perms = admins.get(str(user_id), [])
        if "نشر" in perms: btns.append("نشر بالقناة 📣")
        if "إضافة" in perms: btns.append("إضافة ملفات 📤")
        if "إذاعة" in perms: btns.append("إذاعة للمشتركين 👥")
        btns.append("الإحصائيات 📊")
        btns.append("إنهاء ✅")
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

def create_inline_keyboard(mid, interact_count=0, receive_count=0, is_channel=True):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if is_channel:
        # زر الاستلام يوجه المستخدم للبوت مع معرف الرسالة
        url = f"https://t.me/{BOT_USERNAME}?start=get_{mid}"
        keyboard.row(
            types.InlineKeyboardButton(f"استلم 📩 ({receive_count})", url=url),
            types.InlineKeyboardButton(f"تفاعل ❤️ ({interact_count})", callback_data=f'interact_{mid}')
        )
    return keyboard

# ==========================================
# 3. نظام إدارة المشرفين (تم الإصلاح)
# ==========================================
@bot.message_handler(func=lambda m: m.text == "إدارة المشرفين 👮‍♂️" and m.from_user.id == OWNER_ID)
def admin_manager(message):
    admins = load_json("admins.json")
    txt = "👮‍♂️ قائمة المشرفين:\n\n"
    for aid, perms in admins.items():
        txt += f"👤 `{aid}` - صلاحيات: {perms}\nحذف: /del_{aid}\n\n"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("إضافة مشرف ➕", "إلغاء ❌")
    bot.send_message(OWNER_ID, txt if admins else "لا يوجد مشرفين.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "إضافة مشرف ➕" and m.from_user.id == OWNER_ID)
def add_admin_step(message):
    msg = bot.send_message(OWNER_ID, "أرسل ID المشرف الجديد:")
    bot.register_next_step_handler(msg, save_admin_id)

def save_admin_id(message):
    if not message.text.isdigit():
        bot.send_message(OWNER_ID, "خطأ في الـ ID.")
        return
    new_id = message.text
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("نشر", callback_data=f"set_{new_id}_نشر"),
               types.InlineKeyboardButton("إضافة", callback_data=f"set_{new_id}_إضافة"))
    markup.row(types.InlineKeyboardButton("إذاعة", callback_data=f"set_{new_id}_إذاعة"),
               types.InlineKeyboardButton("كل الصلاحيات", callback_data=f"set_{new_id}_الكل"))
    bot.send_message(OWNER_ID, f"اختر صلاحيات لـ {new_id}:", reply_markup=markup)

# ==========================================
# 4. معالجة الأوامر والرسائل
# ==========================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    # حفظ المستخدم
    if str(uid) not in get_list("users.txt"):
        with open("users.txt", "a") as f: f.write(str(uid) + "\n")
    
    # فحص إذا كان قادماً من زر "استلم" في القناة
    if "get_" in message.text:
        mid = message.text.split("_")[1]
        data = load_json("activity.json")
        if str(uid) in data.get(mid, {}).get("u_interact", []):
            if is_subscribed(uid):
                files = get_list("bot_files.txt")
                for f in files: bot.send_document(uid, f)
                bot.send_message(uid, "✅ تم إرسال الملفات!")
            else:
                bot.send_message(uid, "⚠️ يجب الاشتراك في قنوات البوت أولاً!")
        else:
            bot.send_message(uid, "⚠️ يجب التفاعل بـ ❤️ على المنشور في القناة أولاً!")
        return

    bot.send_message(uid, "🛠️ أهلاً بك في لوحة التحكم:", reply_markup=get_panel(uid))

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    text = message.text
    admins = load_json("admins.json")
    perms = ["نشر", "إضافة", "إذاعة", "حذف"] if uid == OWNER_ID else admins.get(str(uid), [])

    if text == "نشر بالقناة 📣" and "نشر" in perms:
        f_count = len(get_list("bot_files.txt"))
        msg = bot.send_message(CHANNEL_ID, f"⚡ **تم تجديد الملفات!**\n\n📁 المتوفر: `{f_count}`\n⚠️ تفاعل بـ ❤️ ثم اضغط استلم.", parse_mode="Markdown")
        mid = str(msg.message_id)
        bot.edit_message_reply_markup(CHANNEL_ID, msg.message_id, reply_markup=create_inline_keyboard(mid))
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    elif text == "إضافة ملفات 📤" and "إضافة" in perms:
        bot.send_message(uid, "📥 أرسل الملفات الآن، ثم اضغط إنهاء ✅", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء ✅"))
        bot.register_next_step_handler(message, process_upload)

    elif text == "إذاعة للمشتركين 👥" and "إذاعة" in perms:
        m = bot.send_message(uid, "أرسل نص الإذاعة:")
        bot.register_next_step_handler(m, broadcast)

# ==========================================
# 5. معالجة الـ Callback (منع التكرار والإدارة)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid_str = str(call.from_user.id)
    
    # معالجة الصلاحيات
    if call.data.startswith("set_"):
        _, target_id, perm = call.data.split("_")
        admins = load_json("admins.json")
        if perm == "الكل": admins[target_id] = ["نشر", "إضافة", "إذاعة"]
        else: admins.setdefault(target_id, []).append(perm)
        save_json("admins.json", admins)
        bot.answer_callback_query(call.id, "✅ تم الحفظ")
        bot.edit_message_text(f"تم منح {target_id} صلاحية: {admins[target_id]}", call.message.chat.id, call.message.message_id)

    # معالجة التفاعل ❤️
    elif call.data.startswith("interact_"):
        mid = call.data.split("_")[1]
        data = load_json("activity.json")
        if mid not in data: data[mid] = {"i": 0, "u_interact": []}
        
        if uid_str not in data[mid]["u_interact"]:
            data[mid]["u_interact"].append(uid_str)
            data[mid]["i"] = len(data[mid]["u_interact"])
            save_json("activity.json", data)
            bot.answer_callback_query(call.id, "❤️ شكراً لتفاعلك!")
            bot.edit_message_reply_markup(CHANNEL_ID, int(mid), reply_markup=create_inline_keyboard(mid, data[mid]["i"]))
        else:
            bot.answer_callback_query(call.id, "⚠️ لقد تفاعلت مسبقاً!", show_alert=True)

# --- دالات الرفع والإذاعة ---
def process_upload(message):
    if message.text == "إنهاء ✅":
        bot.send_message(message.from_user.id, "تم حفظ الملفات.", reply_markup=get_panel(message.from_user.id))
        return
    fid = message.document.file_id if message.document else None
    if fid:
        with open("bot_files.txt", "a") as f: f.write(fid + "\n")
        bot.send_message(message.from_user.id, "📥 استلمت ملفاً..")
    bot.register_next_step_handler(message, process_upload)

def broadcast(message):
    users = get_list("users.txt")
    for u in users:
        try: bot.send_message(u, message.text)
        except: continue
    bot.send_message(OWNER_ID, "✅ اكتملت الإذاعة.")

bot.infinity_polling()
