from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp


@dp.message_handler(Command('history'))
async def bot_start(message: types.Message):
    await message.answer('История запросов:')
