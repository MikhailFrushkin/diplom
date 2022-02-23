from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = '● /help — помощь по командам бота\n' \
           '● /lowprice — вывод самых дешёвых отелей в городе\n' \
           '● /highprice — вывод самых дорогих отелей в городе\n' \
           '● /bestdeal — вывод отелей, наиболее подходящих' \
           'по цене и расположению от центра.\n' \
           '● /history — вывод истории поиска отелей'
    await message.answer(text)
