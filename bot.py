import logging
import os
import sqlite3
import yt_dlp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# --- Sozlamalar ---
API_TOKEN = '8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg'
CHANNEL_ID = '@temuzikinsta' # Siz bergan kanal
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Baza
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, referrals INTEGER DEFAULT 0)')
conn.commit()

class FSM(StatesGroup):
    waiting_for_link = State()

# --- Menyular ---
def get_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎬 Video yuklash", "Tekin nakrutka", "Rek heshteg", "10 do'st")
    return markup

def check_sub_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Kanalga obuna bo'lish", url="https://t.me/temuzikinsta"))
    markup.add(types.InlineKeyboardButton("Tekshirish", callback_data="check_sub"))
    return markup

# --- Obunani tekshirish funksiyasi ---
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer("Botdan foydalanish uchun avval kanalimizga obuna bo'ling:", reply_markup=check_sub_markup())
    else:
        await message.answer("Xush kelibsiz! Tanlang:", reply_markup=get_main_markup())

@dp.callback_query_handler(text="check_sub")
async def check_sub_callback(call: types.CallbackQuery):
    if await is_subscribed(call.from_user.id):
        await call.message.delete()
        await call.message.answer("Rahmat! Obuna tasdiqlandi.", reply_markup=get_main_markup())
    else:
        await call.answer("Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)

# --- Rek Heshteg menyusi ---
@dp.message_handler(text="Rek heshteg")
async def rek_menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Yapon", "Mashina", "Sport", "Humans", "Ortga")
    await message.answer("Kerakli bo'limni tanlang:", reply_markup=markup)

@dp.message_handler(text="Ortga")
async def back(message: types.Message):
    await message.answer("Bosh menyu:", reply_markup=get_main_markup())

@dp.message_handler(text=["Yapon", "Mashina", "Sport", "Humans"])
async def show_rek(message: types.Message):
    data = {
        "Yapon": ("🇯🇵 日本の文化は素晴らしいです。伝統と現代が混ざり合っています。\n#Japan #Tokyo #Culture #Travel", "yapon"),
        "Mashina": ("🇦🇪 السيارات الفاخرة تعكس الفخامة والقوة. تجربة قيادة لا تنسى.\n#Cars #Luxury #Dubai #Supercar", "mashina"),
        "Sport": ("🇺🇸 Sports training is the key to a healthy and strong body. Keep pushing your limits!\n#Fitness #Gym #Sport #Motivation", "sport"),
        "Humans": ("🇬🇧 Every human has a unique story to tell. Let's celebrate our diversity and kindness.\n#Humanity #Life #People #World", "humanity")
    }
    text = data[message.text][0]
    await message.answer(text)

# --- Video yuklash va Boshqalar ---
@dp.message_handler(text="🎬 Video yuklash")
async def start_extract(message: types.Message):
    await message.answer("Instagram havolasini yuboring:")
    await FSM.waiting_for_link.set()

@dp.message_handler(state=FSM.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    await message.answer("Yuklanmoqda...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            caption = info.get('description', '')
        await message.answer_video(open('video.mp4', 'rb'))
        hashtags = [w for w in caption.split() if w.startswith('#')]
        if hashtags: await message.answer(f"Hashtaglar: {' '.join(hashtags)}")
        if os.path.exists('video.mp4'): os.remove('video.mp4')
    except: await message.answer("Xatolik! Havola noto'g'ri.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
