import json
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# قراءة البيانات من الملفات
with open("itemData.json", "r") as f:
    items_data = json.load(f)

with open("cdn.json", "r") as f:
    cdn_data = json.load(f)

# دالة البحث عن العنصر
def search_item(query):
    for item in items_data:
        if query.lower() in item.get("description", "").lower():
            item_id = item.get("itemID")
            return item, item_id
    return None, None

# دالة جلب رابط الصورة بناءً على itemID
def get_image_url(item_id):
    for cdn_entry in cdn_data:
        if item_id in cdn_entry:
            return cdn_entry[item_id]
    return None

# دالة الرد عند استقبال كلمات البحث
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    item, item_id = search_item(query)
    
    if item:
        image_url = get_image_url(item_id)
        response_text = f"🔹 الوصف: {item.get('description')}\n🔸 التفاصيل: {item.get('description2')}"
        if image_url:
            await update.message.reply_photo(photo=image_url, caption=response_text)
        else:
            await update.message.reply_text(response_text)
    else:
        await update.message.reply_text("❌ لم يتم العثور على العنصر المطلوب.")

# بدء البوت وتوجيه الرسائل
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل اسم العنصر للبحث عنه.")

def main():
    TOKEN = "7361470544:AAEitqyfPIq2BFP33Hq38D6J3MxYxV40Q2I"
    app = ApplicationBuilder().token(TOKEN).build()
    
    # تعريف الأوامر والردود
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
