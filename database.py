import json
import os
from config import Config


class Database:
    @staticmethod
    def load_data(file_path, default_data=None):
        """Загрузка данных из JSON файла"""
        if default_data is None:
            default_data = {}

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_data
        except:
            return default_data

    @staticmethod
    def save_data(file_path, data):
        """Сохранение данных в JSON файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except:
            return False

    # Users methods
    @staticmethod
    def load_users():
        return Database.load_data(Config.USERS_FILE, {})

    @staticmethod
    def save_users(users):
        return Database.save_data(Config.USERS_FILE, users)

    # Bots methods
    @staticmethod
    def load_bots():
        return Database.load_data(Config.BOTS_FILE, {})

    @staticmethod
    def save_bots(bots):
        return Database.save_data(Config.BOTS_FILE, bots)

    # Admins methods
    @staticmethod
    def load_admins():
        default = {
            "global_admins": [],
            "operators": []
        }
        return Database.load_data(Config.ADMINS_FILE, default)

    @staticmethod
    def save_admins(admins):
        return Database.save_data(Config.ADMINS_FILE, admins)

    # User management
    @staticmethod
    def add_user(user_id, username, first_name):
        """Добавление пользователя"""
        users = Database.load_users()
        username_lower = username.lower()

        if username_lower not in users:
            users[username_lower] = {
                "id": user_id,
                "first_name": first_name,
                "rank": "user",
                "banned": False
            }
            Database.save_users(users)
            return True
        return False

    @staticmethod
    def get_user(username):
        """Получение пользователя"""
        users = Database.load_users()
        username_lower = username.lower().replace('@', '')
        return users.get(username_lower)

    @staticmethod
    def update_user(username, updates):
        """Обновление пользователя"""
        users = Database.load_users()
        username_lower = username.lower().replace('@', '')

        if username_lower in users:
            users[username_lower].update(updates)
            Database.save_users(users)
            return True
        return False

    @staticmethod
    def is_banned(username):
        """Проверка бана"""
        user = Database.get_user(username)
        return user and user.get('banned', False)

    @staticmethod
    def get_user_rank(username):
        """Получение ранга пользователя"""
        user = Database.get_user(username)
        return user.get('rank', 'user') if user else 'user'

    # Admin management
    @staticmethod
    def is_operator(username):
        """Проверка оператора"""
        if not username:
            return False
        admins = Database.load_admins()
        username_lower = username.lower().replace('@', '')
        return (username_lower in admins.get('operators', []) or
                username_lower == Config.SUPER_OPERATOR)

    @staticmethod
    def is_global_admin(username):
        """Проверка глобального админа"""
        if not username:
            return False
        admins = Database.load_admins()
        username_lower = username.lower().replace('@', '')
        return (username_lower in admins.get('global_admins', []) or
                Database.is_operator(username_lower))

    @staticmethod
    def is_local_admin(username, bot_name=None):
        """Проверка локального админа"""
        if not username:
            return False

        if Database.is_global_admin(username):
            return True

        if bot_name:
            bots = Database.load_bots()
            username_lower = username.lower().replace('@', '')
            bot = bots.get(bot_name)
            return bot and username_lower in bot.get('ladmins', [])
        return False

    @staticmethod
    def add_operator(username):
        """Добавление оператора"""
        if not username or username.lower() == Config.SUPER_OPERATOR:
            return False

        if Database.is_banned(username):
            return False

        admins = Database.load_admins()
        username_lower = username.lower().replace('@', '')

        if username_lower not in admins['operators']:
            admins['operators'].append(username_lower)
            Database.save_admins(admins)
            Database.update_user(username, {'rank': 'operator'})
            return True
        return False

    @staticmethod
    def remove_operator(username):
        """Удаление оператора"""
        if not username or username.lower() == Config.SUPER_OPERATOR:
            return False

        admins = Database.load_admins()
        username_lower = username.lower().replace('@', '')

        if username_lower in admins['operators']:
            admins['operators'].remove(username_lower)
            Database.save_admins(admins)
            Database.update_user(username, {'rank': 'user'})
            return True
        return False

    @staticmethod
    def add_global_admin(username):
        """Добавление глобального админа"""
        if not username or Database.is_banned(username):
            return False

        admins = Database.load_admins()
        username_lower = username.lower().replace('@', '')

        if username_lower not in admins['global_admins']:
            admins['global_admins'].append(username_lower)
            Database.save_admins(admins)
            Database.update_user(username, {'rank': 'gadmin'})
            return True
        return False

    @staticmethod
    def remove_global_admin(username):
        """Удаление глобального админа"""
        if not username:
            return False

        admins = Database.load_admins()
        username_lower = username.lower().replace('@', '')

        if username_lower in admins['global_admins']:
            admins['global_admins'].remove(username_lower)
            Database.save_admins(admins)
            Database.update_user(username, {'rank': 'user'})
            return True
        return False

    # Bot management
    @staticmethod
    def add_bot(bot_name, exe_path, username=None):  # убрали token, добавили username
        """Добавление бота"""
        bots = Database.load_bots()

        if bot_name in bots:
            return False

        bots[bot_name] = {
            'exe': exe_path,  # изменено на 'exe'
            'username': username,  # добавили username
            'state': False,  # добавили state
            'ladmins': []
        }
        Database.save_bots(bots)
        return True

    @staticmethod
    def remove_bot(bot_name):
        """Удаление бота"""
        bots = Database.load_bots()

        if bot_name in bots:
            del bots[bot_name]
            Database.save_bots(bots)
            return True
        return False

    @staticmethod
    def add_ladmin_to_bot(username, bot_name):
        """Добавление локального админа к боту"""
        if not username or Database.is_banned(username):
            return False

        bots = Database.load_bots()
        bot = bots.get(bot_name)

        if not bot:
            return False

        username_lower = username.lower().replace('@', '')

        if username_lower not in bot['ladmins']:
            bot['ladmins'].append(username_lower)
            Database.save_bots(bots)
            Database.update_user(username, {'rank': 'ladmin'})
            return True
        return False

    @staticmethod
    def remove_ladmin_from_bot(username, bot_name):
        """Удаление локального админа из бота"""
        bots = Database.load_bots()
        bot = bots.get(bot_name)

        if not bot:
            return False

        username_lower = username.lower().replace('@', '')

        if username_lower in bot['ladmins']:
            bot['ladmins'].remove(username_lower)
            Database.save_bots(bots)
            Database.update_user(username, {'rank': 'user'})
            return True
        return False