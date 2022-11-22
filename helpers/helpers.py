from time import sleep
from datetime import datetime, timedelta

import logging


def sleep_until(timestamp: float):
    """
    Sleep until provided timestamp
    :param timestamp: timestamp (float)
    :return: None
    """
    logging.warning("api rate limit reached!")
    time_now = datetime.now()
    ts = datetime.fromtimestamp(timestamp)
    delta = ts - time_now
    if delta > timedelta(0):
        sleep(delta.total_seconds())
        return True
