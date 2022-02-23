from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp


@dp.message_handler(Command('lowprice'))
async def lowprice(message: types.Message):
    await message.answer('Вы выбрали поиск по увеличению цены\n'
                         'введите название города')

