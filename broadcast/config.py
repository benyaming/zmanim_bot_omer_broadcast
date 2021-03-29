from os import getenv

BOT_TOKEN = getenv('BOT_TOKEN')
LOG_ID = getenv('LOG_ID')

MONGO_URL = getenv('MONGO_URL')
DB_NAME = getenv('DB_NAME', 'zmanim_bot')
COLLECTION_NAME = getenv('COLLECTION_NAME', 'zmanim')

JOB_PERIOD = int(getenv('JOB_PERIOD', 3))

MESSAGES = {
      'ru': getenv('MSG_RU'),
      'en': getenv('MSG_EN')
}
