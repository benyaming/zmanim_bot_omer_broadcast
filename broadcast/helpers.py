import logging
from datetime import date
from typing import List, Tuple, Optional
from dataclasses import dataclass

from telegram import Message
from telegram.error import Unauthorized
from pymongo.collection import Collection
from zmanim.hebrew_calendar.jewish_calendar import JewishCalendar

from . import texsts
from .misc import bot
from .file_logger import log_sent_message, log_sent_failure


logger = logging.getLogger(__name__)


@dataclass
class UserData:
    user_id: int
    latitude: float
    longitude: float
    lang: str
    dt: Optional[str] = None


def get_location_from_list(location_list: List[dict]) -> Tuple[float, float]:
    loc = list(filter(lambda l: l['is_active'], location_list))
    if not loc:
        return 55.72, 37.64
    return loc[0]['lat'], loc[0]['lng']


def get_user_data(collection: Collection, exclude_received: bool = True) -> List[UserData]:
    """ Get all users that should receive omer notifications """
    fetched = []
    filters = {'omer.is_enabled': True}
    if exclude_received:
        filters['omer.is_sent_today'] = False
        filters['omer.notification_time'] = {'$ne': None}

    documents = collection.find(filters)

    for doc in documents:
        lat, lng = get_location_from_list(doc['location_list'])
        user = UserData(
            user_id=doc['user_id'],
            latitude=lat,
            longitude=lng,
            lang=doc['language'],
            dt=doc['omer']['notification_time']
        )
        fetched.append(user)

    return fetched


def set_notification_time_for_user(collection: Collection, user_id: int, notification_time: Optional[str]):
    collection.update_one(
        filter={'user_id': user_id},
        update={'$set': {'omer.notification_time': notification_time}}
    )


def set_user_sent_status(collection: Collection, user_id: int):
    collection.update_one(
        filter={'user_id': user_id},
        update={'$set': {'omer.is_sent_today': True}}
    )


def reset_sent_status(collection: Collection):
    collection.update_many(
        filter={'omer.is_enabled': True},
        update={'$set': {'omer.is_sent_today': False}}
    )


def compose_msg(lang: str) -> str:
    jcalendar = JewishCalendar.from_date(date.today()).forward(1)
    omer_day = jcalendar.day_of_omer()
    if not omer_day:
        raise ValueError('No omer day!')

    if jcalendar.gregorian_date.weekday() != 5:
        msg = texsts.MESSAGES[lang]
    else:
        msg = texsts.MESSAGES_FRIDAY[lang]

    if lang == 'en':
        if omer_day % 10 == 1:
            omer_day = f'{omer_day}st'
        elif omer_day % 10 == 2:
            omer_day = f'{omer_day}nd'
        elif omer_day % 10 == 3:
            omer_day = f'{omer_day}rd'
        else:
            omer_day = f'{omer_day}th'
    elif lang == 'ru':
        omer_day = f'{omer_day}-й'

    msg = msg.format(f'<b>{omer_day}</b>')
    full_text = f'{msg}\n\n' \
                f'<code>{texsts.blessing}\n\n' \
                f'{texsts.omer_texts[jcalendar.day_of_omer()]}\n\n' \
                f'{texsts.after_text}</code>'

    return full_text


def notificate_user(user: UserData):
    msg = compose_msg(user.lang)

    try:
        sent_msg: Message = bot.send_message(user.user_id, msg, parse_mode='HTML')
        log_sent_message(sent_msg, user.lang)
    except Unauthorized as e:
        logger.warning(f'User [{user.user_id}] skipped. Reason: {e}')
    except Exception as e:
        log_sent_failure(user.user_id, user.lang, msg, repr(e))
        logger.warning(f'Failed to send message "{msg}" to user {user.user_id}')
        logger.exception(e)
