# =========================================================================
# ⚡ Uchiha Dz - THE SUPREME MONSTER BOT (ULTRA DETAILED SOURCE) ⚡
# 🛠️ Master Architect: SELVA ZOLDEK | 🆔 ID: 8611300267
# 🔄 Version: 300.0.0 (NO COMPRESSION - NO SHORTCUTS)
# 🛡️ Status: AUTO-NAMING SUBSCRIPTION LINKS & FULL PERMISSIONS
# =========================================================================

import telebot
from telebot import types
import os
import json
import time

# --- [ 1. CONFIGURATION & CONSTANTS ] ---

# توكن البوت الخاص بك
BOT_TOKEN = "8401184550:AAH0x8_WC-h3kxOn4RoP3ASTOm7n84TJteU"

# معرف المطور (أنت)
DEVELOPER_ID = 8611300267 

# معرف القناة الرسمية للتواصل
OFFICIAL_CHANNEL = "@Uchiha75"  

# تهيئة كائن البوت
bot = telebot.TeleBot(BOT_TOKEN)

# --- [ 2. DATABASE MANAGEMENT (EXPANDED) ] ---

def load_json_file(file_path, default_data):
    """تحميل البيانات من ملفات JSON بشكل مفصل جداً"""
    if os.path.exists(file_path) == False:
        # إذا لم يكن الملف موجوداً، قم بإنشائه
        file_handle = open(file_path, "w", encoding="utf-8")
        json.dump(default_data, file_handle, indent=4, ensure_ascii=False)
        file_handle.close()
        return default_data
    else:
        # إذا كان الملف موجوداً، قم بقراءته
        try:
            file_handle = open(file_path, "r", encoding="utf-8")
            data_content = json.load(file_handle)
            file_handle.close()
            return data_content
        except Exception as error:
            print("Error loading JSON: " + str(error))
            return default_data

def save_json_file(file_path, data_to_write):
    """حفظ البيانات في ملفات JSON بشكل مفصل جداً"""
    try:
        file_handle = open(file_path, "w", encoding="utf-8")
        json.dump(data_to_write, file_handle, indent=4, ensure_ascii=False)
        file_handle.close()
        return True
    except Exception as error:
        print("Error saving JSON: " + str(error))
        return False

