from loguru import logger

logger.add('logs/logs.log', level='DEBUG')
logger.debug('Error')
logger.info('Information message')
logger.warning('Warning')
