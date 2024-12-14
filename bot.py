import json
import os
from telegram import Update
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
            description = item.get("description")
            return item_id, description
    return None, None

# دالة البحث عن رابط الصورة في cdn.json
def get_image_url(item_id):
    for cdn_entry in cdn_data:
        if item_id in cdn_entry:
            return cdn_entry[item_id]
    return None

# التعامل مع رسائل المستخدم
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()  # النص الذي أرسله المستخدم
    item_id, description = search_item(query)
    
    if item_id:
        image_url = get_image_url(item_id)
        
        if image_url:
            await update.message.reply_photo(
                photo=image_url, 
                caption=f"🔹 **{description}**\n\nمعرف العنصر: `{item_id}`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"✅ تم العثور على العنصر **{description}** ولكن لم يتم العثور على صورة له.")
    else:
        await update.message.reply_text("❌ لم يتم العثور على أي نتائج. حاول استخدام كلمة أخرى!")

# بدء البوت عند إرسال أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا بك! أرسل اسم العنصر للبحث عنه 🔍.")

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
