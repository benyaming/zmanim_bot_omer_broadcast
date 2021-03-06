from os import getenv

BOT_TOKEN = getenv('BOT_TOKEN')
LOG_ID = getenv('LOG_ID')

GET_USERS_QUERY = getenv('GET_USERS_QUERY')
DB_USER_TABLE = getenv('DB_USER_TABLE')

JOB_PERIOD = int(getenv('JOB_PERIOD', 3))

DSN = f'dbname={getenv("DB_NAME")} ' \
      f'user={getenv("DB_USER")} ' \
      f'password={getenv("DB_PASSWORD")} ' \
      f'host={getenv("DB_HOST")} ' \
      f'port={getenv("DB_PORT")}'


MESSAGES = {
      'Russian': getenv('MSG_RU'),
      'English': getenv('MSG_EN')
}

BUTTONS = {
      'Russian': getenv('BUTTON_RU'),
      'English': getenv('BUTTON_EN')
}

CHANNEL_POST_OFFSET = int(getenv('CHANNEL_INIT_POST'))
LINK_TO_POST = getenv('LINK_TO_POST')
