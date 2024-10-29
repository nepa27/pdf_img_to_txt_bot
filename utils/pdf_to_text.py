import io
from PIL import Image, ImageFilter
import re

import fitz
import pytesseract

from constants import PATH_TESSERACT


pytesseract.pytesseract.tesseract_cmd = PATH_TESSERACT

def clean_text(text):
    """Удаляет переносы слов из текста."""
    cleaned_text = re.sub(r'(\w+)-\s*(\w+)', r'\1\2', text)
    # cleaned_text = re.sub(r'(\w+)\s*\n\s*(\w+)', r'\1\2', cleaned_text)
    return cleaned_text

def extract_text_from_pdf(pdf_path):
    """Извлекает текст из PDF, проверяя, есть ли текст или изображения."""
    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)

        text = page.get_text()
        if text.strip():
            print(f'Текст на странице {page_number + 1}:\n{text}\n')
        else:
            print(f'На странице {page_number + 1} нет текста.'
                  f' Пытаемся извлечь текст из изображений.')
            extract_text_from_images(page, page_number)

    pdf_document.close()


def extract_text_from_images(page, page_number):
    """Извлекает текст из изображений на странице."""
    images = page.get_images(full=True)

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
        cleaned_text = clean_text(text)

        with open(
                f"extracted_text_page_{page_number + 1}"
                f"_img_{img_index + 1}.txt", "w", encoding="utf-8"
        ) as text_file:
            text_file.write(cleaned_text)
            print(
                f"Изображение {img_index + 1} на странице "
                f"{page_number + 1} обработано. Текст сохранен."
                )

if __name__ == '__main__':
    pdf_path = '2.pdf'
    extract_text_from_pdf(pdf_path)