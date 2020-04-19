from os import getenv

BOT_TOKEN = getenv('BOT_TOKEN')
LOG_ID = getenv('LOG_ID')

DSN = f'dbname={getenv("DB_NAME")} ' \
      f'user={getenv("DB_USER")} ' \
      f'password={getenv("DB_PASSWORD")} ' \
      f'host={getenv("DB_HOST")} ' \
      f'port={getenv("DB_PORT")}'


MESSAGES = {
      'Russian': getenv('MSG_RU'),
      'English': getenv('MSG_EN')
}
