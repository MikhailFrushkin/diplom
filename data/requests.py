import json
import re
import typing

import aiohttp.client
from loguru import logger


from data import config


async def delete_spans(data: str):
    """Удаление спец.символов HTML"""
    result = re.compile(r'<.*?>')
    return result.sub('', data)


async def get_city_id(city_name: str, locale: str):
    """
    Запрашивает данные по полученному от пользователя городу, и получает id города для поиска отелей.
    :param city_name: Название города для поиска
    :param locale: Локаль для запроса
    :return: Id города
    """
    url = '{}/locations/search'.format(config.BASE_URL)
    params = {'query': city_name, 'locale': str(locale)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=config.headers, params=params) as resp:
                logger.info(f'Отправляю запрос на сервер {resp.url}')
                response = await resp.json()
                logger.info('Получил ответ {}'.format(
                    response.get("suggestions")[0].get("entities")[0].get("destinationId")))
                city_id = response.get('suggestions')[0].get('entities')[0].get('destinationId')
                if city_id:
                    return city_id
                return False
    except Exception as err:
        logger.error(err)


async def get_hotels(city_id: int, hotels_amount: int, currency: str, locale: str, check_in: str,
                     check_out: str, adults_qnt: int, price_sort: str) -> typing.Optional[list]:
    """
    Запрашивает отели в id города
    :param price_sort:
    :param check_out:
    :param adults_qnt:
    :param check_in:
    :param hotels_amount: Количество городов
    :param city_id: id города
    :param currency: Код валюты
    :param locale: Код страны
    :return: Список отелей
    """

    url = '{}/properties/list'.format(config.BASE_URL)
    params = [("destinationId", city_id), ("pageNumber", 1), ("pageSize", hotels_amount), ("checkIn", check_in),
              ("checkOut", check_out), ("adults1", adults_qnt), ("sortOrder", price_sort),
              ("locale", locale), ("currency", currency)]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=config.headers, params=params) as resp:
                logger.info(f'Отправляю запрос на сервер {resp.url}')
                response = await resp.json()
                hotels = response.get('data').get('body').get('searchResults').get('results')
                if hotels:
                    return hotels
                logger.error('Гостиниц по вашему запросу не найдено!')
                return None
    except Exception as err:
        logger.error(err)


async def get_photos(hotel_id: int, hotels_amount: int) -> list:
    """
    Запрашивает фотографии по id отеля
    :param hotels_amount:
    :param hotel_id:
    :return:
    """
    url = '{}/properties/get-hotel-photos'.format(config.BASE_URL)
    params = [('id', hotel_id)]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=config.headers, params=params) as resp:
                logger.info(f'Отправляю запрос на сервер {resp.url}')
                response = await resp.json()
                photo_list = response.get('hotelImages')[:hotels_amount]
                photo_list_url = [re.sub(pattern=r'{size}', repl='y', string=hotel.get("baseUrl")) for hotel in
                                  photo_list]
                return photo_list_url

    except Exception as err:
        logger.error(err)

