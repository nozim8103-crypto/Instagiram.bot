import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# TOKEN va KANALLAR
TOKEN = "8870187278:AAFEzsb2UKK6mtaYJmkfmvf1x1xHRIEaBTM"
CHANNELS = ["@temuzikinsta","@insta_hesh_bot"]

async def is_subscribed(user_id, context):
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']: return False
        except: continue
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Instagramdan video yuklash uchun havola yuboring.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        keyboard = [[InlineKeyboardButton("Kanalga obuna bo'lish 🔗", url="https://t.me/temuzikinsta")]]
        await update.message.reply_text("Botdan foydalanish uchun kanalimizga obuna bo'ling!", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    url = update.message.text.strip()
    status = await update.message.reply_text("Yuklanmoqda... ⏳")
    
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video')
            description = info.get('description', 'Heshteglar mavjud emas.')
            
        await update.message.reply_video(
            video=open('video.mp4', 'rb'), 
            caption=f"📝 {title}\n\n🏷 {description[:500]}"
        )
        await status.delete()
        os.remove('video.mp4')
    except Exception as e:
        await status.edit_text(f"Xatolik yuz berdi: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
