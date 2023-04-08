import betterlogging as bl


from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

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
    safe_set_time(should_reset=False)

    logger.info('Starting scheduler...')
    scheduler.start()


