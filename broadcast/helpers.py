from time import sleep
from typing import List
from datetime import date
from dataclasses import dataclass

from zmanim.hebrew_calendar.jewish_calendar import JewishCalendar

from .misc import bot
from .config import GET_USERS_QUERY, MESSAGES, DB_USER_TABLE


@dataclass
class UserData:
    user_id: int
    latitude: float
    longitude: float
    lang: str
    sent: bool = None
    dt: str = None


def get_user_data(conn) -> List[UserData]:
    cur = conn.cursor()
    cur.execute(GET_USERS_QUERY)

    fetched = []

    for row in cur.fetchall():
        fetched.append(UserData(*row))

    return fetched


def set_user_time(conn, user_id: int, dt: str):
    cur = conn.cursor()
    cur.execute(f'update {DB_USER_TABLE} '
                f'set dt = %s where user_id = %s', (dt, user_id))
    conn.commit()


def set_user_sent_status(conn, user_id: int):
    cur = conn.cursor()
    cur.execute(f'update {DB_USER_TABLE} '
                f'set sent_today = TRUE where user_id = %s', (user_id,))
    conn.commit()


def reset_sent_status(conn):
    cur = conn.cursor()
    cur.execute(f'update {DB_USER_TABLE} '
                f'set sent_today = FALSE where TRUE')
    conn.commit()


def compose_msg(lang: str) -> str:
    jcalendar = JewishCalendar.from_date(date.today()).forward(1)
    omer_day = jcalendar.day_of_omer()
    if not omer_day:
        return ''

    msg = MESSAGES[lang]

    if lang == 'English':
        if omer_day % 10 == 1:
            omer_day = f'{omer_day}st'
        elif omer_day % 10 == 2:
            omer_day = f'{omer_day}nd'
        elif omer_day % 10 == 3:
            omer_day = f'{omer_day}rd'
        else:
            omer_day = f'{omer_day}th'

    msg = msg.format(f'<b>{omer_day}</b>')
    return msg


def notificate_user(conn, user: UserData):
    msg = compose_msg(user.lang)
    bot.send_message(user.user_id, msg, parse_mode='HTML')
    set_user_sent_status(conn, user.user_id)
    sleep(.05)




