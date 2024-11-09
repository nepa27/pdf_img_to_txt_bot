from os import listdir, path, remove

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    ContentType,
    FSInputFile,
    Message,
    ReplyKeyboardRemove,
)

from constants import CONTINUE_WORK, GET_TEXT, GET_FILE, STOP_WORK, USERS_DATA
from keybords.for_questions import get_answers_kb, yes_no_kb
from main import logger
from utils.pdf_to_text import extract_text_from_pdf
from utils.img_to_text import extract_text_from_image

router = Router()


async def download_file(
    message: Message, bot: Bot, user_id: int, file_name: str
):
    try:
        if message.content_type == ContentType.DOCUMENT:
            file = await bot.get_file(message.document.file_id)
        elif message.content_type == ContentType.PHOTO:
            file = await bot.get_file(message.photo[-1].file_id)
        else:
            return

        file_path = file.file_path
        await bot.download_file(
            file_path, f"{USERS_DATA}/{user_id}_{file_name}"
        )
    except BaseException as e:
        logger.error(f"Ошибка при загрузке файла: {str(e)}")
        await message.answer(f"Ошибка при загрузке файла: {str(e)}")


async def send_extracted_text(
    message: Message, bot: Bot, user_id: int, file_path: str
):
    try:
        text = (
            await extract_text_from_pdf(file_path, user_id, bot)
            if file_path.endswith(".pdf")
            else await extract_text_from_image(file_path)
        )
        await message.answer(text)
        logger.info(f"Бот отправил пользователю {user_id} обработанный текст.")
        await message.answer(
            "Работа с этим файлом завершена?", reply_markup=yes_no_kb()
        )
    except TelegramBadRequest:
        await message.answer(
            "Ого, так много текста! У меня не получается "
            "отправить вам текст одним сообщением. "
            "Отправляю файл!"
        )
        await send_text_in_file(message, bot)


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запустил бота.")
    await message.answer(
        "Отправьте файл pdf или изображение, из которого нужно "
        "извлечь текст.\nДля перезапуска бота нажмите /stop, затем /start",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("stop"))
async def stop_conversation(message: Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} остановил бота.")
    await message.answer(
        "Бот остановлен. Нажмите /start, чтобы продолжить",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: Message, bot: Bot):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} отправил файл на обработку.")

    if message.document.mime_type == "application/pdf":
        await message.answer(
            "Вы отправили PDF-файл. Как вы хотите получить текст?",
            reply_markup=get_answers_kb(),
        )
        await download_file(message, bot, user_id, "file.pdf")
    elif message.document.mime_type.startswith("image/"):
        await message.answer(
            "Вы отправили изображение. Как вы хотите получить текст?",
            reply_markup=get_answers_kb(),
        )
        await download_file(message, bot, user_id, "file")
    else:
        await message.answer("Пожалуйста, отправьте PDF-файл или изображение.")


@router.message(F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message, bot: Bot):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} отправил изображение на обработку.")
    await message.answer(
        "Вы отправили изображение. Как вы хотите получить текст?",
        reply_markup=get_answers_kb(),
    )
    await download_file(message, bot, user_id, "file")


@router.message(
    F.text & ~F.text.in_([GET_TEXT, GET_FILE, STOP_WORK, CONTINUE_WORK])
    | F.content_type.in_(
        [ContentType.PHOTO, ContentType.STICKER, ContentType.VIDEO]
    )
)
async def handle_other_content(message: Message):
    await message.answer("Прошу, следуйте инструкциям!")


@router.message(F.text == GET_TEXT)
async def send_text_in_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    file_path = f"{USERS_DATA}/{user_id}_file.pdf"

    if path.exists(file_path):
        await send_extracted_text(message, bot, user_id, file_path)
    else:
        await send_extracted_text(
            message, bot, user_id, f"{USERS_DATA}/{user_id}_file"
        )


@router.message(F.text == GET_FILE)
async def send_text_in_file(message: Message, bot: Bot):
    user_id = message.from_user.id
    file_path = f"{USERS_DATA}/{user_id}_extracted_text.txt"
    files = listdir(USERS_DATA)

    if not path.exists(file_path):
        for file in files:
            if file.startswith(f"{user_id}"):
                if file.endswith(".pdf"):
                    text = await extract_text_from_pdf(
                        f"{USERS_DATA}/{file}", user_id, bot
                    )
                else:
                    text = await extract_text_from_image(
                        f"{USERS_DATA}/{file}"
                    )

        with open(file_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

    input_file = FSInputFile(file_path)
    await message.answer_document(
        input_file, caption="Вот ваш текст из отправленного файла."
    )
    logger.info(f"Бот отправил пользователю {user_id} обработанный текст.")
    await message.answer(
        "Работа с этим файлом завершена?", reply_markup=yes_no_kb()
    )


@router.message(F.text == STOP_WORK)
async def delete_users_file(message: Message):
    user_id = message.from_user.id
    files = listdir(USERS_DATA)

    for file in files:
        if file.startswith(f"{user_id}"):
            remove(f"{USERS_DATA}/{file}")
            logger.info(f"Пользовательский файл {file} был удален.")

    await message.answer(
        "Для продолжения работы загрузите новый файл",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text == CONTINUE_WORK)
async def continue_work(message: Message):
    await message.answer(
        "Как вы хотите получить текст?", reply_markup=get_answers_kb()
    )
