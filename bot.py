import os
import sqlite3
import yt_dlp
import random
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# --- SOZLAMALAR ---
API_TOKEN = '8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg'
CHANNEL_ID = '@temuzikinsta'
ADMIN_ID = 6488199143

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- BAZA ---
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')
conn.commit()

class FSM(StatesGroup):
    waiting_for_link = State()
    waiting_for_name = State()

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📥 Video/Audio yukla", "✨ Niklar paneli", "🎮 O'yin", "💰 Valyuta kursi", "📊 Statistika", "Rek heshteg")
    return markup

# --- START ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (message.from_user.id,))
    conn.commit()
    if not await is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Obuna bo'lish", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        await message.answer("Botdan foydalanish uchun kanalimizga obuna bo'ling:", reply_markup=markup)
    else:
        await message.answer("Xush kelibsiz! Tanlang:", reply_markup=get_main_markup())

# --- MEDIA YUKLAGICH ---
@dp.message_handler(text="📥 Video/Audio yukla")
async def ask_link(message: types.Message):
    await message.answer("Instagram/YouTube havolasini yuboring:")
    await FSM.waiting_for_link.set()

@dp.message_handler(state=FSM.waiting_for_link)
async def process_media(message: types.Message, state: FSMContext):
    await message.answer("Yuklanmoqda...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'media.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        await message.answer_video(video=open('media.mp4', 'rb'))
        os.system("ffmpeg -i media.mp4 audio.mp3 -y")
        await message.answer_audio(audio=open('audio.mp3', 'rb'))
    except Exception as e: await message.answer(f"Xatolik: {e}")
    finally: state.finish()

# --- NIKLAR PANELI ---
@dp.message_handler(text="✨ Niklar paneli")
async def nick_panel(message: types.Message):
    await message.answer("Ism va familiyangizni yozing:")
    await FSM.waiting_for_name.set()

@dp.message_handler(state=FSM.waiting_for_name)
async def gen_nick(message: types.Message, state: FSMContext):
    symbols = ["꧁", "⚡", "🔥", "☠", "⚔", "💎"]
    parts = message.text.split()
    if len(parts) >= 2:
        await message.answer(f"Sizning nik: {random.choice(symbols)}{parts[0]}_{parts[1]}{random.choice(symbols)}")
    await state.finish()

# --- O'YIN ---
@dp.message_handler(text="🎮 O'yin")
async def game_menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("🪨 Tosh", "✂️ Qaychi", "📄 Qog'oz", "Ortga")
    await message.answer("O'yinni tanlang:", reply_markup=markup)

@dp.message_handler(text=["🪨 Tosh", "✂️ Qaychi", "📄 Qog'oz"])
async def play_game(message: types.Message):
    bot_choice = random.choice(["🪨 Tosh", "✂️ Qaychi", "📄 Qog'oz"])
    await message.answer(f"Bot tanladi: {bot_choice}")

# --- HESHTEGLAR ---
@dp.message_handler(text="Rek heshteg")
async def rek_menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Yapon", "Mashina", "Sport", "Humans", "Ortga")
    await message.answer("Tanlang:", reply_markup=markup)

@dp.message_handler(text=["Yapon", "Mashina", "Sport", "Humans"])
async def show_rek(message: types.Message):
    data = {
        "Yapon": "#Japan #Tokyo #Kyoto #JapaneseCulture #TravelJapan #Nippon #ExploreJapan #VisitJapan #JapanTrip #JapaneseFood #Anime #Osaka #Nature #Shibuya #Harajuku #MtFuji #Culture #Tradition #JapanLife #StreetPhotography #SummerInJapan #JapanTravel #TokyoLife #Zen #History #Samurai #CherryBlossom #JapanAdventure #Kawaii #NipponLife",
        "Mashina": "#Cars #LuxuryCars #Supercars #DubaiCars #CarLovers #Speed #Auto #SportCar #LuxuryLifestyle #CarPhotography #Drift #Turbo #V8 #Ferrari #Lamborghini #BMW #Mercedes #Porsche #CarSpotting #DreamCar #ModifiedCars #FastAndFurious #Automotive #CarDesign #Engine #RaceTrack #StreetRacing #Vehicle #Hypercar",
        "Sport": "#Fitness #Motivation #Sport #Training #Gym #Workout #Bodybuilding #HealthyLifestyle #Athlete #GymMotivation #FitLife #CrossFit #Exercise #Strength #Endurance #Football #Running #Yoga #HealthyEating #Wellness #GymLife #Champion #GameDay #SportLife #Active #Muscle #Trainer #FitnessGoals #SportsTraining #Winning",
        "Humans": "#Humanity #Life #History #People #Unity #Portrait #StreetPortrait #HumanLife #Culture #Storytelling #Empathy #Community #Inspiration #LifeQuotes #Philosophy #Global #HumanSpirit #Kindness #Connection #HumanRights #Society #World #TravelPeople #PortraitPhotography #Soul #Peace #LifeJourney #HumanExperience #CultureTrip #GlobalCitizen"
    }
    await message.answer(data.get(message.text))

# --- ADMIN VA STATISTIKA ---
@dp.message_handler(commands=['stat'])
async def stat(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute('SELECT COUNT(*) FROM users')
        await message.answer(f"📊 Jami foydalanuvchilar: {cursor.fetchone()[0]}")

@dp.message_handler(text="💰 Valyuta kursi")
async def currency(message: types.Message):
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(i for i in res if i["Ccy"] == "USD")
        await message.answer(f"🇺🇸 1 USD = {usd['Rate']} so'm")
    except: await message.answer("Kursni aniqlab bo'lmadi.")

@dp.message_handler(text="Ortga")
async def back(message: types.Message):
    await message.answer("Asosiy menyu:", reply_markup=get_main_markup())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
