import time

import betterlogging as bl


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from broadcast.config import JOB_PERIOD
from broadcast.job import set_time_for_today, check_time
from broadcast.file_logger import init_logger


bl.basic_colorized_config(level=bl.INFO)
logger = bl.getLogger(__name__)


def safe_set_time(should_reset: bool = True):
    init_logger()
    try:
        set_time_for_today(should_reset)
    except Exception as e:
        bl.exception(e)


scheduler = BackgroundScheduler()
daily_trigger = CronTrigger(day='*', hour=0, minute=1)
scheduler.add_job(safe_set_time, trigger=daily_trigger)


def infinite_check():
    logger.info('Starting checker thread...')

    while True:
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

    logger.info('Starting scheduler...')
    scheduler.start()

    infinite_check()


