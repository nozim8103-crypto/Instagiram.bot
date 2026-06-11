import telebot
from telebot import types
import yt_dlp
import os
import re
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)
TOKEN = '8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg'
CHANNEL_ID = '@temuzikinsta' 
ADMIN_URL = "https://t.me/roziyev2"
bot = telebot.TeleBot(TOKEN)

# 1. Heshteglarni ajratish
def extract_hashtags(text):
    if not text: return ""
    hashtags = re.findall(r"#(\w+)", text)
    return " ".join([f"#{tag}" for tag in hashtags]) if hashtags else ""

# 2. Obunani tekshirish
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# 3. Asosiy tugmalar
def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Heshteglar", url="https://t.me/insta_hesh_bot"))
    markup.add(types.InlineKeyboardButton("💰 Pulli Sxemalar", callback_data="buy_scheme"))
    return markup

# 4. START va Obuna tekshirish
@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.chat.id):
        bot.send_message(message.chat.id, "Xush kelibsiz! Instagram yoki YouTube linkini tashlang.", reply_markup=main_markup())
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"))
        markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"Botdan foydalanish uchun avval {CHANNEL_ID} kanaliga obuna bo'ling va pastdagi tugmani bosing.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    if is_subscribed(call.message.chat.id):
        bot.edit_message_text("Rahmat! Endi link tashlashingiz mumkin.", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Linkni yuboring:", reply_markup=main_markup())
    else:
        bot.answer_callback_query(call.id, "Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)

# 5. Pulli sxemalar
@bot.callback_query_handler(func=lambda call: call.data == "buy_scheme")
def scheme_menu(call):
    text = (
        "🌟 **Premium Sxemalar:**\n\n"
        "1. **Reka Sxemasi:** Videoni qaysi vaqtda va qaysi kunlari joylash sirlari.\n"
        "2. **Viral Heshteglar:** Har qanday video uchun mos keladigan to'plam.\n\n"
        "⚠️ **Bot birinchi 2 oy bepul ishlaydi, keyin pulli rejimga o'tadi.**\n\n"
        "Sotib olish yoki savollar uchun admin bilan bog'laning:\n"
        "👉 https://t.me/roziyev2"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Admin bilan bog'lanish", url=ADMIN_URL))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# 6. Yuklash va ajratish funksiyasi
@bot.message_handler(func=lambda message: message.text and ("http" in message.text))
def download_media(message):
    if not is_subscribed(message.chat.id):
        bot.reply_to(message, f"Iltimos, avval {CHANNEL_ID} kanaliga obuna bo'ling!")
        return
    
    msg = bot.reply_to(message, "Yuklanmoqda... Iltimos kuting.")
    
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            caption_text = info.get('description', 'Video tayyor!')
            
        hashtags = extract_hashtags(caption_text)
        full_caption = f"{caption_text[:500]}\n\n{hashtags}"
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption=full_caption, reply_markup=main_markup())
        
        os.system("ffmpeg -i video.mp4 audio.mp3")
        with open('audio.mp3', 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption="Musiqa alohida!")
            
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception:
        bot.reply_to(message, "Xatolik yuz berdi. Linkni tekshiring.")
    
    for f in ["video.mp4", "audio.mp3"]:
        if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
