import os
import logging
from dotenv import load_dotenv

load_dotenv()


class Config:
    bot_version = 5.3

    BRB_TOKEN = os.getenv('BRB_TOKEN')
    DS_BRB_TOKEN = os.getenv('DS_BRB_TOKEN')

    SUPER_OPERATOR = os.getenv('SUPER_OPERATOR', 'ghoulyonok')
    MAX_WARN = int(os.getenv('MAX_WARN', 3))
    DEFAULT_BAN_TIME = int(os.getenv('DEFAULT_BAN_TIME', 0))
    AUTH_CODE_EXPIRE_TIME = int(os.getenv('AUTH_CODE_EXPIRE_TIME', 300))

    # Директории
    DATA_DIR = os.getenv('DATA_DIR', 'data')
    LOGS_DIR = os.getenv('LOGS_DIR', 'logs')
    BOTS_DIR = os.getenv('BOTS_DIR', 'bots')

    # Файл базы данных
    DB_FILE = os.path.join(DATA_DIR, 'system.db')

    @classmethod
    def setup_directories(cls):
        """Создает необходимые директории"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        os.makedirs(cls.BOTS_DIR, exist_ok=True)

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