import os
from os import path

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    ContentType,
    FSInputFile,
    Message,
    ReplyKeyboardRemove
)

from constants import (
    CONTINUE_WORK,
    GET_TEXT,
    GET_FILE,
    STOP_WORK
)
from keybords.for_questions import get_answers_kb, yes_no_kb
from utils.pdf_to_text import extract_text_from_pdf
from utils.img_to_text import extract_text_from_image


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Отправьте файл pdf, из которого нужно извлечь текст.\n'
        'Для перезапуска бота нажмите /stop, затем /start',
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command('stop'))
async def stop_conversation(message: Message):
    await message.answer(
        'Бот остановлен. Нажмите /start, чтобы продолжить',
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: Message, bot: Bot):
    if message.document.mime_type == 'application/pdf':
        await message.answer(
            'Вы отправили PDF-файл. Как вы хотите получить текст?',
            reply_markup=get_answers_kb()
        )
        user_id = message.from_user.id
        try:
            file = await bot.get_file(message.document.file_id)
            file_path = file.file_path
            await bot.download_file(file_path, f'{user_id}_file.pdf')
        except BaseException as e:
            await message.answer(f'Ошибка при загрузке файла: {str(e)}')
    elif message.document.mime_type.startswith('image/'):
        await message.answer(
            'Вы отправили изображение. Как вы хотите получить текст?',
            reply_markup=get_answers_kb()
        )
        user_id = message.from_user.id
        try:
            file = await bot.get_file(message.document.file_id)
            file_path = file.file_path
            await bot.download_file(file_path, f'{user_id}_file')
        except BaseException as e:
            await message.answer(f'Ошибка при загрузке файла: {str(e)}')
    else:
        await message.answer('Пожалуйста, отправьте PDF-файл или изображение.')


@router.message(F.text & ~F.text.in_(
    [GET_TEXT,
     GET_FILE,
     STOP_WORK,
     CONTINUE_WORK]
)
                | F.content_type.in_(
    [ContentType.PHOTO,
     ContentType.STICKER,
     ContentType.VIDEO]
))
async def handle_other_content(message: Message):
    await message.answer('Прошу, следуйте инструкциям!')


@router.message(F.text == GET_TEXT)
async def send_text_in_message(message: Message):
    user_id = message.from_user.id
    file_path = f'{user_id}_file.pdf'
    if path.exists(file_path):
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(f'{user_id}_file')
    try:
        await message.answer(text)
        await message.answer(
            'Работа с этим файлом завершена?',
            reply_markup=yes_no_kb()
        )
    except TelegramBadRequest:
        await message.answer('Ого, так много текста!'
                             ' У меня не получается отправить '
                             'вам текст одним сообщением. '
                             'Отправляю файл!')
        await send_text_in_file(message)


@router.message(F.text == GET_FILE)
async def send_text_in_file(message: Message):
    user_id = message.from_user.id
    file_path = f'{user_id}_extracted_text.txt'
    if not path.exists(file_path):
        file_path = f'{user_id}_file.pdf'
        if path.exists(file_path):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_image(f'{user_id}_file')

        with open(file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

    input_file = FSInputFile(file_path)
    await message.answer_document(
        input_file,
        caption='Вот ваш текст из отправленного файла.'
    )
    await message.answer(
        'Работа с этим файлом завершена?',
        reply_markup=yes_no_kb()
    )


@router.message(F.text == STOP_WORK)
async def delete_users_file(message: Message):
    user_id = message.from_user.id
    file_path = f'{user_id}_extracted_text.txt'
    if path.exists(file_path):
        os.remove(file_path)

    file_path = f'{user_id}_file.pdf'
    os.remove(file_path)

    await message.answer(
        'Для продолжения работы загрузите новый файл',
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text == CONTINUE_WORK)
async def continue_work(message: Message):
    await message.answer(
        'Как вы хотите получить текст?',
        reply_markup=get_answers_kb()
    )
