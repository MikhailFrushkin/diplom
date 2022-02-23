from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loguru import logger

city = CallbackData('show_city', 'level', 'id', 'date_in', 'date_out')


# buy_item = CallbackData('buy', 'item_id')


def make_callback_data(level, id='0', date_in='0', date_out='0'):
    return city.new(level=level, id=id, date_in=date_in, date_out=date_out)


async def city_keyboard():
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup()
    data = {
        'Москва, Россия': '1153093',
        'Центр Москвы, Москва, Россия': '10565407',
        'Измайлово, Москва, Россия': '10779356',
        'Арбат, Москва, Россия': '1665959',
        'Сокольники, Москва, Россия': '1786031'
    }
    for key, value in data.items():
        button_text = '{}'.format(key)
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, id=value)
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    logger.info(markup)
    return markup


async def date_in(id):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup()
    button_text = 'Дата заезда'

    callback_data = make_callback_data(level=CURRENT_LEVEL + 1,
                                       id=id, date_in='2')
    markup.insert(
        InlineKeyboardButton(text=button_text, callback_data=callback_data)
    )
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=make_callback_data(level=CURRENT_LEVEL - 1))
    )
    return markup
