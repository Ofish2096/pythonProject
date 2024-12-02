import datetime
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def write_info_line(message):
    logger.info(f"{datetime.datetime.now()} :{message}")

def write_error_line(message):
    logger.error(f"{datetime.datetime.now()} :{message}")
