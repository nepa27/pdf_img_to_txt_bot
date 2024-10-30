from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_answers_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Получить текст в сообщении')
    kb.button(text='Получить текст в файле')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
