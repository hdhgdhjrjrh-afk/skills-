import telebot
from telebot import types
import os, json, time

# --- [ الإعدادات الأساسية ] ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)
BOT_USERNAME = bot.get_me().username

# ذاكرة الجلسات المؤقتة
pending_files = {}

# --- [ نظام إدارة قاعدة البيانات الشامل ] ---
def init_db():
    database = {
        "users.txt": "", 
        "bot_files.json": "[]", 
        "admins.json": "{}", 
        "stats.json": json.dumps({
            "downloads": 0, 
            "likes": 0, 
            "likes_log": [], 
            "downloads_log": []
        }),
        "settings.json": json.dumps({
            "notifications": True, 
            "channel_id": "@Uchiha75", 
            "sub_link": "https://t.me/Uchiha75",
            "force_sub": True
        })
    }
    for filename, content in database.items():
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)

init_db()

def get_db(file):
    try:
        if not os.path.exists(file):
            if "stats" in file: return {"likes": 0, "downloads": 0, "likes_log": [], "downloads_log": []}
            if "files" in file: return []
            return {}
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "stats" in file:
                for k in ["likes", "downloads", "likes_log", "downloads_log"]:
                    if k not in data: data[k] = 0 if "log" not in k else []
            return data
    except:
        return {"likes": 0, "downloads": 0, "likes_log": [], "downloads_log": []} if "stats" in file else []

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    admins = get_db("admins.json")
    return admins.get(str(uid), {}).get(perm, False)

# --- [ أنظمة التحقق والعدادات ] ---

def check_sub(uid):
    conf = get_db("settings.json")
    if not conf.get("force_sub") or int(uid) == OWNER_ID: return True
    try:
        member = bot.get_chat_member(conf["channel_id"], uid)
        return member.status in ['member', 'administrator', 'creator']
    except: return True

def channel_markup():
    st = get_db("stats.json")
    l, d = st.get("likes", 0), st.get("downloads", 0)
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton(f"❤️ تفاعل | {l}", callback_data="hit_like"),
        types.InlineKeyboardButton(f"📩 استلم | {d}", url=f"https://t.me/{BOT_USERNAME}?start=get_files")
    )
    return mk

# --- [ لوحات التحكم الرئيسية ] ---

def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_db("settings.json")
    n_status = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    if has_perm(uid, "can_post"):
        kb.row("نشر في القناة 📣", "إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"):
        kb.row("قسم الإذاعة 📢", "الإحصائيات 📊")
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "صلاحيات أدمن ⚙️")
        kb.row("إضافة اشتراك 🔗", n_status)
        kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    return kb

def perms_kb(admin_id):
    admins = get_db("admins.json")
    p = admins.get(str(admin_id), {"can_post": False, "can_broadcast": False})
    mk = types.InlineKeyboardMarkup(row_width=1)
    mk.add(
        types.InlineKeyboardButton(f"النشر: {'✅' if p['can_post'] else '❌'}", callback_data=f"p_post_{admin_id}"),
        types.InlineKeyboardButton(f"الإذاعة: {'✅' if p['can_broadcast'] else '❌'}", callback_data=f"p_broad_{admin_id}"),
        types.InlineKeyboardButton("حذف الأدمن 🗑️", callback_data=f"p_del_{admin_id}"),
        types.InlineKeyboardButton("إغلاق 💾", callback_data="p_close")
    )
    return mk

# --- [ معالجة الرسائل ] ---

