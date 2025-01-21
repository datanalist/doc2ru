import os
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from keyboards.buttons import language_keyboard, cancel_keyboard, post_file_keyboard, model_keyboard
from aiogram import F

from settings import get_settings
from lib import *


choosen_model = ''

# Хэндлер для запуска бота (команда /start)
async def start_bot(message: Message):
    text = '''
        дравствуйте! Я Ваш умный помощник по переводу презентаций на русский язык! Пожалуйста, выберите провайдера с моделью:
        '''
    await message.answer(text=text, reply_markup=model_keyboard)

async def handle_model_selection(message: Message): 
    choosen_model = message.text
    set_model(choosen_model)  
    await message.answer(f'Вы выбрали модель {choosen_model.lower()}. Теперь выберите язык для перевода:',
                         reply_markup=ReplyKeyboardRemove()) 

    await message.answer('Пожалуйста, выберите язык оригинала презентации:',
                         reply_markup=language_keyboard) 


# Хэндер для остановки бота (команда /stop)
async def stop_bot(message: Message):
    await message.answer(
        'Работа завершена, спасибо! Если понадоблюсь вам ещё - отправляйте команду /start!',
        reply_markup=ReplyKeyboardRemove()
    )

# Хэндлер для кнопки 'Выбрать другой язык презентации'
async def change_language(message: Message):
    await message.answer(
        'Пожалуйста, выберите язык оригинала презентации:',
        reply_markup=language_keyboard
    )

# Хэндлер для обработки выбора языка
async def handle_language_selection(message: Message):
    chosen_language = message.text
    await message.answer(f'Вы выбрали {chosen_language.lower()} язык. Пожалуйста, прикрепите pdf-файл для перевода:',
                         reply_markup=cancel_keyboard)

# Хэндлер для кнопки 'Загрузить ещё"
async def upload_another_file(message: Message):
    await message.answer(f'Пожалуйста, прикрепите pdf-файл для перевода:',
                         reply_markup=cancel_keyboard)

# Хэндлер для отмены выбора языка
async def cancel_selection(message: Message):
    await message.answer(
        'Выбор языка отменен. Пожалуйста, выберите язык оригинала презентации снова:',
        reply_markup=language_keyboard
    )

# Хэндлер для обработки PDF-файла
async def handle_pdf(message: Message, bot: Bot):
    document = message.document

    if document.mime_type == 'application/pdf':
        file_id = document.file_id
        file = await bot.get_file(file_id)

        pdf_path = f'./{document.file_name}'
        await bot.download_file(file.file_path, pdf_path)
        await message.answer('Файл получен! Начинаю обработку, пожалуйста, подождите.',
                             reply_markup=ReplyKeyboardRemove())
        #  Извлекаем метаданные
        pdf_metadata = extract_metadata_pymupdf(pdf_path)
        
        translated_dict = await translate_structured(pdf_info=pdf_metadata)
        # Перевод и переприсваивание переведенного текста
        translated_meatadata = fill_translated_meatadata(original_meta=pdf_metadata,
                          translated_dict=translated_dict)

        # Создаем переведенный pdf
        pdf_path_new = create_pdf_pymupdf(pdf_info=translated_meatadata, path_to="Translated_document.pdf")
        pdf_path_new = os.path.abspath(pdf_path_new)
        pdf_file = FSInputFile(pdf_path_new)

        await message.answer('Файл переведённой презентации готов, теперь вы можете его скачать:')
        await message.answer_document(document=pdf_file)

        os.remove(pdf_path)
        os.remove(pdf_path_new)

        await message.answer('Что вы хотите сделать дальше?', reply_markup=post_file_keyboard)

    else:
        await message.answer('Пожалуйста, убедитесь в том, что отправляете файл в формате pdf и повторите попытку!',
                             reply_markup=ReplyKeyboardRemove())


async def main():
    api_token = load_env("API_TOKEN_BOT")
    settings = get_settings(api_token)
    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()
    out_model = 'gpt-4o-mini'
    dp.message.register(start_bot, Command('start'))
    dp.message.register(handle_model_selection, F.text.in_(['local', out_model]))
    dp.message.register(handle_language_selection, F.text.in_(['Английский', 'Французский', 'Испанский']))
    dp.message.register(cancel_selection, F.text == 'Отменить выбор языка')
    dp.message.register(handle_pdf, F.document)
    dp.message.register(stop_bot, Command('stop'))
    dp.message.register(stop_bot, F.text == 'Остановить бота')
    dp.message.register(stop_bot, F.text == 'Завершить работу')
    dp.message.register(upload_another_file, F.text == 'Загрузить ещё одну презентацию')
    dp.message.register(change_language, F.text == 'Выбрать другой язык презентации')

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # set_env_file() # Инициализируем переменные среды
    asyncio.run(main())