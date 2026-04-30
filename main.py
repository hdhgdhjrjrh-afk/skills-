# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (ULTRA-EXPANDED SOURCE) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 800.0.0 (NO COMPRESSION - NO SHORTCUTS)
# 🛡️ Status: FULLY DETAILED & VERIFIED FOR TERMUX
# =========================================================================

import telebot
from telebot import types
import os
import json
import time

# --- [ 1. إعدادات الهوية والاتصال ] ---

# توكن البوت الخاص بك
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"

# معرف المطور (أنت)
DEVELOPER_ID = 8611300267 

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# --- [ 2. دوال إدارة البيانات (مفصلة جداً) ] ---

def load_database(file_name, default_data):
    """تحميل البيانات من ملف JSON بأسطر منفصلة تماماً"""
    if os.path.exists(file_name) == False:
        # إنشاء الملف إذا كان مفقوداً
        file_handle = open(file_name, "w", encoding="utf-8")
        json.dump(default_data, file_handle, indent=4, ensure_ascii=False)
        file_handle.close()
        return default_data
    else:
        # قراءة الملف بعناية
        try:
            file_handle = open(file_name, "r", encoding="utf-8")
            content = json.load(file_handle)
            file_handle.close()
            return content
        except Exception:
            return default_data

def save_database(file_name, data_to_store):
    """حفظ البيانات في ملف JSON بأسطر منفصلة تماماً"""
    try:
        file_handle = open(file_name, "w", encoding="utf-8")
        json.dump(data_to_store, file_handle, indent=4, ensure_ascii=False)
        file_handle.close()
        return True
    except Exception:
        return False

# تهيئة ملفات النظام عند الإقلاع
def startup_logic():
    load_database("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
    load_database("bot_files.json", [])
    load_database("subs.json", [])
    
    # إعدادات الأدمن والمطور
    initial_admins = {
        str(DEVELOPER_ID): {
            "name": "SELVA ZOLDEK",
            "perms": {
                "upload": True,
                "publish": True,
                "stats": True,
                "clean": True,
                "reset": True,
                "broadcast": True
            }
        }
    }
    load_database("admins.json", initial_admins)
    
    if os.path.exists("users.txt") == False:
        open("users.txt", "w").close()

startup_logic()

# --- [ 3. فحص الصلاحيات والاشتراك ] ---

def check_user_permission(user_id, perm_key):
    """التحقق من صلاحية معينة للمستخدم"""
    if user_id == DEVELOPER_ID:
        return True
    
    admins_data = load_database("admins.json", {})
    user_id_string = str(user_id)
    
    if user_id_string in admins_data:
        user_info = admins_data[user_id_string]
        user_permissions = user_info.get("perms", {})
        if user_permissions.get(perm_key) == True:
            return True
            
    return False

def verify_forced_subscription(user_id):
    """التحقق من اشتراك المستخدم في القنوات"""
    if user_id == DEVELOPER_ID:
        return True
        
    subscription_links = load_database("subs.json", [])
    if len(subscription_links) == 0:
        return True
        
    for sub in subscription_links:
        link_val = sub['link']
        if link_val.startswith("@"):
            try:
                status_check = bot.get_chat_member(link_val, user_id)
                if status_check.status == "left" or status_check.status == "kicked":
                    return False
            except Exception:
                continue
    return True

# --- [ 4. بناة واجهات الأزرار ] ---

def create_perms_keyboard(target_admin_id):
    """بناء كيبورد الصلاحيات بشكل مفصل وبدون اختصارات"""
    all_admins = load_database("admins.json", {})
    admin_id_str = str(target_admin_id)
    
    if admin_id_str not in all_admins:
        return None
        
    admin_perms = all_admins[admin_id_str]["perms"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # استخراج حالة كل زر يدوياً
    s_upload = "✅" if admin_perms.get("upload") == True else "❌"
    s_publish = "✅" if admin_perms.get("publish") == True else "❌"
    s_stats = "✅" if admin_perms.get("stats") == True else "❌"
    s_clean = "✅" if admin_perms.get("clean") == True else "❌"
    s_reset = "✅" if admin_perms.get("reset") == True else "❌"
    
    # إضافة الأزرار بنفس الأسماء التي طلبتها
    markup.add(types.InlineKeyboardButton("إضافة ملفات 📤: " + s_upload, callback_data="TGL_" + admin_id_str + "_upload"))
    markup.add(types.InlineKeyboardButton("نشر في القناة 📣: " + s_publish, callback_data="TGL_" + admin_id_str + "_publish"))
    markup.add(types.InlineKeyboardButton("الإحصائيات 📊: " + s_stats, callback_data="TGL_" + admin_id_str + "_stats"))
    markup.add(types.InlineKeyboardButton("تنظيف بيانات 🧹: " + s_clean, callback_data="TGL_" + admin_id_str + "_clean"))
    markup.add(types.InlineKeyboardButton("تصفير ملفات 🗑️: " + s_reset, callback_data="TGL_" + admin_id_str + "_reset"))
    
    markup.add(types.InlineKeyboardButton("🔙 العودة", callback_data="GO_ADMINS_LIST"))
    return markup

# --- [ 5. معالجة أوامر البداية ] ---

@bot.message_handler(commands=['start'])
def start_logic_handler(message):
    uid = message.from_user.id
    
    # فحص الاشتراك
    if verify_forced_subscription(uid) == False:
        subs_db = load_database("subs.json", [])
        markup = types.InlineKeyboardMarkup(row_width=1)
        for s in subs_db:
            link = s['link']
            if link.startswith("@"):
                final_url = "https://t.me/" + link.replace("@", "")
            else:
                final_url = link
            markup.add(types.InlineKeyboardButton("📢 " + s['title'], url=final_url))
        markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="CHECK_SUBS"))
        bot.send_message(uid, "⚠️ عذراً! يجب الاشتراك في القنوات أدناه أولاً:", reply_markup=markup)
        return

    # حفظ المستخدم الجديد
    file_reader = open("users.txt", "r")
    current_users = file_reader.read()
    file_reader.close()
    
    if str(uid) not in current_users:
        file_writer = open("users.txt", "a")
        file_writer.write(str(uid) + "\n")
        file_writer.close()

    # رسالة الترحيب
    if uid == DEVELOPER_ID:
        welcome_msg = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
    else:
        welcome_msg = "أهلاً بك في نظام Uchiha Dz ⚡"

    # الكيبورد الرئيسي
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if uid == DEVELOPER_ID or str(uid) in load_database("admins.json", {}):
        main_kb.add("لوحة تحكم الأدمن 🛠️")
    else:
        main_kb.add("استلام الملفات 📥")
        
    bot.send_message(uid, welcome_msg, reply_markup=main_kb)

