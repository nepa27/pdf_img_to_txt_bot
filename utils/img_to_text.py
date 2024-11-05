import io
from PIL import Image, ImageFilter

import pytesseract

from constants import PATH_TESSERACT
from .pdf_to_text import clean_text


async def extract_text_from_image(file):
    """Извлекает текст из изображения."""
    extracted_text = ''

    image = Image.open(file)

    # Применяем фильтр для улучшения качества изображения
    image = image.filter(ImageFilter.SHARPEN)

    text = pytesseract.image_to_string(
        image, lang='rus+eng',
        config='--psm 3'
    )

    cleaned_text = await clean_text(text)
    extracted_text += cleaned_text + '\n'

    return extracted_text.strip()
