# from aiogram_calendar import simple_cal_callback, SimpleCalendar
from datetime import datetime, date

from telegram_bot_calendar import DetailedTelegramCalendar
from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger
import re

from data.requests import get_city_id
from data import config

from loader import dp, bot
from states.anyprice import Anyprice
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
    logger.info('Сохраняю ответ в state: city')
    async with state.proxy() as data:
        data['city'] = answer
        data['city_id'] = city_id
        data['locale'] = locale
        data['currency'] = currency

    await message.answer('Сколько отелей показать? (Максимально: {})'.format(config.MAX_HOTELS_TO_SHOW))
    logger.info('Сохраняю ответ в state: hotel_amount')
    await Anyprice.next()


@dp.message_handler(state=Anyprice.hotel_amount)
async def answer_hotel_amount(message: types.Message, state: FSMContext):
    """
       Получает ответ из answer_city хэндлера, сохраняет в кэш, спрашивает следующий вопрос,
       сохраняет в state следующего вопроса.

       :param message: входящее сообщение из state
       :param state: Переданный контекст
       :return: None
       """
    answer = message.text
    pattern = re.search(r'\D', answer)
    if pattern:
        await message.answer('Введите цифрами')
    logger.info('Получил ответ: {}. Сохраняю в state'.format(answer))
    logger.info('Сохраняю ответ в state: hotel_amount')
    async with state.proxy() as data:
        data['hotels_amount'] = int(answer)

    await message.answer('Выберите дату заезда')
    logger.info('Вызываю Календарь заезда')
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
    calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).build()
    await message.answer('Выберите {}'.format(LSTEP[step]), reply_markup=calendar)

    await Anyprice.next()


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=Anyprice.check_in_date)
async def inline_kb_answer_callback_handler(call: types.CallbackQuery, state: FSMContext):
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).process(call.data)

    if not result and key:
        await bot.edit_message_text('Выберите {}'.format(LSTEP[step]),
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=key)
    elif result:

        await bot.edit_message_text('Вы выбрали {}'.format(result),
                                    call.message.chat.id,
                                    call.message.message_id)
        logger.info('Получили дату заезда: - {}'.format(result))
        async with state.proxy() as data:
            data['check_in'] = result
            logger.info('Сохраняю ответ в state: check_in_date')
        await call.message.answer('Выберите дату выезда')
        logger.info('Вызываю Календарь выезда')
        calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).build()
        await call.message.answer('Выберите {}'.format(LSTEP[step]), reply_markup=calendar)
        await Anyprice.next()


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=Anyprice.check_out_date)
async def inline_kb_answer_callback_handler(call: types.CallbackQuery, state: FSMContext):
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).process(call.data)

    if not result and key:
        await bot.edit_message_text('Выберите {}'.format(LSTEP[step]),
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=key)
    elif result:

        await bot.edit_message_text('Вы выбрали {}'.format(result),
                                    call.message.chat.id,
                                    call.message.message_id)
        logger.info('Получили дату выезда: - {}'.format(result))
        async with state.proxy() as data:
            data['check_out'] = result
            logger.info('Сохраняю ответ в state: check_out_date')
        logger.info('Спрашиваем сколько фото показать.')
        await call.message.answer('Сколько фотографий показать? ')
        await Anyprice.next()

