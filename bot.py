import json
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

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
def get_image_url(item_id):
    for cdn_entry in cdn_data:
        if item_id in cdn_entry:
            return cdn_entry[item_id]
    return None

# البحث في GitHub
def search_github_image(icon_name):
    github_api_url = "https://api.github.com/repos/jinix6/ff-resources/contents/pngs/300x300"
    try:
        response = requests.get(github_api_url)
        if response.status_code == 200:
            files = response.json()
            for file in files:
                if icon_name in file["name"]:  # تحقق من وجود الأيقونة
                    return file["download_url"]  # رابط التنزيل المباشر
        else:
            print(f"❌ خطأ أثناء الوصول إلى GitHub: {response.status_code}")
    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء الاتصال بـ GitHub: {e}")
    return None

# البحث عن الصورة (cdn أو GitHub)
def get_image_url_or_github(icon_name):
    # البحث في cdn.json
    image_url = get_image_url(icon_name)
    if image_url:
        return image_url
    
    # البحث في GitHub
    github_image_url = search_github_image(icon_name)
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
        image_url = get_image_url_or_github(icon_name)
        
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

# بدء البوت عند إرسال أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **مرحبًا بك في بوت البحث عن العناصر!**\n\n"
        "🔍 أرسل اسم العنصر أو جزءًا من اسمه للبحث عنه.\n"
        "📄 سأقوم بعرض المعلومات بتنسيق JSON مع الصورة إذا كانت متاحة."
    )

# نقطة بدء تشغيل البوت
def main():
    # قراءة التوكن من متغيرات البيئة
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ربط الأوامر والرسائل
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
