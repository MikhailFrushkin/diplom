from loguru import logger
from aiogram.utils.exceptions import (TelegramAPIError,
                                      MessageNotModified,
                                      CantParseEntities)


from loader import dp


@dp.errors_handler()
async def errors_handler(update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param update:
    :param exception:
    """

    if isinstance(exception, MessageNotModified):
        logger.exception('Message is not modified')
        # do something here?
        return True
      
    if isinstance(exception, CantParseEntities):
        # or here
        logger.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logger.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    
    logger.exception(f'Update: {update} \n{exception}')
