import pathlib
from datetime import date, datetime as dt

from telegram import Message


logs_folder = pathlib.Path(__file__).parent / 'logs'
logs_folder.mkdir(exist_ok=True)


def init_logger():
    path = logs_folder / f'{date.today()}.csv'
    if not path.exists():
        with open(path, 'a') as f:
            f.write('dt,user_id,message_id,language,text,error\n')


def log_sent_message(msg: Message, language: str):
    path = logs_folder / f'{date.today()}.csv'
    with open(path, 'a') as f:
        f.write(f'{dt.now()},{msg.chat.id},{msg.message_id},{language},\n')


def log_sent_failure(user_id: int, language: str, text: str, error: str):
    text = text.replace('\n', '').replace(',', '')
    path = logs_folder / f'{date.today()}.csv'
    with open(path, 'a') as f:
        f.write(f'{dt.now()},{user_id},,{language},{text},{error}\n')
