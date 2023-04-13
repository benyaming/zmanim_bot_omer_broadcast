import time
from datetime import datetime

import betterlogging as bl

from broadcast.config import JOB_PERIOD
from broadcast.job import set_time_for_today, check_time
from broadcast.file_logger import init_logger


RESET_HOUR = 0
RESET_MINUTE = 1


bl.basic_colorized_config(level=bl.INFO)
logger = bl.getLogger(__name__)


def safe_set_time(should_reset: bool = True):
    init_logger()
    try:
        set_time_for_today(should_reset)
    except Exception as e:
        bl.exception(e)


def run_infinite_check():
    logger.info('Starting checker thread...')

    while True:
        now = datetime.now()

        if now.hour == RESET_HOUR and now.minute == RESET_MINUTE:
            logger.info('Initializing reset...')
            safe_set_time()
            time.sleep(60)

        logger.info('Begin check...')
        start = time.time()

        try:
            check_time()
        except Exception as e:
            bl.exception(e)

        logger.info(f'Check done for {int(time.time() - start)}s')
        time.sleep(JOB_PERIOD)


if __name__ == '__main__':
    safe_set_time(should_reset=False)

    logger.info('Starting worker...')

    run_infinite_check()


