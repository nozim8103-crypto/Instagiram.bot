import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# Sozlamalar
TOKEN = "8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg"
CHANNEL1 = "@temuzikinsta" # Birinchi kanal
CHANNEL2 = "@insta_hesh_bot"    # Ikkinchi kanal (o'zgartiring)

def extract_hashtags(text):
    hashtags = re.findall(r"#(\w+)", text)
    return "\n".join([f"#{tag}" for tag in hashtags]) if hashtags else "Heshteg topilmadi"

async def is_subscribed(user_id, context, channel):
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Video havolasini yuboring, uni sifatli yuklab beraman.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Majburiy obuna tekshiruvi
    sub1 = await is_subscribed(user_id, context, CHANNEL1)
    sub2 = await is_subscribed(user_id, context, CHANNEL2)

    if not (sub1 and sub2):
        keyboard = [
            [InlineKeyboardButton("📢 1-Kanalga obuna", url=f"https://t.me/{CHANNEL1.replace('@', '')}")],
            [InlineKeyboardButton("📢 2-Kanalga obuna", url=f"https://t.me/{CHANNEL2.replace('@', '')}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check")]
        ]
        await update.message.reply_text("Botdan foydalanish uchun kanallarga obuna bo'ling:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Heshteglarni ajratish
    hashtags = extract_hashtags(text)
    await update.message.reply_text(f"Topilgan heshteglar:\n{hashtags}")

    # Yuklash jarayoni
    status = await update.message.reply_text("Yuklanmoqda... ⏳")
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'media.mp4',
            'quiet': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])
            
        await update.message.reply_video(video=open('media.mp4', 'rb'), caption="Mana videongiz!")
        
        # Audio (musiqa) qismini yuborish
        # Agar video ichidan audio ajratib olish kerak bo'lsa, ffmpeg kerak
        
        if os.path.exists('media.mp4'): os.remove('media.mp4')
        await status.delete()
    except Exception as e:
        await status.edit_text(f"Xatolik: {e}")

if name == 'main':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
