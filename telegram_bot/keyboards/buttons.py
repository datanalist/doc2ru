from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

language_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Английский')],
    [KeyboardButton(text='Французский')],
    [KeyboardButton(text='Испанский')],
    [KeyboardButton(text='Остановить бота')]

], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите язык')

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отменить выбор языка')],
        [KeyboardButton(text='Остановить бота')]
    ],
    resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите кнопку')

post_file_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Завершить работу')],
        [KeyboardButton(text='Загрузить ещё одну презентацию')],
        [KeyboardButton(text='Выбрать другой язык презентации')]
    ],
    resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите кнопку')

model_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='local')],
        [KeyboardButton(text='gpt-4o-mini')]
    ],
    resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите кнопку')
