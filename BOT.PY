import telebot
import yt_dlp
import os
from telebot import types

TOKEN = '8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg'
bot = telebot.TeleBot(TOKEN)

# 1. Yuklab olish funksiyasi
def download_media(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info

# 2. Xabarni qayta ishlash
@bot.message_handler(content_types=['text'])
def handle_link(message):
    url = message.text
    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url:
        msg = bot.send_message(message.chat.id, "Video tahlil qilinmoqda...")
        try:
            info = download_media(url)
            caption = info.get('description', '')
            
            # Heshteglarni ajratish
            hashtags = [word for word in caption.split() if word.startswith('#')]
            hash_text = " ".join(hashtags)
            
            # Videoni yuborish
            bot.send_video(message.chat.id, open('video.mp4', 'rb'), caption=f"Video tayyor!")
            
            # Heshteglarni alohida yuborish
            if hash_text:
                bot.send_message(message.chat.id, f"📌 Heshteglar:\n{hash_text}")
            
            # Musiqani alohida ajratish (audio shaklida)
            os.system('ffmpeg -i video.mp4 -vn audio.mp3')
            bot.send_audio(message.chat.id, open('audio.mp3', 'rb'), caption="🎵 Musiqa")
            
            # Fayllarni tozalash
            os.remove('video.mp4')
            os.remove('audio.mp3')
            
        except Exception as e:
            bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")
    else:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri havola yuboring.")

bot.polling(none_stop=True)
