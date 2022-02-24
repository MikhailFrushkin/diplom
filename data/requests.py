import re
import typing

import aiohttp.client
from loguru import logger

from data import config


async def get_city_id(city_name: str, locale: str) -> int:
    """
    Запрашивает данные по полученному от пользователя городу, и получает id города для поиска отелей.
    :param city_name: Название города для поиска
    :param locale: Локаль для запроса
    :return: Id города
    """
    url = '{}/locations/search'.format(config.BASE_URL)
    params = [('query', city_name), ('locale', str(locale))]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=config.headers, params=params) as resp:
                logger.info('Отправляю запрос на сервер {}'.format(resp.url))
                response = await resp.json()
                logger.info('Получил ответ:'.format(
                    response.get('suggestions')[0].get('entities')[0].get('destinationId')))
                city_id = response.get('suggestions')[0].get('entities')[0].get('destinationId')
                print(city_id)
                if city_id:
                    return city_id
                return False
    except Exception as err:
        logger.error(err)


