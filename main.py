# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (FINAL MASTERPIECE) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 130.0.0 (ULTRA FULL SOURCE - NO DELETIONS)
# =========================================================================

import telebot
from telebot import types
import os
import json
import time

# --- [ 1. الأساسيات ] ---
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"
DEVELOPER_ID = 8611300267 
OFFICIAL_CHANNEL = "@Uchiha75"  

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ذاكرة الجلسات (للرفع والإذاعة)
SESSION = {"upload": {}, "bc_type": None}

# --- [ 2. محرك البيانات ] ---
def db_load(file, default):
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4, ensure_ascii=False)
        return default
    with open(file, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return default

def db_save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# تهيئة النظام
def init_all():
    db_load("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
    db_load("bot_files.json", [])
    db_load("subs.json", [])
    admin_data = {
        str(DEVELOPER_ID): {
            "name": "SELVA ZOLDEK",
            "perms": {"upload": True, "publish": True, "stats": True, "clean": True, "reset": True, "broadcast": True}
        }
    }
    db_load("admins.json", admin_init if 'admin_init' in locals() else admin_data)
    if not os.path.exists("users.txt"): open("users.txt", "w").close()

init_all()

# --- [ 3. الحماية والفحص ] ---
def check_perm(uid, key):
    if uid == DEVELOPER_ID: return True
    admins = db_load("admins.json", {})
    return admins.get(str(uid), {}).get("perms", {}).get(key, False)

def check_sub(uid):
    if uid == DEVELOPER_ID: return True
    subs = db_load("subs.json", [])
    for s in subs:
        if s['link'].startswith("@"):
            try:
                m = bot.get_chat_member(s['link'], uid)
                if m.status in ['left', 'kicked']: return False
            except: continue
    return True

# --- [ 4. الواجهات البرمجية ] ---
def perms_kb(aid):
    admins = db_load("admins.json", {})
    if str(aid) not in admins: return None
    p = admins[str(aid)]["perms"]
    mk = types.InlineKeyboardMarkup(row_width=2)
    lbls = {"upload":"إضافة ملف 📤","publish":"نشر في قناة 📣","stats":"إحصائيات 📊","clean":"تنظيف بيانات 🧹","reset":"تصفير 🗑️","broadcast":"إذاعة 📡"}
    for k, v in lbls.items():
        st = "✅" if p.get(k) else "❌"
        mk.add(types.InlineKeyboardButton(f"{v}: {st}", callback_data=f"TOG_PERM_{aid}_{k}"))
    mk.add(types.InlineKeyboardButton("🔙 العودة", callback_data="BACK_ADM"))
    return mk

# --- [ 5. الأوامر ] ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    if not check_sub(uid):
        subs = db_load("subs.json", [])
        mk = types.InlineKeyboardMarkup(row_width=1)
        for s in subs:
            url = f"https://t.me/{s['link'].replace('@', '')}" if s['link'].startswith("@") else s['link']
            mk.add(types.InlineKeyboardButton(f"📢 اشترك: {s['title']}", url=url))
        mk.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="VERIFY_SUB"))
        bot.send_message(uid, "⚠️ اشترك أولاً للمتابعة:", reply_markup=mk)
        return

    # تسجيل المستخدم
    with open("users.txt", "a+") as f:
        f.seek(0)
        if str(uid) not in f.read(): f.write(f"{uid}\n")

    # الرسالة التي طلبتها
    if uid == DEVELOPER_ID:
        txt = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
    else:
        txt = "أهلاً بك في نظام Uchiha Dz ⚡"

    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if str(uid) in db_load("admins.json", {}) or uid == DEVELOPER_ID:
        mk.add("لوحة تحكم الأدمن 🛠️")
    else:
        mk.add("استلام الملفات 📥")
    bot.send_message(uid, txt, reply_markup=mk)

# --- [ 6. تفاعلات الأزرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    uid, mid, data = call.from_user.id, call.message.message_id, call.data
    
    if data.startswith("VIEW_ADM_"):
        aid = data.split("_")[2]
        bot.edit_message_text(f"⚙️ صلاحيات: `{aid}`", uid, mid, reply_markup=perms_kb(aid))
    
    elif data.startswith("TOG_PERM_"):
        _, _, aid, pk = data.split("_")
        admins = db_load("admins.json", {})
        admins[aid]["perms"][pk] = not admins[aid]["perms"].get(pk, False)
        db_save("admins.json", admins)
        bot.edit_message_reply_markup(uid, mid, reply_markup=perms_kb(aid))
    
    elif data == "ADD_SUB_TRIGGER":
        msg = bot.send_message(uid, "🔗 أرسل الرابط (أو الرابط مسافة الاسم):")
        bot.register_next_step_handler(msg, save_sub)

    elif data == "VERIFY_SUB":
        if check_sub(uid):
            bot.delete_message(uid, mid)
            bot.send_message(uid, "✅ تم التحقق بنجاح! أرسل /start")
        else: bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

# --- [ 7. لوحة التحكم ] ---
@bot.message_handler(func=lambda m: True)
def panel(message):
    uid, txt = message.from_user.id, message.text
    if str(uid) not in db_load("admins.json", {}) and uid != DEVELOPER_ID: return

    if txt == "لوحة تحكم الأدمن 🛠️":
        mk = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        if check_perm(uid, "upload"): mk.add("إضافة ملفات 📤")
        if check_perm(uid, "publish"): mk.add("نشر في القناة 📣")
        if check_perm(uid, "stats"): mk.add("الإحصائيات 📊")
        if uid == DEVELOPER_ID:
            mk.row("تنظيف بيانات 🧹", "تصفير ملفات 🗑️")
            mk.row("إدارة الاشتراك 🔗", "صلاحيات أدمن ⚙️")
        mk.add("🔙 العودة للمنزل")
        bot.send_message(uid, "🛠️ قائمة التحكم بالوحش:", reply_markup=mk)

    elif txt == "إدارة الاشتراك 🔗" and uid == DEVELOPER_ID:
        subs = db_load("subs.json", [])
        mk = types.InlineKeyboardMarkup(row_width=1)
        for i, s in enumerate(subs): mk.add(types.InlineKeyboardButton(f"🗑️ {s['title']}", callback_data=f"DEL_SUB_{i}"))
        mk.add(types.InlineKeyboardButton("➕ إضافة اشتراك", callback_data="ADD_SUB_TRIGGER"))
        bot.send_message(uid, "🔗 القنوات والروابط:", reply_markup=mk)

    elif txt == "صلاحيات أدمن ⚙️" and uid == DEVELOPER_ID:
        admins = db_load("admins.json", {})
        mk = types.InlineKeyboardMarkup()
        for aid, d in admins.items():
            if int(aid) != DEVELOPER_ID: mk.add(types.InlineKeyboardButton(f"👤 {d['name']}", callback_data=f"VIEW_ADM_{aid}"))
        bot.send_message(uid, "⚙️ اختر الأدمن:", reply_markup=mk)

# --- [ 8. الدوال المساعدة ] ---
def save_sub(message):
    t = message.text
    subs = db_load("subs.json", [])
    if " " in t: link, title = t.split(" ", 1)
    else: link, title = t, "رابط جديد"
    subs.append({"link": link, "title": title})
    db_save("subs.json", subs)
    bot.send_message(message.chat.id, "✅ تم الحفظ.")

# --- [ 9. الإقلاع ] ---
if __name__ == "__main__":
    try:
        bot.send_message(DEVELOPER_ID, "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎")
    except: pass
    bot.infinity_polling()

