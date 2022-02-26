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
    logger.info(f'Получил ответ: {answer}. Сохраняю в state')

    async with state.proxy() as data:
        data['hotels_amount'] = int(answer)

    await message.answer('Выберите дату заезда')
    await start(message)

    logger.info('Сохраняю ответ в state: hotel_amount')
    await Anyprice.next()


@dp.message_handler(commands=['calendar'], state='*')
async def start(message):
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
    calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).build()
    await message.answer(f"Выберите {LSTEP[step]}", reply_markup=calendar)


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state='*')
async def inline_kb_answer_callback_handler(call: types.CallbackQuery, state: FSMContext):
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).process(call.data)

    if not result and key:
        await bot.edit_message_text(f"Select {LSTEP[step]}",
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=key)
    elif result:

        await bot.edit_message_text(f"Вы выбрали {result}",
                                    call.message.chat.id,
                                    call.message.message_id)
        print(result)

        await Anyprice.next()


# @dp.callback_query_handler(simple_cal_callback.filter(), state=Anyprice.check_in_date)
# async def answer_check_in(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
#     """
#     Получает ответ из хэндлера о дате заезда и сохраняет в state
#     :param callback_data:
#     :param call: входящее сообщение из state
#     :param state: Переданный контекст
#     :return:
#     """
#
#     logger.info('Вызываю Календарь...')
#     selected, date = await SimpleCalendar().process_selection(call, callback_data)
#     if selected:
#         check_in_date = date.strftime("%Y-%m-%d")
#         logger.info(f'Получили дату заселения: - {check_in_date}')
#
#         logger.info('Отвечаем пользователю.')
#         await call.message.answer(f'You selected {check_in_date}')
#         logger.info(f'Добавляем {check_in_date} в state')
#
#         async with state.proxy() as data:
#             data['check_in'] = check_in_date
#
#         logger.info('Спрашиваем у пользователя дату выезда!')
#         await call.message.answer('Выберите дату выезда:', reply_markup=await SimpleCalendar().start_calendar())
#
#         await Anyprice.next()
#
#
# @dp.callback_query_handler(simple_cal_callback.filter(), state=Anyprice.check_out_date)
# async def answer_check_out(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
#     """
#     Получает ответ из хэндлера о дате выезда и сохраняет в state
#     :param callback_data:
#     :param call: входящее сообщение из state
#     :param state: Переданный контекст
#     :return:
#     """
#     logger.info('Вызываю Календарь...')
#     selected, date = await SimpleCalendar().process_selection(call, callback_data)
#     if selected:
#         check_out_date = date.strftime("%Y-%m-%d")
#         logger.info(f'Получили дату выезда: - {check_out_date}')
#
#         logger.info('Отвечаем пользователю.')
#         await call.message.answer(f'You selected {check_out_date}')
#         logger.info(f'Добавляем {check_out_date} в state')
#
#         async with state.proxy() as data:
#             data['check_out'] = check_out_date
#
#         logger.info('Спрашиваем сколько фото показать.')
#         await call.message.answer('Сколько фотографий показать? ')
#         logger.info('Сохраняю ответ в state: adult_qnt')
#         await Anyprice.next()

