from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer('Добро пожаловать, {}!'
                         '\nЯ бот - HotelsOnTheTrip'
                         '\nИ я помогу, подобрать отель на время поездки.'
                         '\nДля вызова справки введите /help'.format(message.from_user.full_name))
