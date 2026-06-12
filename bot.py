import os
import sqlite3
import yt_dlp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# --- SOZLAMALAR ---
API_TOKEN = '8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg'
CHANNEL_ID = '@temuzikinsta'
ADMIN_ID = '123456789'  # O'z ID raqamingizni yozing!

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Baza
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, referrals INTEGER DEFAULT 0)')
conn.commit()

class FSM(StatesGroup):
    waiting_for_link = State()

# --- FUNKSIYALAR ---
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎬 Video yuklash", "Tekin nakrutka", "Rek heshteg", "10 do'st")
    return markup

# --- BOT MANTIG'I ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    args = message.get_args()
    if args and args.isdigit() and int(args) != message.from_user.id:
        cursor.execute('UPDATE users SET referrals = referrals + 1 WHERE id = ?', (int(args),))
        conn.commit()
        await bot.send_message(int(args), "Tabriklaymiz! Siz yangi do'st taklif qildingiz.")
        await bot.send_message(ADMIN_ID, f"Yangi obunachi! Taklif qilgan: {args}")

    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (message.from_user.id,))
    conn.commit()

    if not await is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Obuna bo'lish", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        await message.answer("Botdan foydalanish uchun kanalimizga obuna bo'ling:", reply_markup=markup)
    else:
        await message.answer("Xush kelibsiz! Tanlang:", reply_markup=get_main_markup())

@dp.message_handler(text="Rek heshteg")
async def rek_menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Yapon", "Mashina", "Sport", "Humans", "Ortga")
    await message.answer("Tanlang:", reply_markup=markup)

@dp.message_handler(text=["Yapon", "Mashina", "Sport", "Humans"])
async def show_rek(message: types.Message):
    data = {
        "Yapon": "🇯🇵 日本の伝統文化と現代の技術が融合する魅力的な国です。\n#Japan #Tokyo #Travel #Culture",
        "Mashina": "🇦🇪 دبي هي موطن لأفخم السيارات في العالم وأكثرها تطوراً.\n#Cars #Luxury #Dubai #Supercars",
        "Sport": "🇬🇧 Sports define our strength and push us to overcome every challenge.\n#Fitness #Motivation #Sport #Training",
        "Humans": "🇪🇸 La humanidad es una red compleja de historias, sueños y esperanzas compartidas.\n#Humanity #Life #History #People"
    }
    await message.answer(data.get(message.text))

@dp.message_handler(text="10 do'st")
async def invite_friends(message: types.Message):
    cursor.execute('SELECT referrals FROM users WHERE id = ?', (message.from_user.id,))
    res = cursor.fetchone()
    count = res[0] if res else 0
    bot_link = f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}"
    await message.answer(f"Sizning taklif havolangiz: {bot_link}\n\nHozirgacha {count} ta do‘st taklif qildingiz. 10 taga yetkazsangiz, nakrutka ochiladi!")

@dp.message_handler(text="Tekin nakrutka")
async def free_views(message: types.Message):
    cursor.execute('SELECT referrals FROM users WHERE id = ?', (message.from_user.id,))
    res = cursor.fetchone()
    count = res[0] if res else 0
    if count >= 10:
        await message.answer("Tabriklaymiz! Nakrutka uchun havola: https://leofame.com/free-instagram-views")
    else:
        await message.answer(f"Hali 10 ta do'st yig'madingiz! Hozirda {count} ta bor.")

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
        if hashtags: await message.answer(f"Heshteglar: {' '.join(hashtags)}")
        if os.path.exists('video.mp4'): os.remove('video.mp4')
    except: await message.answer("Xatolik! Havolani tekshiring.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
