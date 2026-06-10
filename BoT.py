import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

TOKEN = "8870187278:AAGqNxIYK1sKADwFzSUlbOsUoeP_s_XuPtw"
CHANNEL = "@insta_mobil"
SECOND_BOT_URL = "https://t.me/insta_aqlli_bot"

async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Havola yuboring, men uni video yoki musiqa qilib yuklab beraman.")

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await is_subscribed(query.from_user.id, context):
        await query.answer("✅ Obuna tasdiqlandi!")
        await query.message.delete()
    else:
        await query.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna", url=f"https://t.me/{CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("🤖 Ikkinchi bot", url=SECOND_BOT_URL)],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check")]
        ]
        await update.message.reply_text("Botdan foydalanish uchun obuna bo'ling:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    url = update.message.text
    status = await update.message.reply_text("Yuklanmoqda... ⏳")
    
    try:
        # Video yuklash
        ydl_opts = {'format': 'best', 'outtmpl': 'file.mp4'}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        await update.message.reply_video(video=open('file.mp4', 'rb'), caption="Mana videongiz!")
        
        # Musiqa (Audio) yuklash uchun alohida
        ydl_opts_audio = {'format': 'bestaudio', 'outtmpl': 'file.mp3'}
        with YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([url])
        await update.message.reply_audio(audio=open('file.mp3', 'rb'), caption="Mana musiqangiz!")
        
        await status.delete()
        os.remove('file.mp4')
        os.remove('file.mp3')
    except Exception as e:
        await status.edit_text(f"Xatolik: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub, pattern="check"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
