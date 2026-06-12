import os
import sqlite3
import yt_dlp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '8870187278:AAEEe_heDhMy9zzQXpg48xC-zzQjIe5YDbg'
CHANNEL_ID = '@temuzikinsta'
ADMIN_ID = 6488199143

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, referrals INTEGER DEFAULT 0)')
conn.commit()

class FSM(StatesGroup):
    waiting_for_link = State()

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Heshteg yukla", "Tekin nakrutka", "Rek heshteg", "10 do'st", "Pulli sxema", "Karta", "Reklama xizmati", "Rek heshteg bot")
    return markup

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (message.from_user.id,))
    conn.commit()
    if not await is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Obuna bo'lish", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        markup.add(types.InlineKeyboardButton("Tekshirish", callback_data="check_sub"))
        await message.answer("Botdan foydalanish uchun kanalimizga obuna bo'ling:", reply_markup=markup)
    else:
        await message.answer("Xush kelibsiz! Tanlang:", reply_markup=get_main_markup())

@dp.message_handler(commands=['ok'])
async def approve_payment(message: types.Message):
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        user_id = message.reply_to_message.forward_from.id
        scheme_text = (
            "✅ To'lovingiz tasdiqlandi! Mana siz uchun eksklyuziv 'Rek' sxemasi:\n\n"
            "🕒 **Eng yaxshi vaqt:** 08:00, 13:00, 20:00\n\n"
            "🚀 **Strategiya:** Ilk 3 soniyada qiziqarli kadr qo'ying, trenddagi musiqa ishlating.\n\n"
            "🔥 **Rek Heshteglar:**\n#reels #fyp #instagram #uzbekistan #viral #trending #explore #trend #reelsvideo #foryou\n\n"
            "📝 **Caption:** Ko'pchilik buni bilmaydi, natija hayratda qoldiradi! 🚀 Videoni oxirigacha ko'ring va fikringizni yozing! 👇"
        )
        await bot.send_message(user_id, scheme_text)
        await message.reply("✅ Sxema foydalanuvchiga yuborildi!")

@dp.message_handler(text="Pulli sxema")
async def pay_scheme(message: types.Message):
    await message.answer("Pulli sxema narxi: 12,000 so'm.\n\nKarta: [KARTA JOYI]\n\nTo'lov chekini rasm ko'rinishida yuboring.")

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        await message.answer("Chekingiz qabul qilindi. Admin tekshirmoqda...")

@dp.message_handler(text=["Yapon", "Mashina", "Sport", "Humans"])
async def show_rek(message: types.Message):
    data = {
        "Yapon": "🇯🇵 #Japan #Tokyo #Travel #Culture #Kyoto",
        "Mashina": "🇦🇪 #Cars #Luxury #Dubai #Supercars #Speed",
        "Sport": "🇬🇧 #Fitness #Motivation #Sport #Training #Gym",
        "Humans": "🇪🇸 #Humanity #Life #History #People #Unity"
    }
    await message.answer(data.get(message.text))

@dp.message_handler(text="Rek heshteg")
async def rek_menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Yapon", "Mashina", "Sport", "Humans", "Ortga")
    await message.answer("Tanlang:", reply_markup=markup)

@dp.message_handler(text="Heshteg yukla")
async def start_extract(message: types.Message):
    await message.answer("Instagram havolasini yuboring:")
    await FSM.waiting_for_link.set()

@dp.message_handler(state=FSM.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    await message.answer("Yuklanmoqda...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'user_agent': 'Mozilla/5.0'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            caption = info.get('description', 'Video')
        await message.answer_video(video=open('video.mp4', 'rb'), caption=caption[:1024])
        if os.path.exists('video.mp4'): os.remove('video.mp4')
    except Exception as e: await message.answer(f"Xatolik: {str(e)}")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