@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    st = get_db("stats.json")

    # نظام استلام الملفات من القناة
    if "get_files" in message.text:
        if uid in st.get("likes_log", []):
            files = get_db("bot_files.json")
            if not files: return bot.send_message(uid, "❌ قاعدة البيانات فارغة.")
            
            bot.send_message(uid, "🚀 تم التحقق من تفاعلك بنجاح! استلم ملفاتك:")
            for item in files:
                try:
                    bot.send_document(uid, item["file_id"], caption=item["caption"])
                    time.sleep(0.3)
                except: continue
            
            if uid not in st.get("downloads_log", []):
                st["downloads"] += 1
                st.setdefault("downloads_log", []).append(uid)
                save_db("stats.json", st)
        else:
            bot.send_message(uid, "⚠️ خطأ! يجب التفاعل بـ (❤️) في القناة أولاً.")
        return

    # الدخول العادي
    if not check_sub(uid):
        conf = get_db("settings.json")
        mk = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("اشترك هنا ⚡", url=conf["sub_link"]))
        return bot.send_message(uid, "❌ اشترك في القناة لتتمكن من استخدام البوت.", reply_markup=mk)

    welcome = "مرحبا ايها مطور 😈SELVA 😈" if uid == OWNER_ID else "مرحبا بك في بوت Uchiha Dz ⚡"
    
    # تسجيل المستخدم وتنبيه الأونر
    with open("users.txt", "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open("users.txt", "a") as f: f.write(f"{uid}\n")
        conf = get_db("settings.json")
        if conf.get("notifications"):
            try: bot.send_message(OWNER_ID, f"🔔 دخول مستخدم جديد: `{uid}`")
            except: pass

    bot.send_message(uid, welcome, reply_markup=main_kb(uid))

@bot.message_handler(func=lambda m: True)
def router(message):
    uid, text = message.from_user.id, message.text

    if text == "الإحصائيات 📊" and has_perm(uid, "can_broadcast"):
        st = get_db("stats.json")
        files = get_db("bot_files.json")
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        msg = (f"📊 **إحصائيات كاملة:**\n\n👥 مستخدمين: `{u_count}`\n"
               f"📁 ملفات: `{len(files)}`\n❤️ تفاعلات: `{st['likes']}`\n"
               f"📥 مستلمين: `{st['downloads']}`")
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif text == "إضافة ملفات 📤" and has_perm(uid, "can_post"):
        pending_files[uid] = []
        mk = types.ReplyKeyboardMarkup(resize_keyboard=True).add("إنهاء الحفظ ✅")
        bot.send_message(uid, "📤 أرسل ملفاتك الآن، واضغط إنهاء عند الاكتمال.", reply_markup=mk)
        bot.register_next_step_handler(message, file_collector)

    elif text == "نشر في القناة 📣" and has_perm(uid, "can_post"):
        conf = get_db("settings.json")
        files = get_db("bot_files.json")
        if not files: return bot.send_message(uid, "❌ لا توجد ملفات.")
        cap = f"⚡ **Uchiha Dz Update** ⚡\n\n📁 الملفات: {len(files)}\n🚀 السرعة: فائقة\n━━━━━━━━━━━━━━"
        bot.send_message(conf["channel_id"], cap, reply_markup=channel_markup(), parse_mode="Markdown")
        bot.send_message(uid, "✅ تم النشر بنجاح.")

    elif text == "صلاحيات أدمن ⚙️" and uid == OWNER_ID:
        admins = get_db("admins.json")
        if not admins: return bot.send_message(uid, "❌ لا يوجد أدمنية.")
        for aid in admins:
            bot.send_message(uid, f"👤 أدمن: `{aid}`", reply_markup=perms_kb(aid), parse_mode="Markdown")

    elif text == "إضافة أدمن ➕" and uid == OWNER_ID:
        m = bot.send_message(uid, "أرسل آيدي الأدمن الجديد:")
        bot.register_next_step_handler(m, add_admin_step)

    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        save_db("bot_files.json", [])
        bot.send_message(uid, "🗑️ تم تصفير قاعدة بيانات الملفات.")

# --- [ الدوال التنفيذية ] ---

def file_collector(message):
    uid = message.from_user.id
    if message.text == "إنهاء الحفظ ✅":
        db = get_db("bot_files.json")
        db.extend(pending_files[uid]); save_db("bot_files.json", db)
        bot.send_message(uid, f"✅ تم حفظ {len(pending_files[uid])} ملف.", reply_markup=main_kb(uid))
        del pending_files[uid]; return

    fid = message.document.file_id if message.document else (message.video.file_id if message.video else (message.photo[-1].file_id if message.photo else None))
    if fid:
        pending_files.setdefault(uid, []).append({"file_id": fid, "caption": message.caption or ""})
        bot.send_message(uid, f"📥 استلمت ({len(pending_files[uid])})...")
    bot.register_next_step_handler(message, file_collector)

def add_admin_step(message):
    if message.text.isdigit():
        admins = get_db("admins.json")
        admins[message.text] = {"can_post": True, "can_broadcast": True}
        save_db("admins.json", admins)
        bot.send_message(message.chat.id, "✅ تم الإضافة بنجاح.")
    else: bot.send_message(message.chat.id, "❌ خطأ في الآيدي.")

# --- [ الكول باك ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = call.from_user.id
    st = get_db("stats.json")
    
    if call.data == "hit_like":
        if uid not in st.get("likes_log", []):
            st["likes"] += 1; st.setdefault("likes_log", []).append(uid); save_db("stats.json", st)
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=channel_markup())
            except: pass
            bot.answer_callback_query(call.id, "❤️ شكراً SELVA!")
        else: bot.answer_callback_query(call.id, "⚠️ متفاعل مسبقاً!", show_alert=True)

    elif call.data.startswith("p_"):
        if uid != OWNER_ID: return
        admins = get_db("admins.json")
        parts = call.data.split("_")
        if parts[1] == "close": bot.delete_message(call.message.chat.id, call.message.message_id)
        elif parts[1] == "del":
            del admins[parts[2]]; save_db("admins.json", admins)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            p_name = "can_post" if parts[1] == "post" else "can_broadcast"
            admins[parts[2]][p_name] = not admins[parts[2]][p_name]
            save_db("admins.json", admins)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=perms_kb(parts[2]))

if __name__ == "__main__":
    print("🔥 THE ULTIMATE UCHIHA BOT IS ACTIVE...")
    bot.infinity_polling()
