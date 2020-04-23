import logging
from time import sleep

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from broadcast.tg_logger import logger
from broadcast.config import JOB_PERIOD
from broadcast.job import set_time_for_today, check_time

logging.basicConfig(level=logging.DEBUG)


def safe_set_time(reset_status: bool = True):
    try:
        set_time_for_today(reset_status)
    except Exception as e:
        logging.exception(e)


def safe_check():
    try:
        check_time()
    except Exception as e:
        logging.exception(e)


scheduler = BlockingScheduler()
daily_trigger = CronTrigger(day='*', hour=0, minute=1)
trigger = IntervalTrigger(minutes=JOB_PERIOD)

scheduler.add_job(safe_set_time, trigger=daily_trigger)
scheduler.add_job(safe_check, trigger=trigger)


if __name__ == '__main__':
    safe_set_time(reset_status=False)

    logger.info('Starting scheduler...')
    scheduler.start()


