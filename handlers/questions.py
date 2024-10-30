from os import path

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, ContentType, FSInputFile

from keybords.for_questions import get_answers_kb
from utils.pdf_to_text import extract_text_from_pdf

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Отправьте файл pdf, из которого нужно извлечь текст.\n'
        'Для перезапуска бота нажмите /stop, затем /start',
        reply_markup=None
    )


@router.message(Command('stop'))
async def stop_conversation(message: Message):
    await message.answer(
        'Бот остановлен. Нажмите /start, чтобы продолжить',
        reply_markup=None
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
    else:
        await message.answer('Пожалуйста, отправьте PDF-файл.')


@router.message(F.text & ~F.text.in_(
    ['Получить текст в сообщении', 'Получить текст в файле']
)
                | F.content_type.in_(
    [ContentType.PHOTO,
     ContentType.STICKER,
     ContentType.VIDEO]
))
async def handle_other_content(message: Message):
    await message.answer('Прошу, следуйте инструкциям!')


@router.message(F.text == 'Получить текст в сообщении')
async def send_text_in_message(message: Message):
    user_id = message.from_user.id
    text = extract_text_from_pdf(f'{user_id}_file.pdf')
    try:
        await message.answer(text)
        await message.answer(
            'Если хотите обработать новый документ, то загрузите его.'
        )
    except TelegramBadRequest:
        await message.answer('Ого, так много текста!'
                             ' У меня не получается отправить '
                             'вам текст одним сообщением. '
                             'Отправляю файл!')
        await send_text_in_file(message)


@router.message(F.text == 'Получить текст в файле')
async def send_text_in_file(message: Message):
    user_id = message.from_user.id
    file_path = f"{user_id}_extracted_text.txt"
    if not path.exists(file_path):
        text = extract_text_from_pdf(f'{user_id}_file.pdf')

        with open(file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

    input_file = FSInputFile(file_path)
    await message.answer_document(
        input_file,
        caption='Вот ваш текст из PDF.'
    )
    await message.answer(
        'Если хотите обработать новый документ, то загрузите его.'
    )
