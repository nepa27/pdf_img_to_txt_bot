from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from constants import CONTINUE_WORK, GET_TEXT, GET_FILE, STOP_WORK


def get_answers_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=GET_TEXT)
    kb.button(text=GET_FILE)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=STOP_WORK)
    kb.button(text=CONTINUE_WORK)
    kb.adjust(1)
    return kb.as_markup(
        resize_keyboard=True, input_field_placeholder="Продолжить работу с файлом?"
    )
