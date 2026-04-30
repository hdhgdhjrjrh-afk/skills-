# =========================================================================
# ⚡ Uchiha Dz - THE FINAL MONSTER SYSTEM ⚡
# 🛠️ Master Architect: SELVA ZOLDEK
# 🆔 Developer ID: 8611300267
# 🔄 Version: 13.0.0 (COMPLETE OMNI-EDITION)
# =========================================================================

import telebot
from telebot import types
import os
import json
import time
import datetime
import sys

# --- [ 1. CONFIGURATION ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=50)

# ذاكرة الجلسة المؤقتة (لمنع الحفظ التلقائي للملفات)
FILE_BUFFER = {}

# --- [ 2. DATABASE ENGINE ] ---
def db_op(action, file_name, data=None):
    try:
        if action == "read":
            if not os.path.exists(file_name):
                return [] if "json" in file_name else {}
            with open(file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        elif action == "write":
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
    except: return [] if action == "read" else False

def init_system():
    schema = {
        "users.txt": "", "bot_files.json": "[]", "admins.json": "{}",
        "subs.json": "[]", "settings.json": json.dumps({"channel_id": "@Uchiha75"}),
        "stats.json": json.dumps({"likes": 0, "receives": 0, "interacted_users": [], "received_users": []})
    }
    for f, c in schema.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file: file.write(c)

init_system()

# --- [ 3. PERMISSIONS ] ---
def is_dev(uid): return int(uid) == OWNER_ID
def has_perm(uid, key):
    if is_dev(uid): return True
    admins = db_op("read", "admins.json")
    return admins.get(str(uid), {}).get(key, False)

# --- [ 4. KEYBOARDS ] ---
def main_markup(uid):
    mk = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if is_dev(uid) or str(uid) in db_op("read", "admins.json"):
        mk.row("لوحة تحكم الأدمن 🛠️")
    mk.row("استلام الملفات 📥")
    return mk

def admin_markup(uid):
    mk = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = ["إضافة ملفات 📤", "نشر في القناة 📣", "إذاعة متطورة 📡", "الإحصائيات 📊", "تصفير ملفات 🗑️", "تنظيف بيانات 🧹"]
    mk.add(*[types.KeyboardButton(b) for b in btns])
    if is_dev(uid): mk.row("إدارة الاشتراك 🔗", "صلاحيات أدمن ⚙️")
    mk.row("🔙 العودة")
    return mk

def session_markup():
    mk = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    mk.add("✅ إنهاء وحفظ الكل", "❌ إلغاء الحفظ")
    return mk

# --- [ 5. START & ROUTING ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.from_user.id
    with open("users.txt", "a+", encoding="utf-8") as f:
        f.seek(0)
        if str(uid) not in f.read(): f.write(f"{uid}\n")
        
    if is_dev(uid):
        bot.send_message(uid, "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة ايها مطور", reply_markup=main_markup(uid))
    else:
        bot.send_message(uid, "أهلاً بك في نظام Uchiha Dz ⚡", reply_markup=main_markup(uid))

@bot.message_handler(func=lambda m: True)
def router(message):
    uid, txt = message.from_user.id, message.text

    if txt == "لوحة تحكم الأدمن 🛠️" and (is_dev(uid) or str(uid) in db_op("read", "admins.json")):
        bot.send_message(uid, "🛠️ لوحة تحكم الوحش:", reply_markup=admin_markup(uid))

    elif txt == "🔙 العودة":
        bot.send_message(uid, "تم العودة للقائمة الرئيسية.", reply_markup=main_markup(uid))

    elif txt == "الإحصائيات 📊" and has_perm(uid, "stats"):
        st = db_op("read", "stats.json")
        u_count = len(open("users.txt").readlines()) if os.path.exists("users.txt") else 0
        msg = (f"📊 **إحصائيات الوحش:**\n\n👤 المستخدمين: `{u_count}`\n❤️ المتفاعلين: `{st.get('likes', 0)}`"
               f"\n📥 المستلمين: `{st.get('receives', 0)}` \n📂 الملفات: `{len(db_op('read', 'bot_files.json'))}`")
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif txt == "إذاعة متطورة 📡" and has_perm(uid, "broadcast"):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("📝 نص", callback_data="bc_text"),
               types.InlineKeyboardButton("🖼️ صورة", callback_data="bc_photo"),
               types.InlineKeyboardButton("🔄 توجيه", callback_data="bc_fwd"))
        bot.send_message(uid, "اختر نوع الإذاعة:", reply_markup=mk)

    elif txt == "تصفير ملفات 🗑️" and has_perm(uid, "reset"):
        db_op("write", "bot_files.json", [])
        bot.send_message(uid, "✅ تم تصفير القاعدة.")

    elif txt == "تنظيف بيانات 🧹" and has_perm(uid, "clean"):
        st = db_op("read", "stats.json")
        st.update({"likes": 0, "receives": 0, "interacted_users": [], "received_users": []})
        db_op("write", "stats.json", st)
        bot.send_message(uid, "🧹 تم تنظيف العدادات.")

    elif txt == "نشر في القناة 📣" and has_perm(uid, "post"):
        send_monster_post(uid)

    elif txt == "إدارة الاشتراك 🔗" and is_dev(uid):
        manage_subs(uid)

    elif txt == "إضافة ملفات 📤" and has_perm(uid, "upload"):
        FILE_BUFFER[uid] = []
        bot.send_message(uid, "📤 أرسل الملفات الآن.\nلن يتم حفظها حتى تضغط (إنهاء وحفظ).", reply_markup=session_markup())
        bot.register_next_step_handler(message, collect_files)

    elif txt == "✅ إنهاء وحفظ الكل":
        commit_files(uid)

    elif txt == "❌ إلغاء الحفظ":
        FILE_BUFFER.pop(uid, None)
        bot.send_message(uid, "🗑️ تم إلغاء الرفع.", reply_markup=admin_markup(uid))

