# Телеграмм-бот для получения текста из pdf-файлов и изображений
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
## Описание
Бот, который извлекает текст из из pdf-файлов и изображений.
## Основные особенности
- Возможность получения извлеченного текста в ответном сообщении;
- Возможность получения извлеченного текста в файле.
## Стек использованных технологий
+ Python 3.11
+ aiogram
+ asynco

## Запуск проекта
1. Клонируйте репозиторий на ваш локальном компьютере:

```
git clone https://github.com/nepa27/pdf_img_to_txt_bot
cd pdf_img_to_txt_bot
```
   
2. Установите и активируйте виртуальное окружение c учетом версии Python 3.11:
* Если у вас Linux/macOS

```
python3 -m venv env
source env/bin/activate
```

* Если у вас Windows

```
python -m venv venv
source venv/Scripts/activate
```

+ Обновите менеджер пакетов pip:

```
python -m pip install --upgrade pip
```
+ Установите tesseract, который позволяет извлекать текст из изображений
```
sudo apt install tesseract-ocr

sudo apt install tesseract-ocr-rus
```
+ Затем установите зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

+ Запускаем скрипт командой:

```
python main.py
```
3. Для правильной работы бота создайте TELEGRAM_TOKEN в файле .env:

```
TELEGRAM_TOKEN       # токен телеграмм-бота
```
4. Модуль tesseract поддерживает множество языков.
```
Русский: rus
Английский: eng
Немецкий: deu
Французский: fra
Испанский: spa
Итальянский: ita
Португальский: por
Китайский (упрощенный): chi_sim
Китайский (традиционный): chi_tra
Японский: jpn
Корейский: kor
Украинский: ukr
Белорусский: bel
```
   в файле pdf_to_text в 56 строке жестко прописан используемый язык
```
image, lang='rus+eng'
```
   Вы можете сделать изменения по своему усмотрению. 

## Автор
+ [Александр Непочатых](https://github.com/nepa27)

