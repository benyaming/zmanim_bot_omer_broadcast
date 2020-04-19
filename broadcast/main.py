import logging
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from broadcast.tg_logger import TgHandler
from broadcast.config import JOB_PERIOD
from broadcast.job import set_time_for_today, check_time


logger = logging.getLogger('omer_broadcast')
logger.setLevel(logging.INFO)
logger.addHandler(TgHandler(logging.WARNING))
logger.addHandler(logging.StreamHandler())


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


scheduler = BackgroundScheduler()
daily_trigger = CronTrigger(day='*', hour=0, minute=1)
trigger = IntervalTrigger(minutes=JOB_PERIOD)

scheduler.add_job(safe_set_time, trigger=daily_trigger)
scheduler.add_job(safe_check, trigger=trigger)


if __name__ == '__main__':
    msg = '''ERROR:omer_broadcast:Forbidden: bot was blocked by the user
<code>Traceback (most recent call last):
  File &quot;/home/app/broadcast/job.py&quot;, line 64, in check_time
    notificate_user(conn, user)
  File &quot;/home/app/broadcast/helpers.py&quot;, line 79, in notificate_user
    bot.send_message(user.user_id, msg, parse_mode=&#x27;HTML&#x27;)
  File &quot;&lt;decorator-gen-2&gt;&quot;, line 2, in send_message
  File &quot;/root/.local/share/virtualenvs/app-4uwEKS64/lib/python3.7/site-packages/telegram/bot.py&quot;, line 70, in decorator
    result = func(*args, **kwargs)
  File &quot;/root/.local/share/virtualenvs/app-4uwEKS64/lib/python3.7/site-packages/telegram/bot.py&quot;, line 351, in send_message
    timeout=timeout, **kwargs)
  File &quot;/root/.local/share/virtualenvs/app-4uwEKS64/lib/python3.7/site-packages/telegram/bot.py&quot;, line 178, in _message
    result = self._request.post(url, data, timeout=timeout)
  File &quot;/root/.local/share/virtualenvs/app-4uwEKS64/lib/python3.7/site-packages/telegram/utils/request.py&quot;, line 334, in post
    **urlopen_kwargs)
  File &quot;/root/.local/share/virtualenvs/app-4uwEKS64/lib/python3.7/site-packages/telegram/utils/request.py&quot;, line 243, in _request_wrapper
    raise Unauthorized(message)
telegram.error.Unauthorized: Forbidden: bot was blocked by the user

===========================

61
62                if dt.fromisoformat(user.dt) < now and not user.sent:
63                    try:
64 →                      notificate_user(conn, user)
65                    except Exception as e:
66                        logger.exception(e)
</code>'''
    logger.error(msg)
    # safe_set_time(reset_status=False)
    #
    # scheduler.start()
    # logger.info('Starting scheduler...')
    #
    # try:
    #     while True:
    #         sleep(10)
    # except (KeyboardInterrupt, SystemExit):
    #     scheduler.shutdown()

