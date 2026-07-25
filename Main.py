from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8816866283:AAGJK1TXHj1b7LZQYQOG7e5w18fOfUH51PM"


async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # Eng yuqori sifatdagi rasmni oladi
        photo = update.message.photo[-1]

        await update.message.reply_text(
            f"📸 File ID:\n\n{photo.file_id}",
            parse_mode="Markdown"
        )


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(filters.PHOTO, get_file_id)
)

print("🤖 Bot ishga tushdi...")
app.run_polling(
        
    
            
        
