import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# Sozlamalar
TOKEN = "8870187278:AAGqNxIYK1sKADwFzSUlbOsUoeP_s_XuPtw"
CHANNEL = "@temuzikinsta
SECOND_BOT_URL = "https://t.me/insta_hesh_bot"

def extract_hashtags(text):
    hashtags = re.findall(r"#(\w+)", text)
    return ", ".join([f"#{tag}" for tag in hashtags]) if hashtags else "Heshteg topilmadi"

async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Video havolasini yuboring, men uni yuklab beraman va matndagi heshteglarni ajratib beraman.")

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await is_subscribed(query.from_user.id, context):
        await query.answer("✅ Obuna tasdiqlandi!")
        await query.message.delete()
    else:
        await query.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Obunani tekshirish
    if not await is_subscribed(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna", url=f"https://t.me/{CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("🤖 @insta_hesh_bot", url=SECOND_BOT_URL)],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check")]
        ]
        await update.message.reply_text("Botdan foydalanish uchun obuna bo'ling:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Heshteglarni ajratish
    hashtags = extract_hashtags(text)
    await update.message.reply_text(f"Topilgan heshteglar:\n{hashtags}")

    status = await update.message.reply_text("Yuklanmoqda... ⏳")
    try:
        # Video yuklash
        ydl_opts_video = {'format': 'best', 'outtmpl': 'file.mp4'}
        with YoutubeDL(ydl_opts_video) as ydl: ydl.download([text])
        await update.message.reply_video(video=open('file.mp4', 'rb'), caption="Mana videongiz!")
        
        # Musiqa yuklash
        ydl_opts_audio = {'format': 'bestaudio', 'outtmpl': 'file.mp3'}
        with YoutubeDL(ydl_opts_audio) as ydl: ydl.download([text])
        await update.message.reply_audio(audio=open('file.mp3', 'rb'), caption="Mana musiqangiz!")
        
        await status.delete()
        os.remove('file.mp4')
        os.remove('file.mp3')
    except Exception as e:
        await status.edit_text(f"Xatolik yuz berdi: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub, pattern="check"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot muvaffaqiyatli ishga tushdi!")
    app.run_polling()

if __name__ == '__main__':
    main()
