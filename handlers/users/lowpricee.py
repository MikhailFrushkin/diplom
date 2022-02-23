from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp


@dp.message_handler(Command('lowprice'))
async def bot_start(message: types.Message):
    await message.answer('Вы выбрали поиск по увеличению ценны\n'
                         'введите название города')
