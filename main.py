import telebot
from telebot import types
import os, json

# --- الإعدادات ---
TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
OWNER_ID = 8611300267 
bot = telebot.TeleBot(TOKEN)

# --- نظام الملفات ---
def init_db():
    files = {
        "users.txt": "", 
        "bot_files.txt": "", 
        "admins.json": "{}", 
        "stats.json": json.dumps({"downloads": 0, "likes": 0}),
        "settings.json": json.dumps({"notifications": True, "channel_id": "@Uchiha75", "sub_link": "https://t.me/Uchiha75"})
    }
    for f, c in files.items():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file: file.write(c)

init_db()

def get_conf():
    with open("settings.json", "r", encoding="utf-8") as f: return json.load(f)

def save_conf(conf):
    with open("settings.json", "w", encoding="utf-8") as f: json.dump(conf, f, indent=4)

def has_perm(uid, perm):
    if int(uid) == OWNER_ID: return True
    try:
        admins = json.load(open("admins.json"))
        return admins.get(str(uid), {}).get(perm, False)
    except: return False

def is_subscribed(uid):
    conf = get_conf()
    try:
        status = bot.get_chat_member(conf["channel_id"], uid).status
        return status in ['member', 'administrator', 'creator']
    except: return True # إذا حدث خطأ في البوت نعتبره مشتركا مؤقتا لتفادى التوقف

# --- الكيبورد المطور (تم حذف زر إنهاء) ---
def main_kb(uid):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    conf = get_conf()
    n_text = "إيقاف الإشعارات ❌" if conf.get("notifications") else "تفعيل الإشعارات ✅"
    
    # توزيع الأزرار حسب الصلاحيات
    if has_perm(uid, "can_post"): kb.row("نشر تلقائي 📣", "إضافة ملفات 📤")
    if has_perm(uid, "can_broadcast"): kb.row("إرسال إذاعة 📣", "الإحصائيات 📊")
    
    if int(uid) == OWNER_ID:
        kb.row("إضافة أدمن ➕", "إضافة اشتراك 🔗")
    
    kb.row(n_text)
    if has_perm(uid, "can_reset"): kb.row("تنظيف البيانات 🧹", "تصفير الملفات 🗑️")
    
    return kb

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        conf = get_conf()
        mk.add(types.InlineKeyboardButton("اشترك هنا 📢", url=conf["sub_link"]))
        mk.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="verify_sub"))
        return bot.send_message(uid, "⚠️ يجب الاشتراك في القناة أولاً!", reply_markup=mk)

    bot.send_message(uid, "💎 أهلاً بك في لوحة التحكم الخاصة بك:", reply_markup=main_kb(uid))

# --- معالجة الأزرار الرئيسية ---
@bot.message_handler(func=lambda m: True)
def handle_text_buttons(message):
    uid, text = message.from_user.id, message.text
    
    # 1. زر إضافة أدمن (للمالك فقط)
    if text == "إضافة أدمن ➕" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🆔 أرسل آيدي الشخص المراد جعله أدمن:")
        bot.register_next_step_handler(m, setup_admin_perms)

    # 2. زر إرسال إذاعة
    elif text == "إرسال إذاعة 📣" and has_perm(uid, "can_broadcast"):
        m = bot.send_message(uid, "📢 أرسل الرسالة التي تريد إذاعتها لجميع المستخدمين:")
        bot.register_next_step_handler(m, run_broadcast)

    # 3. زر إضافة اشتراك (للمالك فقط)
    elif text == "إضافة اشتراك 🔗" and int(uid) == OWNER_ID:
        m = bot.send_message(uid, "🔗 أرسل رابط القناة الجديد (t.me/...):")
        bot.register_next_step_handler(m, update_sub_link)

    # 4. زر الإحصائيات
    elif text == "الإحصائيات 📊":
        with open("users.txt", "r") as f: u_count = len(f.read().splitlines())
        st = json.load(open("stats.json"))
        bot.send_message(uid, f"📊 **الإحصائيات:**\n\n👥 مستخدمين: `{u_count}`\n📩 استلام: `{st['downloads']}`\n❤️ تفاعل: `{st['likes']}`", parse_mode="Markdown")

    # 5. تفعيل/إيقاف الإشعارات
    elif text in ["إيقاف الإشعارات ❌", "تفعيل الإشعارات ✅"]:
        conf = get_conf()
        conf["notifications"] = not conf["notifications"]
        save_conf(conf)
        bot.send_message(uid, "⚙️ تم تحديث حالة الإشعارات.", reply_markup=main_kb(uid))

    # 6. تصفير الملفات
    elif text == "تصفير الملفات 🗑️" and has_perm(uid, "can_reset"):
        with open("bot_files.txt", "w") as f: f.write("")
        bot.send_message(uid, "🗑️ تم تصفير جميع الملفات بنجاح.")

# --- دوال الخطوات التالية (Next Step Handlers) ---

def setup_admin_perms(message):
    if not message.text.isdigit(): return bot.send_message(message.chat.id, "❌ آيدي خاطئ.")
    target = message.text
    mk = types.InlineKeyboardMarkup()
    mk.row(types.InlineKeyboardButton("إذاعة ✅", callback_data=f"p_bc_{target}"),
           types.InlineKeyboardButton("نشر ✅", callback_data=f"p_pst_{target}"))
    mk.add(types.InlineKeyboardButton("💾 حفظ الأدمن", callback_data=f"sv_ad_{target}"))
    bot.send_message(message.chat.id, f"⚙️ اختر صلاحيات `{target}`:", reply_markup=mk)

def run_broadcast(message):
    with open("users.txt", "r") as f: users = f.read().splitlines()
    sent = 0
    bot.send_message(message.chat.id, "🚀 بدأت الإذاعة...")
    for u in users:
        try:
            bot.copy_message(u, message.chat.id, message.message_id)
            sent += 1
        except: pass
    bot.send_message(message.chat.id, f"✅ تمت الإذاعة بنجاح لـ {sent} مستخدم.")

def update_sub_link(message):
    if "t.me/" in message.text:
        conf = get_conf()
        conf["sub_link"] = message.text
        conf["channel_id"] = "@" + message.text.split("t.me/")[1].split("/")[0]
        save_conf(conf)
        bot.send_message(message.chat.id, "✅ تم تحديث رابط القناة بنجاح.")
    else:
        bot.send_message(message.chat.id, "❌ رابط غير صحيح.")

# --- Callbacks ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid, data = call.from_user.id, call.data
    
    if data.startswith("sv_ad_"):
        target = data.split("_")[-1]
        admins = json.load(open("admins.json"))
        # نعطي صلاحيات افتراضية بسيطة عند الحفظ
        admins[target] = {"can_broadcast": True, "can_post": True, "can_add_files": True, "can_reset": False}
        with open("admins.json", "w") as f: json.dump(admins, f)
        bot.edit_message_text(f"✅ تم تفعيل الأدمن `{target}` بنجاح.", call.message.chat.id, call.message.message_id)

    elif data == "verify_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ شكراً لاشتراكك!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(uid, "💎 تم التحقق، يمكنك استخدام البوت الآن.", reply_markup=main_kb(uid))
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد!", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()

