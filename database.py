import sqlite3
import time
from config import Config, logger


class Database:
    def __init__(self):
        self.db_file = Config.DB_FILE
        self.init_database()

    def get_connection(self):
        """Получение соединения с базой данных"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Инициализация таблиц базы данных"""
        try:
            with self.get_connection() as conn:
                # Таблица пользователей
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        first_name TEXT NOT NULL,
                        rank TEXT NOT NULL DEFAULT 'user',
                        banned BOOLEAN NOT NULL DEFAULT FALSE,
                        warns INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Таблица ботов
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bots (
                        name TEXT PRIMARY KEY,
                        exe_path TEXT NOT NULL,
                        username TEXT NOT NULL,
                        state BOOLEAN NOT NULL DEFAULT FALSE,
                        type TEXT NOT NULL DEFAULT 'Standard',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Таблица локальных администраторов ботов
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bot_ladmins (
                        bot_name TEXT NOT NULL,
                        username TEXT NOT NULL,
                        PRIMARY KEY (bot_name, username),
                        FOREIGN KEY (bot_name) REFERENCES bots (name) ON DELETE CASCADE,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                ''')

                # Таблица глобальных администраторов
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS global_admins (
                        username TEXT PRIMARY KEY,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                ''')

                # Таблица операторов
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS operators (
                        username TEXT PRIMARY KEY,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                ''')

                # Таблица банов
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bans (
                        username TEXT PRIMARY KEY,
                        banned_by TEXT NOT NULL,
                        banned_at INTEGER NOT NULL,
                        ban_time INTEGER NOT NULL DEFAULT 0,
                        reason TEXT,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                ''')

                # Таблица кодов аутентификации
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS auth_codes (
                        code TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        used BOOLEAN NOT NULL DEFAULT FALSE,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                ''')

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    # User methods
    def add_user(self, user_id, username, first_name):
        """Добавление пользователя"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                    (user_id, username.lower(), first_name)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    def get_user(self, username):
        """Получение пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM users WHERE username = ?',
                    (username.lower(),)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def update_user(self, username, updates):
        """Обновление пользователя"""
        try:
            with self.get_connection() as conn:
                set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
                values = list(updates.values()) + [username.lower()]

                conn.execute(
                    f'UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE username = ?',
                    values
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    def user_exists(self, username):
        """Проверка существования пользователя"""
        return self.get_user(username) is not None

    def get_all_users(self):
        """Получение всех пользователей"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT * FROM users')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    # Ban methods
    def is_banned(self, username):
        """Проверка бана"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM bans WHERE username = ?',
                    (username.lower(),)
                )
                ban_info = cursor.fetchone()

                if not ban_info:
                    return False

                ban_info = dict(ban_info)
                ban_time = ban_info.get('ban_time', 0)
                banned_at = ban_info.get('banned_at', 0)

                # Проверяем временный бан
                if ban_time > 0:
                    current_time = int(time.time())
                    if current_time - banned_at >= ban_time * 3600:
                        # Время бана истекло, разбаниваем
                        self.unban_user(username)
                        return False
                    return True
                # Перманентный бан
                return True
        except Exception as e:
            logger.error(f"Error checking ban: {e}")
            return False

    def ban_user(self, username, banned_by, ban_time=0, reason=""):
        """Бан пользователя"""
        try:
            with self.get_connection() as conn:
                # Обновляем пользователя
                conn.execute(
                    'UPDATE users SET banned = TRUE, rank = "user", warns = 0 WHERE username = ?',
                    (username.lower(),)
                )

                # Удаляем из админов/операторов если нужно
                conn.execute('DELETE FROM global_admins WHERE username = ?', (username.lower(),))
                conn.execute('DELETE FROM operators WHERE username = ?', (username.lower(),))

                # Добавляем запись о бане
                conn.execute(
                    'INSERT OR REPLACE INTO bans (username, banned_by, banned_at, ban_time, reason) VALUES (?, ?, ?, ?, ?)',
                    (username.lower(), banned_by.lower(), int(time.time()), ban_time, reason)
                )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            return False

    def unban_user(self, username):
        """Разбан пользователя"""
        try:
            with self.get_connection() as conn:
                # Обновляем пользователя
                conn.execute(
                    'UPDATE users SET banned = FALSE WHERE username = ?',
                    (username.lower(),)
                )

                # Удаляем запись о бане
                conn.execute(
                    'DELETE FROM bans WHERE username = ?',
                    (username.lower(),)
                )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            return False

    def get_ban_info(self, username):
        """Получение информации о бане"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM bans WHERE username = ?',
                    (username.lower(),)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting ban info: {e}")
            return None

    # Admin management
    def is_operator(self, username):
        """Проверка оператора"""
        if not username or username.lower() == Config.SUPER_OPERATOR:
            return username and username.lower() == Config.SUPER_OPERATOR

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT 1 FROM operators WHERE username = ?',
                    (username.lower(),)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking operator: {e}")
            return False

    def is_global_admin(self, username):
        """Проверка глобального админа"""
        if not username:
            return False
        if self.is_operator(username):
            return True

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT 1 FROM global_admins WHERE username = ?',
                    (username.lower(),)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking global admin: {e}")
            return False

    def is_local_admin(self, username, bot_name=None):
        """Проверка локального админа"""
        if not username:
            return False

        if self.is_global_admin(username):
            return True

        if bot_name:
            try:
                with self.get_connection() as conn:
                    cursor = conn.execute(
                        'SELECT 1 FROM bot_ladmins WHERE bot_name = ? AND username = ?',
                        (bot_name, username.lower())
                    )
                    return cursor.fetchone() is not None
            except Exception as e:
                logger.error(f"Error checking local admin: {e}")
                return False
        return False

    def add_operator(self, username):
        """Добавление оператора"""
        if not username or username.lower() == Config.SUPER_OPERATOR:
            return False

        if self.is_banned(username):
            return False

        if not self.user_exists(username):
            return False

        try:
            with self.get_connection() as conn:
                # Добавляем в операторы
                conn.execute(
                    'INSERT OR IGNORE INTO operators (username) VALUES (?)',
                    (username.lower(),)
                )

                # Обновляем ранг пользователя
                conn.execute(
                    'UPDATE users SET rank = "operator" WHERE username = ?',
                    (username.lower(),)
                )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding operator: {e}")
            return False

    def remove_operator(self, username):
        """Удаление оператора"""
        if not username or username.lower() == Config.SUPER_OPERATOR:
            return False

        try:
            with self.get_connection() as conn:
                # Удаляем из операторов
                conn.execute(
                    'DELETE FROM operators WHERE username = ?',
                    (username.lower(),)
                )

                # Обновляем ранг пользователя
                conn.execute(
                    'UPDATE users SET rank = "user" WHERE username = ?',
                    (username.lower(),)
                )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error removing operator: {e}")
            return False

    def add_global_admin(self, username):
        """Добавление глобального админа"""
        if not username or self.is_banned(username):
            return False

        if not self.user_exists(username):
            return False

        try:
            with self.get_connection() as conn:
                # Добавляем в глобальные админы
                conn.execute(
                    'INSERT OR IGNORE INTO global_admins (username) VALUES (?)',
                    (username.lower(),)
                )

                # Обновляем ранг пользователя
                conn.execute(
                    'UPDATE users SET rank = "gadmin" WHERE username = ?',
                    (username.lower(),)
                )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding global admin: {e}")
            return False

    def remove_global_admin(self, username):
        """Удаление глобального админа"""
        if not username:
            return False

        try:
            with self.get_connection() as conn:
                # Удаляем из глобальных админов
                conn.execute(
                    'DELETE FROM global_admins WHERE username = ?',
                    (username.lower(),)
                )

                # Обновляем ранг пользователя
                conn.execute(
                    'UPDATE users SET rank = "user" WHERE username = ?',
                    (username.lower(),)
                )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error removing global admin: {e}")
            return False

    # Warn management
    def add_warn(self, username, warned_by, reason=""):
        """Добавление предупреждения"""
        user = self.get_user(username)
        if not user:
            return False, "User not found"

        current_warns = user.get('warns', 0)
        if current_warns >= Config.MAX_WARN:
            return False, "Max warns reached"

        # Обновляем количество варнов
        if not self.update_user(username, {'warns': current_warns + 1}):
            return False, "Error updating warns"

        # Проверяем, не достиг ли пользователь максимума варнов
        if current_warns + 1 >= Config.MAX_WARN:
            self.ban_user(username, warned_by, Config.DEFAULT_BAN_TIME, reason)
            return True, "banned"

        return True, "warned"

    def remove_warn(self, username):
        """Удаление предупреждения"""
        user = self.get_user(username)
        if not user:
            return False

        current_warns = user.get('warns', 0)
        if current_warns > 0:
            return self.update_user(username, {'warns': current_warns - 1})
        return False

    # Bot management
    def add_bot(self, bot_name, exe_path, bot_username, bot_type="Standard"):
        """Добавление бота"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    'INSERT INTO bots (name, exe_path, username, type) VALUES (?, ?, ?, ?)',
                    (bot_name, exe_path, bot_username, bot_type)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Бот уже существует
        except Exception as e:
            logger.error(f"Error adding bot: {e}")
            return False

    def remove_bot(self, bot_name):
        """Удаление бота"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    'DELETE FROM bots WHERE name = ?',
                    (bot_name,)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error removing bot: {e}")
            return False

    def get_bot(self, bot_name):
        """Получение бота"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM bots WHERE name = ?',
                    (bot_name,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting bot: {e}")
            return None

    def get_all_bots(self):
        """Получение всех ботов"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT * FROM bots')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all bots: {e}")
            return []

    def update_bot_state(self, bot_name, state):
        """Обновление состояния бота"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    'UPDATE bots SET state = ? WHERE name = ?',
                    (state, bot_name)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating bot state: {e}")
            return False

    # Local admin management
    def add_ladmin_to_bot(self, username, bot_name):
        """Добавление локального админа к боту"""
        if not username or self.is_banned(username):
            return False

        if not self.user_exists(username):
            return False

        if not self.get_bot(bot_name):
            return False

        try:
            with self.get_connection() as conn:
                # Добавляем как локального админа
                conn.execute(
                    'INSERT OR IGNORE INTO bot_ladmins (bot_name, username) VALUES (?, ?)',
                    (bot_name, username.lower())
                )

                # Обновляем ранг пользователя
                conn.execute(
                    'UPDATE users SET rank = "ladmin" WHERE username = ?',
                    (username.lower(),)
                )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding local admin: {e}")
            return False

    def remove_ladmin_from_bot(self, username, bot_name):
        """Удаление локального админа из бота"""
        try:
            with self.get_connection() as conn:
                # Удаляем из локальных админов
                conn.execute(
                    'DELETE FROM bot_ladmins WHERE bot_name = ? AND username = ?',
                    (bot_name, username.lower())
                )

                # Проверяем, есть ли у пользователя другие права
                cursor = conn.execute(
                    'SELECT 1 FROM bot_ladmins WHERE username = ?',
                    (username.lower(),)
                )
                has_other_ladmin = cursor.fetchone() is not None

                cursor = conn.execute(
                    'SELECT 1 FROM global_admins WHERE username = ?',
                    (username.lower(),)
                )
                has_global_admin = cursor.fetchone() is not None

                cursor = conn.execute(
                    'SELECT 1 FROM operators WHERE username = ?',
                    (username.lower(),)
                )
                has_operator = cursor.fetchone() is not None

                # Обновляем ранг только если нет других прав
                if not has_other_ladmin and not has_global_admin and not has_operator:
                    conn.execute(
                        'UPDATE users SET rank = "user" WHERE username = ?',
                        (username.lower(),)
                    )

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error removing local admin: {e}")
            return False

    def get_bot_ladmins(self, bot_name):
        """Получение локальных админов бота"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT username FROM bot_ladmins WHERE bot_name = ?',
                    (bot_name,)
                )
                return [row['username'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting bot ladmins: {e}")
            return []

    def get_all_operators(self):
        """Получение всех операторов"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT username FROM operators')
                return [row['username'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting operators: {e}")
            return []

    def get_all_global_admins(self):
        """Получение всех глобальных админов"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT username FROM global_admins')
                return [row['username'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting global admins: {e}")
            return []

    def get_all_ladmins(self):
        """Получение всех локальных админов"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT DISTINCT username FROM bot_ladmins')
                return [row['username'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all ladmins: {e}")
            return []

    # Auth codes
    def add_auth_code(self, code, username):
        """Добавление кода аутентификации"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    'INSERT INTO auth_codes (code, username, created_at) VALUES (?, ?, ?)',
                    (code, username.lower(), int(time.time()))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding auth code: {e}")
            return False

    def use_auth_code(self, code):
        """Использование кода аутентификации"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'UPDATE auth_codes SET used = TRUE WHERE code = ? AND used = FALSE',
                    (code,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error using auth code: {e}")
            return False

    def get_auth_code(self, code):
        """Получение информации о коде"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM auth_codes WHERE code = ?',
                    (code,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting auth code: {e}")
            return None

    def cleanup_expired_auth_codes(self):
        """Очистка просроченных кодов"""
        try:
            with self.get_connection() as conn:
                expire_time = int(time.time()) - Config.AUTH_CODE_EXPIRE_TIME
                conn.execute(
                    'DELETE FROM auth_codes WHERE created_at < ? OR used = TRUE',
                    (expire_time,)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error cleaning up auth codes: {e}")
            return False

    # Utility methods
    def can_ban_user(self, issuer_username, target_username):
        """Проверка прав на бан"""
        if not self.user_exists(target_username):
            return False, "User not found"

        if self.is_operator(target_username):
            return False, "Cannot ban operators"

        if self.is_global_admin(target_username):
            if not self.is_operator(issuer_username):
                return False, "Only operators can ban global admins"

        issuer_rank = self.get_user(issuer_username).get('rank', 'user')
        target_rank = self.get_user(target_username).get('rank', 'user')

        if issuer_rank == 'gadmin' and target_rank in ['gadmin', 'operator']:
            return False, "Insufficient permissions"

        return True, ""

    def can_warn_user(self, issuer_username, target_username):
        """Проверка прав на варн"""
        if not self.user_exists(target_username):
            return False, "User not found"

        if self.is_operator(target_username) or self.is_global_admin(target_username):
            return False, "Cannot warn operators or global admins"

        return True, ""

    def get_user_rank(self, username):
        """Получение ранга пользователя"""
        user = self.get_user(username)
        return user.get('rank', 'user') if user else None

    def get_user_warns(self, username):
        """Получение количества предупреждений"""
        user = self.get_user(username)
        return user.get('warns', 0) if user else 0


# Глобальный экземпляр базы данных
db_instance = Database()