# --- [ 6. FILE COLLECTION LOGIC ] ---
def collect_files(message):
    uid = message.from_user.id
    if message.text in ["✅ إنهاء وحفظ الكل", "❌ إلغاء الحفظ"]:
        router(message)
        return
    if message.content_type == 'document':
        if uid not in FILE_BUFFER: FILE_BUFFER[uid] = []
        FILE_BUFFER[uid].append({"file_id": message.document.file_id, "cap": message.caption})
        bot.send_message(uid, f"📥 تم استلام ({len(FILE_BUFFER[uid])}). تابع الإرسال أو احفظ.", reply_markup=session_markup())
        bot.register_next_step_handler(message, collect_files)
    else:
        bot.send_message(uid, "⚠️ أرسل ملفاً فقط!")
        bot.register_next_step_handler(message, collect_files)

def commit_files(uid):
    if uid in FILE_BUFFER and FILE_BUFFER[uid]:
        files = db_op("read", "bot_files.json")
        files.extend(FILE_BUFFER[uid])
        db_op("write", "bot_files.json", files)
        count = len(FILE_BUFFER[uid])
        FILE_BUFFER.pop(uid)
        bot.send_message(uid, f"✅ تم تثبيت {count} ملفات بنجاح!", reply_markup=admin_markup(uid))
    else: bot.send_message(uid, "❌ الذاكرة فارغة.")

