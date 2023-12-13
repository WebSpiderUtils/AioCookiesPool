import os
from loguru import logger
from os.path import join
from aiocookiespool.config import LOG_DIR


if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

rotation = '1 week'
encoding = 'utf-8'
compression = 'zip'
retention = '7 days'
logger.add(
    join(LOG_DIR, 'info.log'), level='INFO', rotation=rotation, encoding=encoding,
    enqueue=True, compression=compression, retention=retention
)
logger.add(
    join(LOG_DIR, 'error.log'), level='ERROR', rotation=rotation, encoding=encoding,
    enqueue=True, compression=compression, retention=retention
)
logger.add(
    join(LOG_DIR, 'warning.log'), level='WARNING', rotation=rotation, encoding=encoding,
    enqueue=True, compression=compression, retention=retention
)
logger.add(
    join(LOG_DIR, 'success.log'), level='SUCCESS', rotation=rotation, encoding=encoding,
    enqueue=True, compression=compression, retention=retention
)
