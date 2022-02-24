from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default import menu
from loader import dp
from utils.db_api.base import Users


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer('Добро пожаловать, {}!'
                         '\nЯ бот - HotelsOnTheTrip'
                         '\nИ я помогу, подобрать отель на время поездки.'
                         '\nДля вызова справки введите /help'.format(message.from_user.first_name))
    await message.answer('Выберите действие', reply_markup=menu)
    # user_data = [{'nuser_id': message.from_user.id}, {'first_name': message.from_user.first_name},
    #              {'first_name': message.from_user.first_name}, {'last_name': message.from_user.last_name},
    #              {'user_name': message.from_user.username}]
    # Users.insert_many(user_data).execute()