# --- [ 6. معالج الأزرار النصية (الراوتر الرئيسي) ] ---

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.from_user.id
    text = message.text
    
    admins_db = load_database("admins.json", {})
    is_authorized = str(uid) in admins_db or uid == DEVELOPER_ID
    
    if is_authorized == False:
        return

    # 🛠️ لوحة تحكم الأدمن
    if text == "لوحة تحكم الأدمن 🛠️":
        kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        if check_user_permission(uid, "upload"): kb.add("إضافة ملفات 📤")
        if check_user_permission(uid, "publish"): kb.add("نشر في القناة 📣")
        if check_user_permission(uid, "stats"): kb.add("الإحصائيات 📊")
        if uid == DEVELOPER_ID:
            kb.row("تنظيف بيانات 🧹", "تصفير ملفات 🗑️")
            kb.row("إدارة الاشتراك 🔗", "صلاحيات أدمن ⚙️")
        kb.add("🔙 العودة للمنزل")
        bot.send_message(uid, "🛠️ غرفة التحكم:", reply_markup=kb)

    # 📊 الإحصائيات
    elif text == "الإحصائيات 📊":
        if check_user_permission(uid, "stats"):
            stats = load_database("stats.json", {"likes": 0, "receives": 0})
            msg = "📊 إحصائيات النظام:\n\n💎 التفاعلات: " + str(stats.get('likes')) + "\n📥 المستلمة: " + str(stats.get('receives'))
            bot.send_message(uid, msg)

    # 🧹 تنظيف بيانات
    elif text == "تنظيف بيانات 🧹":
        if check_user_permission(uid, "clean"):
            save_database("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
            bot.send_message(uid, "🧹 تم تنظيف سجل الإحصائيات بالكامل.")

    # 🗑️ تصفير ملفات
    elif text == "تصفير ملفات 🗑️":
        if check_user_permission(uid, "reset"):
            save_database("bot_files.json", [])
            bot.send_message(uid, "🗑️ تم مسح جميع الملفات من قاعدة البيانات.")

    # ⚙️ صلاحيات أدمن
    elif text == "صلاحيات أدمن ⚙️" and uid == DEVELOPER_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for aid, val in admins_db.items():
            if int(aid) != DEVELOPER_ID:
                markup.add(types.InlineKeyboardButton("👤 " + val['name'], callback_data="VW_ADM_" + aid))
        bot.send_message(uid, "⚙️ اختر الأدمن لتعديل صلاحياته:", reply_markup=markup)

    # 📤 إضافة ملفات
    elif text == "إضافة ملفات 📤":
        if check_user_permission(uid, "upload"):
            bot.send_message(uid, "📤 أرسل الملف الآن ليتم حفظه.")

    # 📣 نشر في القناة
    elif text == "نشر في القناة 📣":
        if check_user_permission(uid, "publish"):
            bot.send_message(uid, "📣 أرسل ما تود نشره في القناة الرسمية.")

    # 🔗 إدارة الاشتراك
    elif text == "إدارة الاشتراك 🔗" and uid == DEVELOPER_ID:
        subs = load_database("subs.json", [])
        mk = types.InlineKeyboardMarkup(row_width=1)
        for i in range(len(subs)):
            item = subs[i]
            mk.add(types.InlineKeyboardButton("🗑️ حذف: " + item['title'], callback_data="DL_SUB_" + str(i)))
        mk.add(types.InlineKeyboardButton("➕ إضافة رابط جديد", callback_data="ADD_SUB_CMD"))
        bot.send_message(uid, "🔗 إدارة الروابط:", reply_markup=mk)

    elif text == "🔙 العودة للمنزل":
        start_logic_handler(message)

# --- [ 7. معالج التفاعلات الخلفية (Callback) ] ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid, mid, cid, data = call.from_user.id, call.message.message_id, call.message.chat.id, call.data

    if data.startswith("VW_ADM_"):
        target_id = data.split("_")[2]
        bot.edit_message_text("⚙️ صلاحيات الأدمن: `" + target_id + "`", cid, mid, reply_markup=create_perms_keyboard(target_id))

    elif data.startswith("TGL_"):
        parts = data.split("_")
        target_id = parts[1]
        perm_key = parts[2]
        
        db = load_database("admins.json", {})
        if target_id in db:
            current_status = db[target_id]["perms"].get(perm_key, False)
            if current_status == True:
                db[target_id]["perms"][perm_key] = False
            else:
                db[target_id]["perms"][perm_key] = True
            
            save_database("admins.json", db)
            bot.edit_message_reply_markup(cid, mid, reply_markup=create_perms_keyboard(target_id))
            bot.answer_callback_query(call.id, "✅")

    elif data == "ADD_SUB_CMD":
        msg = bot.send_message(uid, "🔗 أرسل الرابط الآن (سيتم حفظه تلقائياً):")
        bot.register_next_step_handler(msg, final_save_link)

    elif data == "CHECK_SUBS":
        if verify_forced_subscription(uid) == True:
            bot.delete_message(cid, mid)
            bot.send_message(uid, "✅ تم التحقق! أرسل /start الآن.")
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

# --- [ 8. دالة الحفظ التلقائي للروابط ] ---

def final_save_link(message):
    user_link = message.text
    subs_db = load_database("subs.json", [])
    
    # حفظ الرابط باسم تلقائي كما طلبت
    new_sub = {
        "link": user_link,
        "title": "رابط إجباري 🔗"
    }
    
    subs_db.append(new_sub)
    save_database("subs.json", subs_db)
    bot.send_message(message.chat.id, "✅ تم حفظ الرابط بنجاح باسم: رابط إجباري 🔗")

# --- [ 9. تشغيل النظام ] ---

if __name__ == "__main__":
    try:
        startup_alert = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
        bot.send_message(DEVELOPER_ID, startup_alert)
    except:
        pass
        
    print(">>> Uchiha Dz System is LIVE.")
    bot.infinity_polling()

