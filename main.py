import telebot
import threading
from config import Config, logger
from handlers import Handlers
from console import ConsoleHandler
from discord_bot import start_discord_bot
from utils import Utils


def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация бота
        bot = telebot.TeleBot(Config.BRB_TOKEN)

        # Устанавливаем экземпляр бота в Utils для отправки сообщений
        Utils.set_telegram_bot(bot)

        # Инициализация обработчиков
        handlers = Handlers(bot)

        # Запуск консольного обработчика
        ConsoleHandler.start_console_listener()

        # Запуск Discord бота в отдельном потоке
        discord_thread = threading.Thread(target=start_discord_bot, daemon=True)
        discord_thread.start()

        logger.info(f"BRB BOT v{Config.bot_version} runs!")
        logger.info(f"Discord bot starting in separate thread")
        print(f"🤖 Barbariska Bot v{Config.bot_version} запущен!")
        print("🤖 Discord bot запускается в отдельном потоке")
        print("⚡ Готов к работе...")
        print("🎮 Консольные команды доступны в отдельном потоке")

        # Запуск бота
        bot.infinity_polling()

    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        print(f"❌ Ошибка запуска: {e}")


if __name__ == "__main__":
    main()