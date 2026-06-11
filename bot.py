import telebot
from telebot import types
import yt_dlp
import os

TOKEN = '8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg'
CHANNEL_ID = '@temuzikinsta' 
bot = telebot.TeleBot(TOKEN)

# 1. Majburiy obuna tekshiruvi
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# 2. Asosiy tugmalar (Biznes sxemalar)
def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Heshteglar", url="https://t.me/insta_hesh_bot"))
    markup.add(types.InlineKeyboardButton("💰 Pulli Sxemalar", callback_data="buy_scheme"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.chat.id):
        bot.send_message(message.chat.id, "Xush kelibsiz! Instagram yoki YouTube linkini tashlang.", reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id, f"Botdan foydalanish uchun avval {CHANNEL_ID} kanaliga obuna bo'ling va /start ni qayta bosing.")

# 3. Pulli sxemalar menyusi
@bot.callback_query_handler(func=lambda call: call.data == "buy_scheme")
def scheme_menu(call):
    text = ("🌟 **Premium Sxemalar:**\n\n"
            "1. **Reka Sxemasi:** Videoni qaysi vaqtda va qaysi kunlari joylash sirlari.\n"
            "2. **Viral Heshteglar:** Har qanday video uchun mos keladigan to'plam.\n\n"
            "Bot 4 oy bepul ishlaydi, keyin pulli rejimga o'tadi.\n"
            "Sotib olish uchun admin bilan bog'laning.")
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_markup())

# 4. Linkni qayta ishlash
@bot.message_handler(func=lambda message: message.text and ("http" in message.text))
def download_media(message):
    if not is_subscribed(message.chat.id):
        bot.reply_to(message, "Iltimos, avval kanalga obuna bo'ling!")
        return
    
    bot.reply_to(message, "Yuklanmoqda... Iltimos kuting.")
    
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        
        # Videoni va audioni yuborish
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="Video tayyor!")
        
        os.system("ffmpeg -i video.mp4 audio.mp3")
        with open('audio.mp3', 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption="Musiqa alohida!")
            
    except Exception as e:
        bot.reply_to(message, "Xatolik yuz berdi. Iltimos, linkni tekshiring.")
    
    # Tozalash
    if os.path.exists("video.mp4"): os.remove("video.mp4")
    if os.path.exists("audio.mp3"): os.remove("audio.mp3")

bot.polling(none_stop=True)
