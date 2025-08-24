import os
import logging
from dotenv import load_dotenv

load_dotenv()


class Config:
    BRB_TOKEN = os.getenv('BRB_TOKEN')
    SUPER_OPERATOR = 'ghoulyonok'

    # Директории
    DATA_DIR = os.getenv('DATA_DIR')
    LOGS_DIR = os.getenv('LOGS_DIR')
    BOTS_DIR = os.getenv('BOTS_DIR')

    # Файлы данных
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    BOTS_FILE = os.path.join(DATA_DIR, 'bots_data.json')
    ADMINS_FILE = os.path.join(DATA_DIR, 'admins.json')

    @classmethod
    def setup_directories(cls):
        """Создает необходимые директории"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)

    @classmethod
    def setup_logging(cls):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(cls.LOGS_DIR, 'brb-bot.log')),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('brb-bot')


# Инициализация
Config.setup_directories()
logger = Config.setup_logging()