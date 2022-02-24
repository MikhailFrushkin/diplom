from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger
import re

from data.requests import get_city_id
from data import config
from loader import dp
from states.anyprice import Anyprice
from utils.db_api.base import *
from utils.chek_local import locale_check


@dp.message_handler(commands=['lowprice', 'highprice'], state='*')
async def get_any_price(message: types.Message, state: FSMContext):
    """
    По нажатию на команду /lowprice или /highprice запускает серию хендлеров для уточнения информации
    Сохраняет ответы в states.Anyprice
    :param state: Данные из контекста
    :param message: Входящее сообщение
    """
    logger.info('Пользователь {}: {} запросил команду /lowprice или  /highprice'.format(
        message.from_user.id,
        message.from_user.username))
    await message.answer('Напишите город, где хотите подобрать отель.')
    logger.info('Сохраняю ответ в state: city')

    async with state.proxy() as data:
        data['command'] = message.get_command()
        data['message_id'] = message.message_id

        if message.get_command() == '/lowprice':
            data['price_sort'] = 'PRICE'
        elif message.get_command() == '/highprice':
            data['price_sort'] = 'PRICE_HIGHEST_FIRST'

    await Anyprice.city.set()


@dp.message_handler(state=Anyprice.city)
async def answer_city(message: types.Message, state: FSMContext):
    """
    Получает ответ из get_any_price хэндлера, сохраняет в кэш, спрашивает следующий вопрос,
    сохраняет в state следующего вопроса.
    :param message: входящее сообщение из state
    :param state: Переданный контекст
    """
    answer = message.text.lower()

    locale = config.locales[locale_check(answer)].get('locale')
    currency = config.locales[locale_check(answer)].get('currency')
    logger.info('Получил ответ: {}. Сохраняю в state'.format(answer))

    city_id = await get_city_id(answer, locale)

    async with state.proxy() as data:
        data['city'] = answer
        data['city_id'] = city_id
        data['locale'] = locale
        data['currency'] = currency

    await message.answer(f'Сколько отелей показать? (Max: {config.MAX_HOTELS_TO_SHOW})')
    logger.info('Сохраняю ответ в state: hotel_amount')
    await Anyprice.next()
