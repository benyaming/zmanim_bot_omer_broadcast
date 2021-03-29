from typing import Optional
from datetime import date, datetime as dt

from pytz import timezone
from pymongo import MongoClient
from timezonefinder import TimezoneFinder
from zmanim.util.geo_location import GeoLocation
from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.hebrew_calendar.jewish_calendar import JewishCalendar

from .config import MONGO_URL, DB_NAME, COLLECTION_NAME
from .tg_logger import logger
from .helpers import UserData, get_user_data, set_notification_time_for_user, notificate_user, reset_sent_status


def get_omer_time(user_data: UserData) -> Optional[dt]:
    tz_name = TimezoneFinder().timezone_at(lat=user_data.latitude, lng=user_data.longitude)
    location = GeoLocation('', user_data.latitude, user_data.longitude, time_zone=tz_name)
    calendar = ZmanimCalendar(60, geo_location=location, date=date.today())
    jcalendar = JewishCalendar.from_date(date.today())

    omer_day = jcalendar.day_of_omer()
    if not omer_day:
        return

    if date.today().weekday() == 4:
        omer_time = calendar.candle_lighting()
    else:
        omer_time = calendar.tzais()

    return omer_time


def set_time_for_today(reset_status: bool):
    """
    Find all users that should receive omer updates and set their notification times
    :param reset_status:
    :return:
    """
    logger.info(f'Setting timings for today, reset={reset_status}')
    client = MongoClient(MONGO_URL)
    collection = client[DB_NAME][COLLECTION_NAME]

    user_data = get_user_data(collection)

    for user in user_data:
        omer_time = get_omer_time(user)
        if not omer_time:
            continue

        set_notification_time_for_user(collection, user.user_id, omer_time.isoformat())

        if reset_status:
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

        if dt.fromisoformat(user.dt) < now and not user.sent:
            try:
                notificate_user(collection, user)
            except Exception as e:
                logger.exception(e)

    client.close()
