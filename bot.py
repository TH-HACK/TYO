import json
import os
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# قراءة البيانات من الملفات
try:
    with open("itemData.json", "r") as f:
        items_data = json.load(f)
except FileNotFoundError:
    print("❌ ملف 'itemData.json' غير موجود!")
    items_data = []

try:
    with open("cdn.json", "r") as f:
        cdn_data = json.load(f)
except FileNotFoundError:
    print("❌ ملف 'cdn.json' غير موجود!")
    cdn_data = []

# دالة البحث عن العنصر
def search_item(query):
    query = query.lower()
    for item in items_data:
        if query in item.get("description", "").lower() or query in item.get("description2", "").lower():
            return {
                "itemID": item.get("itemID"),
                "description": item.get("description"),
                "description2": item.get("description2"),
                "icon": item.get("icon")
            }
    return None

# البحث في cdn.json
def get_image_url_from_cdn(item_id):
    for cdn_entry in cdn_data:
        if item_id in cdn_entry:
            return cdn_entry[item_id]
    return None

# البحث عن الصورة في المجلد المحدد على GitHub
def search_image_in_github(icon_name):
    github_api_url = "https://api.github.com/repos/jinix6/ff-resources/contents/pngs/300x300"
    try:
        response = requests.get(github_api_url)
        if response.status_code == 200:
            files = response.json()
            for file in files:
                if icon_name in file["name"]:  # تحقق من وجود الأيقونة
                    return file["download_url"]  # رابط التنزيل المباشر
        else:
            print(f"❌ خطأ أثناء الوصول إلى GitHub API: {response.status_code}")
    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء الاتصال بـ GitHub API: {e}")
    return None

# البحث عن الصورة (cdn أو GitHub)
def get_image_url(icon_name, item_id):
    # البحث في cdn.json
    image_url = get_image_url_from_cdn(item_id)
    if image_url:
        return image_url
    
    # البحث في مجلد GitHub باستخدام API
    github_image_url = search_image_in_github(icon_name)
    if github_image_url:
        return github_image_url

    # إذا لم يتم العثور على الصورة
    return None

# تنسيق البيانات بتنسيق JSON مع رموز
def format_json_with_emojis(item_data):
    formatted_json = (
        "{\n"
        f"  🔹 \"itemID\": \"{item_data['itemID']}\",\n"
        f"  📝 \"description\": \"{item_data['description']}\",\n"
        f"  📄 \"description2\": \"{item_data['description2']}\",\n"
        f"  🖼 \"icon\": \"{item_data['icon']}\"\n"
        "}"
    )
    return formatted_json

# التعامل مع رسائل المستخدم
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()  # النص الذي أرسله المستخدم
    item_data = search_item(query)
    
    if item_data:
        icon_name = item_data["icon"]
        item_id = item_data["itemID"]
        image_url = get_image_url(icon_name, item_id)
        
        # تنسيق البيانات بتنسيق JSON
        formatted_message = f"✨ **معلومات العنصر بتنسيق JSON** ✨\n```json\n{format_json_with_emojis(item_data)}\n```"
        
        if image_url:
            # إرسال الصورة مع النص
            await update.message.reply_photo(
                photo=image_url, 
                caption=formatted_message,
                parse_mode="Markdown"
            )
        else:
            # إرسال النص فقط في حالة عدم وجود صورة
            await update.message.reply_text(
                f"{formatted_message}\n🚫 **الصورة غير متوفرة!**",
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text(
            "🚫 **لم يتم العثور على أي نتائج!**\n🔍 حاول استخدام كلمة أخرى.",
            parse_mode="Markdown"
        )

# إعداد لوحة تحكم الأدمن
ADMIN_PANEL_BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("✅ تفعيل البوت", callback_data="enable_bot"),
         InlineKeyboardButton("❌ تعطيل البوت", callback_data="disable_bot")],
        [InlineKeyboardButton("📊 عدد الأعضاء", callback_data="member_count")]
    ]
)

# التعامل مع أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == 5164991393:  # استبدل YOUR_ADMIN_ID بالـ ID الخاص بك
        await update.message.reply_text(
            "🎉 مرحبًا بك في لوحة تحكم الأدمن!",
            reply_markup=ADMIN_PANEL_BUTTONS,
        )
    else:
        await update.message.reply_text(
            "👋 **مرحبًا بك في بوت البحث عن العناصر!**\n\n"
            "🔍 أرسل اسم العنصر أو جزءًا من اسمه للبحث عنه.\n"
            "📄 سأقوم بعرض المعلومات بتنسيق JSON مع الصورة إذا كانت متاحة."
        )

# التعامل مع الأزرار الخاصة بلوحة التحكم
async def admin_controls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_STATUS
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != 5164991393:  # استبدل YOUR_ADMIN_ID بالـ ID الخاص بك
        await query.answer("❌ ليس لديك صلاحيات.", show_alert=True)
        return

    if query.data == "enable_bot":
        BOT_STATUS = True
        await query.answer("✅ تم تفعيل البوت.")
    elif query.data == "disable_bot":
        BOT_STATUS = False
        await query.answer("❌ تم تعطيل البوت.")
    elif query.data == "member_count":
        # استبدل هنا بطريقة للحصول على عدد الأعضاء، مثلاً:
        member_count = 100  # هذا مجرد مثال
        await query.message.reply_text(f"📊 عدد الأعضاء: {member_count}")

# نقطة بدء تشغيل البوت
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ربط الأوامر والرسائل
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(admin_controls))  # إضافة معالج الأزرار

    print("✅ البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
