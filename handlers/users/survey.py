from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.inline.city_show import city_keyboard, date_in, city
from loader import dp


@dp.message_handler(Command('menu'))
async def show_city(message: types.Message):
    await list_city(message)


async def list_city(message: Union[CallbackQuery, Message], **kwargs):
    markup = await city_keyboard()

    if isinstance(message, Message):
        await message.answer("Уточните пожалуйста", reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)


async def date_input(callback: CallbackQuery, id, **kwargs):
    markup = await date_in(id)

    await callback.message.edit_reply_markup(markup)


@dp.callback_query_handler(city.filter())
async def navigate(call: CallbackQuery, callback_data: dict):
    """
    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    :param callback_data: Словарь с данными, которые хранятся в нажатой кнопке
    """
    current_level = callback_data.get("level")
    id = callback_data.get("id")
    levels = {
        "0": list_city,  # Отдаем города
        "1": date_input  # дата въезда
    }
    current_level_function = levels[current_level]

    # Выполняем нужную функцию и передаем туда параметры, полученные из кнопки
    await current_level_function(
        call,
        id=id,
        date_in=date_in
    )
