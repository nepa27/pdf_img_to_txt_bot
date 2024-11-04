import io
from PIL import Image, ImageFilter
import re

import fitz
import pytesseract

from constants import PATH_TESSERACT


def extract_text_from_image(data):
    """Извлекает текст из изображения."""
    extracted_text = ''

    for img in data:
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
        text = pytesseract.image_to_string(
            image, lang='rus+eng',
            config='--psm 3'
        )
        cleaned_text = clean_text(text)
        extracted_text += cleaned_text + '\n'

    return extracted_text.strip()
