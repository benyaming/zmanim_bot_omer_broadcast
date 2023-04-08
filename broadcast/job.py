import time
import logging
from typing import Optional
from datetime import date, datetime as dt

from pytz import timezone
from pymongo import MongoClient
from timezonefinder import TimezoneFinder
from zmanim.util.geo_location import GeoLocation
from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.hebrew_calendar.jewish_calendar import JewishCalendar

from .config import MONGO_URL, DB_NAME, COLLECTION_NAME
from .helpers import UserData, get_user_data, set_notification_time_for_user, notificate_user, \
    reset_sent_status, set_user_sent_status


logger = logging.getLogger(__name__)


def get_omer_time(user_data: UserData) -> Optional[str]:
    tz_name = TimezoneFinder().timezone_at(lat=user_data.latitude, lng=user_data.longitude)
    location = GeoLocation('', user_data.latitude, user_data.longitude, time_zone=tz_name)
    calendar = ZmanimCalendar(60, geo_location=location, date=date.today())
    jcalendar = JewishCalendar.from_date(date.today())

    jcalendar.in_israel = tz_name in ('Asia/Tel_Aviv', 'Asia/Jerusalem', 'Asia/Hebron')

    omer_day = jcalendar.day_of_omer()
    if not omer_day and (jcalendar.jewish_day, jcalendar.jewish_month) != (15, 1):
        return

    if jcalendar.is_assur_bemelacha() and jcalendar.is_tomorrow_assur_bemelacha():
        return
    elif jcalendar.is_tomorrow_assur_bemelacha():
        omer_time = calendar.candle_lighting()
    else:
        omer_time = calendar.tzais()

    if isinstance(omer_time, dt):
        return omer_time.isoformat()


def set_time_for_today(should_reset: bool):
    """
    Find all users that should receive omer updates and set their notification times
    :param should_reset: if True, reset all users' sent status
    :return:
    """
    logger.info(f'Setting timings for today, reset={should_reset}')
    client = MongoClient(MONGO_URL)
    collection = client[DB_NAME][COLLECTION_NAME]

    user_data = get_user_data(collection, exclude_received=False)

    for user in user_data:
        omer_time = get_omer_time(user)
        set_notification_time_for_user(collection, user.user_id, omer_time)

        if should_reset:
            reset_sent_status(collection)

    client.close()


def check_time():
    logger.info(f'Checking time...')
    client = MongoClient(MONGO_URL)
    collection = client[DB_NAME][COLLECTION_NAME]
    user_data = get_user_data(collection)

    for user in user_data:
        tz_name = TimezoneFinder().timezone_at(lat=user.latitude, lng=user.longitude)
        tz = timezone(tz_name)
        now = dt.now(tz)

        if dt.fromisoformat(user.dt) < now:
            try:
                notificate_user(user)
            except Exception as e:
                logger.exception(e)
            finally:
                set_user_sent_status(collection, user.user_id)

        time.sleep(.05)

    client.close()
