import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# Sozlamalar
TOKEN = "8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg"
CHANNEL1 = "@temuzikinsta" 
CHANNEL2 = "@insta_hesh_bot"  # Siz so'ragan kanal

def extract_hashtags(text):
    hashtags = re.findall(r"#(\w+)", text)
    return "\n".join([f"#{tag}" for tag in hashtags]) if hashtags else "Heshteg topilmadi"

async def is_subscribed(user_id, context, channel):
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Video havolasini yuboring, uni sifatli yuklab beraman va heshteglarni ajrataman.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # 1. Majburiy obuna tekshiruvi
    sub1 = await is_subscribed(user_id, context, CHANNEL1)
    sub2 = await is_subscribed(user_id, context, CHANNEL2)

    if not (sub1 and sub2):
        keyboard = [
            [InlineKeyboardButton("📢 1-Kanal", url=f"https://t.me/{CHANNEL1.replace('@', '')}")],
            [InlineKeyboardButton("📢 2-Kanal", url=f"https://t.me/{CHANNEL2.replace('@', '')}")]
        ]
        await update.message.reply_text("Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # 2. Yuklash jarayoni
    status = await update.message.reply_text("Yuklanmoqda... ⏳")
    try:
        ydl_opts = {'quiet': True, 'format': 'best'}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)
            caption = info.get('description', '')
            
            # Video va Audio yuborish
            await update.message.reply_video(video=open(filename, 'rb'), caption="Mana videongiz!")
            await update.message.reply_audio(audio=open(filename, 'rb'), caption="Musiqasi ham tayyor!")
            
            # Heshteglarni yuborish
            await update.message.reply_text(f"Topilgan heshteglar:\n{extract_hashtags(caption)}")
            
            # Faylni tozalash
            if os.path.exists(filename): os.remove(filename)
            await status.delete()
    except Exception as e:
        await status.edit_text(f"Xatolik yuz berdi: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