# --- [ 7. BROADCAST & POSTING ] ---
def send_monster_post(uid):
    c = db_op("read", "settings.json")
    msg = ("┏━━━━━━━ ⚡ ━━━━━━━┓\n   ⚡ **UCHIHA DZ UPDATE** ⚡\n┗━━━━━━━ ⚡ ━━━━━━━┛\n\n"
           "🔥 **تفاعل**\n📥 **استلام**\n      🚀 **سرعة**\n      💪 **قوة**\n      ⏳ **مدة طويلة**\n\n"
           "⚠️ **سارع قبل انتهاء مدة!**\n\n━━━━━━━━━━━━━━━━━━━━")
    mk = types.InlineKeyboardMarkup()
    mk.row(types.InlineKeyboardButton("تفاعل ❤️", callback_data="L_post"),
           types.InlineKeyboardButton("استلام 📥", callback_data="D_post"))
    bot.send_message(c["channel_id"], msg, reply_markup=mk, parse_mode="Markdown")
    bot.send_message(uid, "✅ تم النشر.")

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid, data = call.from_user.id, call.data
    st = db_op("read", "stats.json")
    if data == "L_post":
        if uid not in st.get("interacted_users", []):
            st["likes"] += 1; st.setdefault("interacted_users", []).append(uid); db_op("write", "stats.json", st)
            bot.answer_callback_query(call.id, "تم تسجيل التفاعل! ❤️", show_alert=True)
        else: bot.answer_callback_query(call.id, "متفاعل بالفعل!")
    elif data == "D_post":
        if uid in st.get("interacted_users", []):
            if uid not in st.get("received_users", []):
                st["receives"] += 1; st.setdefault("received_users", []).append(uid); db_op("write", "stats.json", st)
            bot.answer_callback_query(call.id, "🚀 جاري الاستلام...")
            for f in db_op("read", "bot_files.json"): bot.send_document(uid, f['file_id'], caption=f['cap'])
        else: bot.answer_callback_query(call.id, "⚠️ يجب التفاعل ❤️ أولاً!", show_alert=True)
    elif data == "bc_text": bot.register_next_step_handler(bot.send_message(uid, "نص الإذاعة:"), run_bc, "text")
    elif data == "bc_photo": bot.register_next_step_handler(bot.send_message(uid, "الصورة:"), run_bc, "photo")
    elif data == "bc_fwd": bot.register_next_step_handler(bot.send_message(uid, "وجه الرسالة:"), run_bc, "fwd")
    elif data == "add_sub": bot.register_next_step_handler(bot.send_message(uid, "يوزر واسم:"), save_sub)
    elif data.startswith("del_"):
        subs = db_op("read", "subs.json"); subs.pop(int(data.split("_")[1])); db_op("write", "subs.json", subs)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=refresh_subs(subs))

def run_bc(message, mode):
    users = open("users.txt").readlines()
    for u in users:
        try:
            u = u.strip()
            if mode == "text": bot.send_message(u, message.text)
            elif mode == "photo": bot.send_photo(u, message.photo[-1].file_id, caption=message.caption)
            elif mode == "fwd": bot.forward_message(u, message.chat.id, message.message_id)
        except: continue
    bot.send_message(message.chat.id, "✅ تم.")

def manage_subs(uid):
    subs = db_op("read", "subs.json")
    mk = types.InlineKeyboardMarkup(row_width=1)
    for i, s in enumerate(subs): mk.add(types.InlineKeyboardButton(f"❌ حذف: {s['title']}", callback_data=f"del_{i}"))
    mk.add(types.InlineKeyboardButton("➕ إضافة", callback_data="add_sub"))
    bot.send_message(uid, "🔗 القنوات:", reply_markup=mk)

def save_sub(message):
    try:
        p = message.text.split(" ", 1)
        subs = db_op("read", "subs.json")
        subs.append({"chat_id": p[0], "title": p[1], "url": f"https://t.me/{p[0][1:]}"})
        db_op("write", "subs.json", subs); bot.send_message(message.chat.id, "✅")
    except: bot.send_message(message.chat.id, "❌")

def refresh_subs(subs):
    mk = types.InlineKeyboardMarkup(row_width=1)
    for i, s in enumerate(subs): mk.add(types.InlineKeyboardButton(f"❌ حذف: {s['title']}", callback_data=f"del_{i}"))
    mk.add(types.InlineKeyboardButton("➕ إضافة", callback_data="add_sub"))
    return mk

# --- [ 8. RUN ] ---
if __name__ == "__main__":
    print("😈 THE MONSTER IS FULLY COMPLETE!")
    bot.infinity_polling()

