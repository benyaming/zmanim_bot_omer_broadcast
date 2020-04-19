import logging
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from broadcast.tg_logger import TgHandler
from broadcast.job import set_time_for_today, check_time


logger = logging.getLogger('omer_broadcast')
logger.setLevel(logging.INFO)
logger.addHandler(TgHandler(logging.WARNING))
logger.addHandler(logging.StreamHandler())


def safe_set_time():
    try:
        set_time_for_today()
    except Exception as e:
        logging.exception(e)


def safe_check():
    try:
        check_time()
    except Exception as e:
        logging.exception(e)


scheduler = BackgroundScheduler()
daily_trigger = CronTrigger(day='*', hour=0, minute=1)
trigger = IntervalTrigger(minutes=1)

scheduler.add_job(safe_set_time, trigger=daily_trigger)
scheduler.add_job(safe_check, trigger=trigger)


if __name__ == '__main__':
    scheduler.start()
    logger.info('Starting scheduler...')

    try:
        while True:
            sleep(10)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

