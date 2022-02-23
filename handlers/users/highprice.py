from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp


@dp.message_handler(Command('highprice'))
async def highprice(message: types.Message):
    await message.answer('Вы выбрали поиск по уменьшению цены\n'
                         'введите название города')
