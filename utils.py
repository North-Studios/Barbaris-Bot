import re
import subprocess
import psutil
import os
from database import Database


class Utils:
    @staticmethod
    def extract_username(text):
        """Извлечение username из текста"""
        if not text:
            return None

        # Убираем @ в начале если есть
        text = text.replace('@', '').strip()

        # Проверяем валидность username
        if re.match(r'^[a-zA-Z0-9_]{1,32}$', text):  # Исправлено: минимальная длина 1 символ
            return text.lower()
        return None

    @staticmethod
    def get_user_info_text(username):
        """Получение информации о пользователе"""
        user = Database.get_user(username)
        if not user:
            return "❌ Пользователь не найден"

        rank_translation = {
            'user': '👤 Пользователь',
            'ladmin': '👨‍💼 Локальный администратор',
            'gadmin': '👑 Глобальный администратор',
            'operator': '⚡ Оператор'
        }

        rank = rank_translation.get(user['rank'], '👤 Пользователь')
        banned = "🚫 Забанен" if user.get('banned', False) else "✅ Отсутствуют"

        return f"""👤 <b>Информация о пользователе</b>

📧 Username: @{username}
👨‍💼 Ранг: {rank}
🆔 ID: {user.get('id', 'Неизвестно')}
📛 Имя: {user.get('first_name', 'Неизвестно')}
📊 Ограничения: {banned}"""

    @staticmethod
    def get_bot_status(bot_name):
        """Проверка статуса бота"""
        bots = Database.load_bots()
        bot = bots.get(bot_name)

        if not bot or not bot.get('exe'):  # Исправлено на 'exe'
            return "not_found"

        # Проверяем запущен ли процесс
        try:
            exe_path = bot['exe']  # Исправлено на 'exe'
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

        if not bot or not bot.get('exe'):  # Исправлено на 'exe'
            return False, "❌ Бот не найден"

        try:
            # Проверяем, не запущен ли уже бот
            if Utils.get_bot_status(bot_name) == "running":
                return False, "❌ Бот уже запущен"

            subprocess.Popen([bot['exe']])  # Исправлено на 'exe'
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

        exe_path = bot.get('exe')  # Исправлено на 'exe'
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

        total_users = len(users)
        banned_users = sum(1 for user in users.values() if user.get('banned', False))

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
            'ban': '🚫',
            'ladmin': '👨‍💼',
            'gadmin': '👑',
            'operator': '⚡'
        }

        title = {
            'ban': 'Забаненные пользователи',
            'ladmin': 'Локальные администраторы',
            'gadmin': 'Глобальные администраторы',
            'operator': 'Операторы'
        }

        result = [f"<b>{emoji[list_type]} {title[list_type]}</b>\n"]

        for i, username in enumerate(users, 1):
            user = Database.get_user(username)
            if user:
                status = "🚫" if user.get('banned', False) else "✅"
                result.append(f"{i}. @{username} {status}")
            else:
                result.append(f"{i}. @{username} (нет в базе)")

        return "\n".join(result)