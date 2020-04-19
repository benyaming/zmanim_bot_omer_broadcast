import logging
from typing import Optional
from datetime import date, datetime as dt

from pytz import timezone
from psycopg2 import connect
from timezonefinder import TimezoneFinder
from zmanim.util.geo_location import GeoLocation
from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.hebrew_calendar.jewish_calendar import JewishCalendar
from telegram.error import Unauthorized

from .config import DSN
from .helpers import UserData, get_user_data, set_user_time, notificate_user, reset_sent_status


logger = logging.getLogger('omer_broadcast')


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
    logger.info('Setting timings for today')
    with connect(DSN) as conn:
        if reset_status:
            reset_sent_status(conn)
        user_data = get_user_data(conn)

        for user in user_data:
            omer_time = get_omer_time(user)
            if not omer_time:
                continue

            set_user_time(conn, user.user_id, omer_time.isoformat())


def check_time():
    logger.info(f'Checking time...')
    with connect(DSN) as conn:
        user_data = get_user_data(conn)
        for user in user_data:
            tz_name = TimezoneFinder().timezone_at(lat=user.latitude, lng=user.longitude)
            tz = timezone(tz_name)
            now = dt.now(tz)

            if dt.fromisoformat(user.dt) < now and not user.sent:
                try:
                    notificate_user(conn, user)
                except Exception as e:
                    logger.exception(e)

