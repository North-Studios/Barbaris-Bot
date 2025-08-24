import telebot
from config import Config, logger
from database import Database
from handlers import Handlers
from console import ConsoleHandler


def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация бота
        bot = telebot.TeleBot(Config.BRB_TOKEN)

        # Инициализация обработчиков
        handlers = Handlers(bot)

        # Запуск консольного обработчика
        ConsoleHandler.start_console_listener()

        logger.info("Бот Barbariska Bot v3.1 запущен")
        print("🤖 Barbariska Bot v3.1 запущен!")
        print("⚡ Готов к работе...")
        print("🎮 Консольные команды доступны в отдельном потоке")

        # Запуск бота
        bot.infinity_polling()

    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        print(f"❌ Ошибка запуска: {e}")


if __name__ == "__main__":
    main()