# تهيئة الملفات الأساسية للنظام
def boot_system_files():
    # إحصائيات التفاعل
    load_json_file("stats.json", {"likes": 0, "receives": 0, "interacted": [], "received": []})
    
    # ملفات البوت
    load_json_file("bot_files.json", [])
    
    # قائمة الاشتراكات
    load_json_file("subs.json", [])
    
    # سجل الأدمنية (المطور له الصلاحيات الكاملة دائماً)
    default_admins = {
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
    load_json_file("admins.json", default_admins)
    
    # سجل المستخدمين (Text)
    if os.path.exists("users.txt") == False:
        file_f = open("users.txt", "w")
        file_f.close()

boot_system_files()

# --- [ 3. SECURITY & SUBSCRIPTION CHECKS ] ---

def user_has_permission(uid, permission_key):
    """فحص صلاحية معينة للمستخدم بشكل مفصل"""
    if uid == DEVELOPER_ID:
        return True
    
    admins_database = load_json_file("admins.json", {})
    string_id = str(uid)
    
    if string_id in admins_database:
        admin_data = admins_database[string_id]
        permissions = admin_data.get("perms", {})
        status = permissions.get(permission_key, False)
        return status
    
    return False

def check_forced_subscription(uid):
    """فحص الاشتراك الإجباري في القنوات والروابط"""
    if uid == DEVELOPER_ID:
        return True
    
    subscription_list = load_json_file("subs.json", [])
    
    if len(subscription_list) == 0:
        return True
    
    for sub_item in subscription_list:
        link = sub_item['link']
        if link.startswith("@"):
            try:
                member_status = bot.get_chat_member(link, uid).status
                if member_status == "left":
                    return False
                if member_status == "kicked":
                    return False
            except Exception:
                continue
    return True

# --- [ 4. UI KEYBOARD BUILDERS ] ---

def build_admin_perms_keyboard(target_aid):
    """بناء كيبورد الصلاحيات بشكل تفصيلي"""
    all_admins = load_json_file("admins.json", {})
    str_target = str(target_aid)
    
    if str_target not in all_admins:
        return None
    
    perms = all_admins[str_target]["perms"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # استخراج حالات الصلاحيات
    s1 = "✅" if perms.get("upload") == True else "❌"
    s2 = "✅" if perms.get("publish") == True else "❌"
    s3 = "✅" if perms.get("stats") == True else "❌"
    s4 = "✅" if perms.get("clean") == True else "❌"
    s5 = "✅" if perms.get("reset") == True else "❌"
    s6 = "✅" if perms.get("broadcast") == True else "❌"
    
    # إضافة الأزرار يدوياً واحداً تلو الآخر
    btn1 = types.InlineKeyboardButton("إضافة ملف 📤: " + s1, callback_data="TOG_" + str_target + "_upload")
    btn2 = types.InlineKeyboardButton("نشر في قناة 📣: " + s2, callback_data="TOG_" + str_target + "_publish")
    btn3 = types.InlineKeyboardButton("إحصائيات 📊: " + s3, callback_data="TOG_" + str_target + "_stats")
    btn4 = types.InlineKeyboardButton("تنظيف بيانات 🧹: " + s4, callback_data="TOG_" + str_target + "_clean")
    btn5 = types.InlineKeyboardButton("تصفير 🗑️: " + s5, callback_data="TOG_" + str_target + "_reset")
    btn6 = types.InlineKeyboardButton("إذاعة 📡: " + s6, callback_data="TOG_" + str_target + "_broadcast")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    
    back_btn = types.InlineKeyboardButton("🔙 العودة لقائمة الأدمنية", callback_data="GOTO_ADMINS")
    markup.add(back_btn)
    
    return markup

def build_user_subs_keyboard():
    """بناء كيبورد الاشتراك للمستخدمين"""
    subs_data = load_json_file("subs.json", [])
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for item in subs_data:
        link_str = item['link']
        if link_str.startswith("@"):
            final_url = "https://t.me/" + link_str.replace("@", "")
        else:
            final_url = link_str
            
        markup.add(types.InlineKeyboardButton(text="📢 " + item['title'], url=final_url))
    
    check_btn = types.InlineKeyboardButton(text="✅ تم الاشتراك، تحقق الآن", callback_data="VERIFY_SUBS")
    markup.add(check_btn)
    return markup

# --- [ 5. CORE HANDLERS & LOGIC ] ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    
    # التحقق من الاشتراك
    if check_forced_subscription(uid) == False:
        bot.send_message(uid, "⚠️ عذراً! يجب الاشتراك في القنوات التالية أولاً:", reply_markup=build_user_subs_keyboard())
        return

    # تسجيل المستخدم في الأرشيف
    file_r = open("users.txt", "r")
    current_users = file_r.read()
    file_r.close()
    
    if str(uid) not in current_users:
        file_a = open("users.txt", "a")
        file_a.write(str(uid) + "\n")
        file_a.close()

    # تحديد رسالة الترحيب المطلوبة
    if uid == DEVELOPER_ID:
        welcome_txt = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
    else:
        welcome_txt = "أهلاً بك في نظام Uchiha Dz ⚡"

    # إنشاء الكيبورد الرئيسي السفلي
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    admins_db = load_json_file("admins.json", {})
    
    if str(uid) in admins_db or uid == DEVELOPER_ID:
        main_kb.add("لوحة تحكم الأدمن 🛠️")
    else:
        main_kb.add("استلام الملفات 📥")
        
    bot.send_message(uid, welcome_txt, reply_markup=main_kb)

# --- [ 6. CALLBACK ENGINE (DETAILED) ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    mid = call.message.message_id
    cid = call.message.chat.id
    data = call.data

    # عرض الصلاحيات
    if data.startswith("VIEW_"):
        target_id = data.split("_")[1]
        kb = build_admin_perms_keyboard(target_id)
        bot.edit_message_text("⚙️ إدارة صلاحيات الأدمن: `" + target_id + "`", cid, mid, reply_markup=kb)

    # تبديل حالة الصلاحية
    elif data.startswith("TOG_"):
        parts = data.split("_")
        target_id = parts[1]
        perm_key = parts[2]
        
        admins_db = load_json_file("admins.json", {})
        if target_id in admins_db:
            # عكس الحالة
            current_val = admins_db[target_id]["perms"].get(perm_key, False)
            if current_val == True:
                admins_db[target_id]["perms"][perm_key] = False
            else:
                admins_db[target_id]["perms"][perm_key] = True
            
            save_json_file("admins.json", admins_db)
            # تحديث الواجهة فوراً
            bot.edit_message_reply_markup(cid, mid, reply_markup=build_admin_perms_keyboard(target_id))
            bot.answer_callback_query(call.id, "✅ تم تحديث الحالة")

    # إضافة اشتراك (يقبل رابط فقط)
    elif data == "ADD_SUB_PROMPT":
        prompt_msg = bot.send_message(uid, "🔗 أرسل الرابط الآن:\n(يمكنك إرسال الرابط فقط وسيقوم البوت بتسميته تلقائياً)")
        bot.register_next_step_handler(prompt_msg, logic_save_subscription)

    # التحقق من الاشتراك
    elif data == "VERIFY_SUBS":
        if check_forced_subscription(uid) == True:
            bot.delete_message(cid, mid)
            bot.send_message(uid, "✅ تم التحقق! أرسل /start للدخول.")
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في كل القنوات!", show_alert=True)

    # العودة لقائمة الأدمنية
    elif data == "GOTO_ADMINS":
        admins_db = load_json_file("admins.json", {})
        mk = types.InlineKeyboardMarkup(row_width=1)
        for aid, details in admins_db.items():
            if int(aid) != DEVELOPER_ID:
                mk.add(types.InlineKeyboardButton("👤 " + details['name'], callback_data="VIEW_" + aid))
        bot.edit_message_text("⚙️ قائمة الأدمنية:", cid, mid, reply_markup=mk)

# --- [ 7. ADMIN TOOLS & MENU ] ---

@bot.message_handler(func=lambda message: True)
def handle_admin_tools(message):
    uid = message.from_user.id
    txt = message.text
    
    admins_db = load_json_file("admins.json", {})
    if str(uid) not in admins_db and uid != DEVELOPER_ID:
        return

    if txt == "لوحة تحكم الأدمن 🛠️":
        mk = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        if user_has_permission(uid, "upload"): mk.add("إضافة ملفات 📤")
        if user_has_permission(uid, "publish"): mk.add("نشر في القناة 📣")
        if user_has_permission(uid, "stats"): mk.add("الإحصائيات 📊")
        if uid == DEVELOPER_ID:
            mk.row("تنظيف بيانات 🧹", "تصفير ملفات 🗑️")
            mk.row("إدارة الاشتراك 🔗", "صلاحيات أدمن ⚙️")
        mk.add("🔙 العودة للمنزل")
        bot.send_message(uid, "🛠️ غرفة التحكم:", reply_markup=mk)

    elif txt == "إدارة الاشتراك 🔗" and uid == DEVELOPER_ID:
        subs_db = load_json_file("subs.json", [])
        mk = types.InlineKeyboardMarkup(row_width=1)
        for i in range(len(subs_db)):
            item = subs_db[i]
            mk.add(types.InlineKeyboardButton("🗑️ حذف: " + item['title'], callback_data="DEL_SUB_" + str(i)))
        mk.add(types.InlineKeyboardButton("➕ إضافة رابط جديد", callback_data="ADD_SUB_PROMPT"))
        bot.send_message(uid, "🔗 إدارة الاشتراكات:", reply_markup=mk)

    elif txt == "صلاحيات أدمن ⚙️" and uid == DEVELOPER_ID:
        admins_db = load_json_file("admins.json", {})
        mk = types.InlineKeyboardMarkup(row_width=1)
        for aid, details in admins_db.items():
            if int(aid) != DEVELOPER_ID:
                mk.add(types.InlineKeyboardButton("👤 " + details['name'], callback_data="VIEW_" + aid))
        bot.send_message(uid, "⚙️ اختر الأدمن لتعديل صلاحياته:", reply_markup=mk)

# --- [ 8. SUBSCRIPTION LOGIC (AUTO-NAMING) ] ---

def logic_save_subscription(message):
    """حفظ الرابط الجديد بوضوح تام مع تسمية تلقائية للروابط فقط"""
    user_input = message.text
    subs_list = load_json_file("subs.json", [])
    
    # التحقق من وجود مسافة (اسم مع الرابط)
    if " " in user_input:
        split_data = user_input.split(" ", 1)
        final_link = split_data[0]
        final_title = split_data[1]
    else:
        # إذا أرسل رابط فقط، نضع له اسم تلقائي فخم
        final_link = user_input
        final_title = "رابط إجباري 🔗"
        
    new_sub = {
        "link": final_link,
        "title": final_title
    }
    
    subs_list.append(new_sub)
    save_json_file("subs.json", subs_list)
    bot.send_message(message.chat.id, "✅ تم حفظ الاشتراك بنجاح!\nالرابط: " + final_link + "\nالاسم: " + final_title)

# --- [ 9. RUNTIME ] ---

if __name__ == "__main__":
    # إرسال رسالة الإقلاع للمطور
    try:
        startup_msg = "مرحبا ايها مطور 😈SELVA ZOLDEK 😈\nتم تشغيل نظام الوحش النظام جاهز للخدمة 💎"
        bot.send_message(DEVELOPER_ID, startup_msg)
    except Exception as e:
        print("Startup Notification Error: " + str(e))
        
    print(">>> SYSTEM STATUS: ONLINE")
    bot.infinity_polling()
