import io

from PIL import Image, ImageFilter
import pytesseract
import asyncio
from concurrent.futures import ThreadPoolExecutor

from constants import PATH_TESSERACT
from main import logger
from .pdf_to_text import clean_text


def extract_text(image):
    """Извлекает текст из изображения."""
    return pytesseract.image_to_string(
        image, lang='rus+eng',
        config='--psm 3'
    )


# Асинхронная функция для обработки изображения
async def extract_text_from_image(file):
    """Извлекает текст из изображения асинхронно."""
    extracted_text = ''

    # Открываем изображение
    image = Image.open(file)

    # Применяем фильтр для улучшения качества изображения
    image = image.filter(ImageFilter.SHARPEN)

    # Запускаем извлечение текста в отдельном потоке
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        text = await loop.run_in_executor(pool, extract_text, image)

    # Очищаем текст
    cleaned_text = await clean_text(text)
    extracted_text += cleaned_text + '\n'

    return extracted_text.strip()
