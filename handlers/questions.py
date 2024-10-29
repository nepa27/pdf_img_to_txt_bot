from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from keybords.for_questions import get_cities_kb
from utils.get_weather import get_weather

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'В каком городе вы хотите узнать погоду?\n'
        'Для перезапуска бота нажмите /stop, затем /start',
        reply_markup=get_cities_kb()
    )
@router.message(Command('stop'))
async def stop_conversation(message: Message):
    await message.answer('Бот остановлен. Нажмите /start, чтобы продолжить')

@router.message(F.location)
async def get_location(message: Message):
    await message.answer(
        await get_weather(
            message.location.latitude,
            message.location.longitude
        )
    )

@router.message(F.text.lower() == 'другой город')
async def ask_for_city_name(message: Message):
    await message.answer('Введите название города')

@router.message(F.text)
async def custom_city(message: Message):
    response = await get_weather(message.text)
    if response == 'Нет данных':
        await message.answer('Это не название города!')
    else:
        await message.answer(response)

@router.message()
async def handle_non_text_messages(message: Message):
    await message.answer("Это не название города!")
