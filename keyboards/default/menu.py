from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton('Поиск по возрастанию цены'),
     KeyboardButton('Поиск по убыванию цены')],
    [KeyboardButton('Поиск по точным параметрам'),
     KeyboardButton('Помощь')],
    [KeyboardButton('История'),
     KeyboardButton('Погода')]], resize_keyboard=True)
