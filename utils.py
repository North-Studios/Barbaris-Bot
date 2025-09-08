import re
import subprocess
import psutil
import os
from database import Database
from config import Config, logger

telegram_bot = None

class Utils:
    @staticmethod
    def extract_username(text):
        """Извлечение username из текста"""
        if not text:
            return None

        text = text.replace('@', '').strip()

        if re.match(r'^[a-zA-Z0-9_]{1,32}$', text):
            return text.lower()
        return None

    @staticmethod
    def get_bot_status(bot_name):
        """Проверка статуса бота"""
        bots = Database.load_bots()
        bot = bots.get(bot_name)

        if not bot or not bot.get('exe'):
            return "not_found"

        try:
            exe_path = bot['exe']
            exe_name = os.path.basename(exe_path)

            for process in psutil.process_iter(['name', 'exe']):
                if process.info['exe'] and os.path.basename(process.info['exe']).lower() == exe_name.lower():
                    return "running"
            return "stopped"
        except Exception as e:
            print(f"❌ Ошибка проверки статуса бота {bot_name}: {e}")
            return "error"

    @staticmethod
    def start_bot(bot_name):
        """Запуск бота"""
        bots = Database.load_bots()
        bot = bots.get(bot_name)

        if not bot or not bot.get('exe'):
            return False, "❌ Бот не найден"

        try:
            if Utils.get_bot_status(bot_name) == "running":
                return False, "❌ Бот уже запущен"

            subprocess.Popen([bot['exe']])
            return True, "✅ Бот запущен"
        except Exception as e:
            return False, f"❌ Ошибка запуска: {e}"

    @staticmethod
    def stop_bot(bot_name):
        """Остановка бота"""
        bots = Database.load_bots()
        bot = bots.get(bot_name)

        if not bot:
            return False, "❌ Бот не найден"

        exe_path = bot.get('exe')
        if not exe_path:
            return False, "❌ Путь к exe не указан"

        try:
            process_found = False
            exe_name = os.path.basename(exe_path)

            for process in psutil.process_iter(['name', 'exe']):
                if process.info['exe'] and os.path.basename(process.info['exe']).lower() == exe_name.lower():
                    process.terminate()
                    process_found = True

            if process_found:
                return True, "✅ Бот остановлен"
            else:
                return False, "❌ Бот не был запущен"
        except Exception as e:
            return False, f"❌ Ошибка остановки: {e}"

    @staticmethod
    def get_stats():
        """Получение статистики"""
        users = Database.load_users()
        bots = Database.load_bots()
        admins = Database.load_admins()
        banned_data = Database.load_banned()

        total_users = len(users)
        banned_users = len(banned_data)

        running_bots = 0
        for bot_name in bots:
            if Utils.get_bot_status(bot_name) == "running":
                running_bots += 1

        return f"""📊 <b>Статистика системы</b>

👥 Всего пользователей: {total_users}
🚫 Забаненных: {banned_users}
✅ Активных: {total_users - banned_users}

🤖 Всего ботов: {len(bots)}
▶️ Активных ботов: {running_bots}
⏹️ Остановленных: {len(bots) - running_bots}

👑 Глобальных админов: {len(admins.get('global_admins', []))}
⚡ Операторов: {len(admins.get('operators', []))}"""

    @staticmethod
    def format_user_list(users, list_type):
        """Форматирование списка пользователей"""
        if not users:
            return "❌ Список пуст"

        emoji = {
            'ladmin': '👨‍💼',
            'gadmin': '👑',
            'operator': '⚡'
        }

        title = {
            'ladmin': 'Локальные администраторы',
            'gadmin': 'Глобальные администраторы',
            'operator': 'Операторы'
        }

        result = [f"<b>{emoji[list_type]} {title[list_type]}</b>\n"]

        for i, username in enumerate(users, 1):
            user = Database.get_user(username)
            if user:
                status = "🚫" if Database.is_banned(username) else "✅"
                result.append(f"{i}. @{username} {status}")
            else:
                result.append(f"{i}. @{username} (нет в базе)")

        return "\n".join(result)

    @staticmethod
    def format_ban_time(ban_time):
        """Форматирование времени бана"""
        if ban_time == 0:
            return "Перманентный"
        return f"{ban_time} часов"

    @staticmethod
    def send_message_to_user(bot, username, message):
        """Отправка сообщения пользователю в ЛС"""
        try:
            user = Database.get_user(username)
            if user and user.get('id'):
                bot.send_message(user['id'], message)
                return True
        except Exception as e:
            logger.error(f"Error sending message to {username}: {e}")
        return False

    @staticmethod
    def set_telegram_bot(bot_instance):
        """Установка экземпляра Telegram бота для отправки сообщений"""
        global telegram_bot
        telegram_bot = bot_instance

    @staticmethod
    def send_message_to_user(bot, username, message):
        """Отправка сообщения пользователю в ЛС через Telegram"""
        try:
            user = Database.get_user(username)
            if user and user.get('id'):
                # Используем глобальный экземпляр бота если не передан
                if bot is None and telegram_bot is not None:
                    telegram_bot.send_message(user['id'], message, parse_mode='HTML')
                elif bot is not None:
                    bot.send_message(user['id'], message, parse_mode='HTML')
                return True
        except Exception as e:
            logger.error(f"Error sending message to {username}: {e}")
        return False