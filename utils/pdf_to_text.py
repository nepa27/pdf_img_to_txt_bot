import io
import re

import fitz
from PIL import Image, ImageFilter
import pytesseract

from constants import PATH_TESSERACT


pytesseract.pytesseract.tesseract_cmd = PATH_TESSERACT

async def clean_text(text):
    """Удаляет переносы слов из текста."""
    cleaned_text = re.sub(r'(\w+)-\s*(\w+)', r'\1\2', text)
    return cleaned_text

async def extract_text_from_pdf(pdf_path) -> str:
    """Извлекает текст из PDF, проверяя, есть ли текст или изображения."""
    pdf_document = fitz.open(pdf_path)
    extracted_text = ''

    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)

        text = page.get_text()
        if text.strip():
            extracted_text += text + '\n'
        else:
            extracted_text += await extract_text_from_images(page) + '\n'

    pdf_document.close()
    return extracted_text.strip()


async def extract_text_from_images(page):
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
        text = pytesseract.image_to_string(
            image, lang='rus+eng',
            config='--psm 3'
        )
        cleaned_text = await clean_text(text)
        extracted_text += cleaned_text + '\n'

    return extracted_text.strip()
