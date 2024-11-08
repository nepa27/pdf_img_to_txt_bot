import io
import re

import fitz
from PIL import Image, ImageFilter
import pytesseract
import asyncio
from concurrent.futures import ThreadPoolExecutor

from constants import PATH_TESSERACT


pytesseract.pytesseract.tesseract_cmd = PATH_TESSERACT


async def clean_text(text):
    """Удаляет переносы слов из текста."""
    cleaned_text = re.sub(r'(\w+)-\s*(\w+)', r'\1\2', text)
    return cleaned_text


def extract_text(image):
    """Извлекает текст из изображения."""
    return pytesseract.image_to_string(
        image, lang='rus+eng',
        config='--psm 3'
    )


async def extract_text_from_images(
        page,
        user_id,
        bot,
        total_pages,
        page_number,
        progress_message_id=None
):
    """Извлекает текст из изображений на странице."""
    images = page.get_images(full=True)
    extracted_text = ''

    for img_index, img in enumerate(images):
        xref = img[0]
        base_image = fitz.Pixmap(page.parent, xref)

        # Проверяем, является ли изображение цветным или черно-белым
        if base_image.n < 5:  # Если изображение не имеет альфа-канала
            image_bytes = base_image.tobytes()  # Получаем байты изображения
        else:
            # Если изображение имеет альфа-канал, конвертируем его в RGB
            image_rgb = fitz.Pixmap(fitz.csRGB, base_image)
            image_bytes = image_rgb.tobytes()

        image = Image.open(io.BytesIO(image_bytes))
        image = image.filter(ImageFilter.SHARPEN)

        # Запускаем извлечение текста в отдельном потоке
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            text = await loop.run_in_executor(pool, extract_text, image)

        cleaned_text = await clean_text(text)
        extracted_text += cleaned_text + '\n'

    # Удаляем предыдущее сообщение, если оно существует
    if progress_message_id is not None:
        try:
            await bot.delete_message(
                chat_id=user_id,
                message_id=progress_message_id
            )
        except Exception as e:
            logger.error(f'Не удалось удалить сообщение: {e}')

    progress_message = (f'Обработано {page_number + 1} '
                        f'из {total_pages} изображений.')
    new_progress_message = await bot.send_message(
        chat_id=user_id,
        text=progress_message
    )

    return extracted_text.strip(), new_progress_message.message_id


async def extract_text_from_pdf(pdf_path, user_id, bot) -> str:
    """Извлекает текст из PDF, проверяя, есть ли текст или изображения."""
    pdf_document = fitz.open(pdf_path)
    extracted_text = ''
    total_pages = pdf_document.page_count
    progress_message_id = None

    for page_number in range(total_pages):
        page = pdf_document.load_page(page_number)

        text = page.get_text()
        if text.strip():
            extracted_text += text + '\n'
        else:
            (extracted_text_part,
             progress_message_id) = await extract_text_from_images(
                page,
                user_id,
                bot,
                total_pages,
                page_number,
                progress_message_id
            )
            extracted_text += extracted_text_part + '\n'

    pdf_document.close()
    return extracted_text.strip()
