import json
import os
import time
from config import Config, logger


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
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return default_data

    @staticmethod
    def save_data(file_path, data):
        """Сохранение данных в JSON файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
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

    # Banned methods
    @staticmethod
    def load_banned():
        return Database.load_data(Config.BANNED_FILE, {})

    @staticmethod
    def save_banned(banned):
        return Database.save_data(Config.BANNED_FILE, banned)

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
                "banned": False,
                "warns": 0
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
        banned_data = Database.load_banned()
        username_lower = username.lower().replace('@', '')

        if username_lower in banned_data:
            ban_info = banned_data[username_lower]
            ban_time = ban_info.get('ban_time', 0)
            banned_at = ban_info.get('banned_at', 0)

            # Проверяем временный бан
            if ban_time > 0:
                current_time = int(time.time())
                if current_time - banned_at >= ban_time * 3600:
                    # Время бана истекло, разбаниваем
                    Database.unban_user(username_lower)
                    return False
                return True
            # Перманентный бан
            return True
        return False

    @staticmethod
    def get_user_rank(username):
        """Получение ранга пользователя"""
        user = Database.get_user(username)
        return user.get('rank', 'user') if user else None

    @staticmethod
    def get_user_warns(username):
        """Получение количества предупреждений"""
        user = Database.get_user(username)
        return user.get('warns', 0) if user else 0

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

        user = Database.get_user(username)
        if not user:
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

        user = Database.get_user(username)
        if not user:
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

    # Ban management
    @staticmethod
    def ban_user(username, banned_by, ban_time=0):
        """Бан пользователя"""
        user = Database.get_user(username)
        if not user:
            return False

        banned_data = Database.load_banned()
        username_lower = username.lower().replace('@', '')

        if Database.get_user_rank(username) == 'gadmin':
            Database.remove_global_admin(username)

        banned_data[username_lower] = {
            "banned_by": banned_by.lower().replace('@', ''),
            "banned_at": int(time.time()),
            "ban_time": ban_time
        }

        # Обновляем пользователя
        Database.update_user(username, {
            'banned': True,
            'rank': 'user',
            'warns': 0
        })

        return Database.save_banned(banned_data)

    @staticmethod
    def unban_user(username):
        """Разбан пользователя"""
        banned_data = Database.load_banned()
        username_lower = username.lower().replace('@', '')

        if username_lower in banned_data:
            del banned_data[username_lower]
            Database.save_banned(banned_data)

        # Обновляем пользователя
        Database.update_user(username, {'banned': False})
        return True

    @staticmethod
    def get_ban_info(username):
        """Получение информации о бане"""
        banned_data = Database.load_banned()
        username_lower = username.lower().replace('@', '')
        return banned_data.get(username_lower)

    # Warn management
    @staticmethod
    def add_warn(username, warned_by, reason=""):
        """Добавление предупреждения"""
        user = Database.get_user(username)
        if not user:
            return False, "User not found"

        current_warns = user.get('warns', 0)
        if current_warns >= Config.MAX_WARN:
            return False, "Max warns reached"

        Database.update_user(username, {'warns': current_warns + 1})

        # Проверяем, не достиг ли пользователь максимума варнов
        if current_warns + 1 >= Config.MAX_WARN:
            Database.ban_user(username, warned_by, Config.DEFAULT_BAN_TIME)
            return True, "banned"

        return True, "warned"

    @staticmethod
    def remove_warn(username):
        """Удаление предупреждения"""
        user = Database.get_user(username)
        if not user:
            return False

        current_warns = user.get('warns', 0)
        if current_warns > 0:
            Database.update_user(username, {'warns': current_warns - 1})
            return True
        return False

    # Bot management
    @staticmethod
    def add_bot(bot_name, exe_path, bot_username, bot_type="Standard"):
        """Добавление бота"""
        bots = Database.load_bots()

        if bot_name in bots:
            return False

        bots[bot_name] = {
            'exe': exe_path,
            'ladmins': [],
            'username': bot_username,
            'state': False,
            'type': bot_type
        }
        return Database.save_bots(bots)

    @staticmethod
    def remove_bot(bot_name):
        """Удаление бота"""
        bots = Database.load_bots()

        if bot_name in bots:
            del bots[bot_name]
            return Database.save_bots(bots)
        return False

    @staticmethod
    def add_ladmin_to_bot(username, bot_name):
        """Добавление локального админа к боту"""
        if not username or Database.is_banned(username):
            return False

        user = Database.get_user(username)
        if not user:
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

    # User check methods
    @staticmethod
    def user_exists(username):
        """Проверка существования пользователя"""
        return Database.get_user(username) is not None

    @staticmethod
    def can_ban_user(issuer_username, target_username):
        """Проверка прав на бан"""
        if not Database.user_exists(target_username):
            return False, "User not found"

        if Database.is_operator(target_username):
            return False, "Cannot ban operators"

        if Database.is_global_admin(target_username):
            if not Database.is_operator(issuer_username):
                return False, "Only operators can ban global admins"

        issuer_rank = Database.get_user_rank(issuer_username)
        target_rank = Database.get_user_rank(target_username)

        if issuer_rank == 'gadmin' and target_rank in ['gadmin', 'operator']:
            return False, "Insufficient permissions"

        return True, ""

    @staticmethod
    def can_warn_user(issuer_username, target_username):
        """Проверка прав на варн"""
        if not Database.user_exists(target_username):
            return False, "User not found"

        if Database.is_operator(target_username) or Database.is_global_admin(target_username):
            return False, "Cannot warn operators or global admins"

        return True, ""