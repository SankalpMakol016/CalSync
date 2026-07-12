import sys

import mysql.connector

from config.config import Config
from exception.exception import CalSyncException
from logger.logger import logger


# ── DB CONNECTION ─────────────────────────────────────────────
def get_db():
    try:
        return mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
        )

    except Exception as e:
        logger.error(e)
        raise CalSyncException(e, sys)
