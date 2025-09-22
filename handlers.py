import os
from telebot import *
from telebot.types import Message, CallbackQuery
from config import Config, logger
from database import db_instance as Database
from keyboards import Keyboards
from utils import Utils


class Handlers:
    def __init__(self, bot):
        self.bot = bot
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка всех обработчиков"""

        # Команды
        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start_help(message: Message):
            self.handle_start(message)

        @self.bot.message_handler(commands=['me'])
        def handle_me(message: Message):
            self.handle_me(message)

        @self.bot.message_handler(commands=['promote', 'demote'])
        def handle_promote_demote(message: Message):
            self.handle_promote_demote(message)

        @self.bot.message_handler(commands=['ban', 'unban'])
        def handle_ban_unban(message: Message):
            self.handle_ban_unban(message)

        @self.bot.message_handler(commands=['warn', 'unwarn'])
        def handle_warn_unwarn(message: Message):
            self.handle_warn_unwarn(message)

        @self.bot.message_handler(commands=['list'])
        def handle_list(message: Message):
            self.handle_list(message)

        @self.bot.message_handler(commands=['getinfo'])
        def handle_getinfo(message: Message):
            self.handle_getinfo(message)

        @self.bot.message_handler(commands=['reguser'])
        def handle_reguser(message: Message):
            self.handle_reguser(message)

        @self.bot.message_handler(commands=['op', 'unop'])
        def handle_op_unop(message: Message):
            self.handle_op_unop(message)

        @self.bot.message_handler(commands=['stats'])
        def handle_stats(message: Message):
            self.handle_stats(message)

        @self.bot.message_handler(commands=['alarm'])
        def handle_alarm(message: Message):
            self.handle_alarm(message)

        @self.bot.message_handler(commands=['chatid'])
        def handle_chatid(message: Message):
            """Обработка команды /chatid"""
            self.bot.send_message(message.chat.id, f"🔐 CHAT ID 🔐\n\n"
                                                   f"<code>{message.chat.id}</code>",
                                  parse_mode='HTML')

        # Бот-менеджмент команды
        @self.bot.message_handler(commands=['startbot', 'stopbot', 'addbot', 'removebot'])
        def handle_bot_management(message: Message):
            self.handle_bot_management(message)

        # Текстовые сообщения (обработка кнопок меню)
        @self.bot.message_handler(content_types=['text'])
        def handle_text_messages(message: Message):
            self.handle_text_messages(message)

        # Callback queries
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call: CallbackQuery):
            self.handle_callback_query(call)

    def handle_text_messages(self, message: Message):
        """Обработка текстовых сообщений (кнопок меню)"""
        username = message.from_user.username
        if not username:
            self.bot.reply_to(message, "❌ У вас не установлен username! Установите его в настройках Telegram.")
            return

        # Проверяем, есть ли пользователь в системе
        if not Database.user_exists(username):
            self.bot.reply_to(message, "❌ Вы не зарегистрированы в системе! Обратитесь к администратору.")
            return

        # Проверяем бан
        if Database.is_banned(username):
            self.bot.reply_to(message, "🚫 Вы забанены и не можете использовать бота.")
            return

        text = message.text.lower()

        # Обработка текстовых команд через меню
        if text == "📊 статистика":
            self.handle_stats(message)
        elif text == "📋 список ботов":
            self.show_bot_list(message)
        elif text == "🔙 назад":
            self.show_main_menu(message, username)

    def show_main_menu(self, message: Message, username: str):
        """Показать главное меню"""
        self.bot.send_message(
            message.chat.id,
            "Главное меню:",
            reply_markup=Keyboards.main_menu(username)
        )

    def show_user_list_menu(self, message: Message):
        """Показать меню списков пользователей"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_local_admin(username):
            self.bot.reply_to(message, "❌ Недостаточно прав!")
            return

        self.bot.send_message(
            message.chat.id,
            "📋 Выберите список для просмотра:",
            reply_markup=Keyboards.user_list_menu()
        )

    def show_bot_list(self, message: Message):
        """Показать список ботов"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_operator(username):
            self.bot.reply_to(message, "❌ Только операторы могут просматривать список ботов!")
            return

        bots = Database.get_all_bots()
        if not bots:
            self.bot.reply_to(message, "❌ Нет добавленных ботов!")
            return

        bot_list = "🤖 <b>Список ботов:</b>\n\n"
        for i, (bot_name, bot_data) in enumerate(bots.items(), 1):
            status = Utils.get_bot_status(bot_name)
            status_emoji = "🟢" if status == "running" else "🔴" if status == "stopped" else "⚫"
            bot_list += f"{i}. {bot_name} ({bot_data['username']}) {status_emoji}\n"

        self.bot.reply_to(message, bot_list, parse_mode='HTML')

    def handle_start(self, message: Message):
        """Обработка команды /start"""

        username = message.from_user.username
        user_id = message.from_user.id
        first_name = message.from_user.first_name

        if not username:
            self.bot.reply_to(message, "❌ У вас не установлен username! Установите его в настройках Telegram.")
            return

        # Проверяем бан
        if Database.is_banned(username):
            self.bot.reply_to(message, "🚫 Вы забанены и не можете использовать бота.")
            return

        if not Database.user_exists(username):
            Database.add_user(user_id, username, first_name)
            logger.info(f"New user @{username}")

        # Отправляем приветствие в зависимости от роли
        rank = Database.get_user_rank(username)
        welcome_text = f"👋 Добро пожаловать, {first_name}!\n"

        if rank == 'operator':
            welcome_text += "⚡ Вы оператор системы"
        elif rank == 'gadmin':
            welcome_text += "👑 Вы глобальный администратор"
        elif rank == 'ladmin':
            welcome_text += "👨‍💼 Вы локальный администратор"
        else:
            welcome_text += "👤 Вы обычный пользователь"

        self.bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=Keyboards.main_menu(username)
        )

    def handle_me(self, message: Message):
        """Обработка команды /me - информация о себе"""
        username = message.from_user.username
        if not username:
            self.bot.reply_to(message, "❌ У вас не установлен username!")
            return

        # Проверяем, есть ли пользователь в системе
        if not Database.user_exists(username):
            self.bot.reply_to(message, "❌ Вы не зарегистрированы в системе!")
            return

        # Проверяем бан
        if Database.is_banned(username):
            self.bot.reply_to(message, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = Database.get_user(username)
        if not user_data:
            self.bot.reply_to(message, "❌ Ошибка получения данных!")
            return

        rank_text = {
            'operator': '⚡ Оператор',
            'gadmin': '🔧 Глобальный администратор',
            'ladmin': '🪛 Локальный администратор',
            'user': '👤 Пользователь'
        }.get(user_data.get('rank', 'user'), '👤 Пользователь')

        banned_status = "🚫 Забанен" if Database.is_banned(username) else "✅ Активен"
        info_text = (
            "👤 <b>Информация о пользователе</b>\n\n"
            f"📧 Username: @{username}\n"
            f"👨‍💼 Ранг: {rank_text}\n"
            f"🆔 ID: <code>{user_data['user_id']}</code>\n"
            f"📛 Имя: {user_data['first_name']}"
        )
        if not user_data['rank'] in ['gadmin', 'operator']:
            info_text += (
                f"\n📊 Ограничения: {banned_status}\n"
                f"💢 Предупреждения: {user_data['warns']}/{Config.MAX_WARN}"
            )

        self.bot.reply_to(message, info_text, parse_mode='HTML')

    def handle_promote_demote(self, message: Message):
        """Обработка повышения/понижения"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_global_admin(username):
            self.bot.reply_to(message, "❌ Недостаточно прав!")
            return

        parts = message.text.split()
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: /promote @username или /demote @username")
            return

        target_username = Utils.extract_username(parts[1])
        if not target_username:
            self.bot.reply_to(message, "❌ Неверный username!")
            return

        # Проверяем, есть ли целевой пользователь в системе
        if not Database.user_exists(target_username):
            self.bot.reply_to(message, "❌ Пользователь не найден в системе!")
            return

        # Проверяем бан целевого пользователя
        if Database.is_banned(target_username):
            self.bot.reply_to(message, "❌ Нельзя работать с забаненными пользователями!")
            return

        if parts[0].startswith('/promote'):
            # Повышение
            if not Database.is_operator(username):
                self.bot.reply_to(message, "❌ Только операторы могут повышать!")
                return

            self.bot.send_message(
                message.chat.id,
                f"Выберите ранг для @{target_username}:",
                reply_markup=Keyboards.rank_selection(target_username)
            )
        else:
            # Понижение
            target_rank = Database.get_user_rank(target_username)

            if target_rank == 'operator' and not Database.is_operator(username):
                self.bot.reply_to(message, "❌ Только операторы могут понижать операторов!")
                return

            Database.update_user(target_username, {'rank': 'user'})
            self.bot.reply_to(message, f"✅ @{target_username} понижен до пользователя")

    def handle_ban_unban(self, message: Message):
        """Обработка бана/разбана"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        parts = message.text.split()
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: /ban @username [время_часы] [причина] или /unban @username")
            return

        target_username = Utils.extract_username(parts[1])
        if not target_username:
            self.bot.reply_to(message, "❌ Неверный username!")
            return

        # Проверяем, есть ли целевой пользователь в системе
        if not Database.user_exists(target_username):
            self.bot.reply_to(message, "❌ Пользователь не найден в системе!")
            return

        action = "ban" if parts[0].startswith('/ban') else "unban"

        if action == "ban":
            # Проверяем права на бан
            can_ban, error_msg = Database.can_ban_user(username, target_username)
            if not can_ban:
                self.bot.reply_to(message, f"❌ {error_msg}")
                return

            # Получаем время бана и причину
            ban_time = Config.DEFAULT_BAN_TIME
            reason = ""

            if len(parts) >= 3:
                try:
                    ban_time = int(parts[2])
                except ValueError:
                    # Если третий аргумент не число, то это причина
                    reason = " ".join(parts[2:])
            if len(parts) >= 4 and ban_time != Config.DEFAULT_BAN_TIME:
                reason = " ".join(parts[3:])

            # Баним пользователя
            if Database.ban_user(target_username, username, ban_time):
                # Отправляем уведомление пользователю
                ban_info = Database.get_ban_info(target_username)
                ban_duration = "неопределенный срок" if ban_time == 0 else f"{ban_time} часов"
                ban_message = (
                    "🚫 <b>Вы заблокированы в нашей сетке ботов!</b>\n\n"
                    f"👮 Кто выдал: @{username}\n"
                    f"⏰ Длительность бана: {ban_duration}\n"
                )
                if reason:
                    ban_message += f"📝 Причина: {reason}"

                Utils.send_message_to_user(self.bot, target_username, ban_message)

                self.bot.reply_to(message, f"✅ @{target_username} забанен на {ban_duration}")
            else:
                self.bot.reply_to(message, f"❌ Не удалось забанить @{target_username}")

        else:
            # Разбан
            if not Database.is_global_admin(username):
                self.bot.reply_to(message, "❌ Недостаточно прав для разбана!")
                return

            if Database.unban_user(target_username):
                # Отправляем уведомление пользователю
                unban_message = "✅ <b>Вы разблокированы в нашей сетке ботов!</b>"
                Utils.send_message_to_user(self.bot, target_username, unban_message)

                self.bot.reply_to(message, f"✅ @{target_username} разбанен")
            else:
                self.bot.reply_to(message, f"❌ Не удалось разбанить @{target_username}")

    def handle_warn_unwarn(self, message: Message):
        """Обработка выдачи/снятия предупреждений"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_global_admin(username):
            self.bot.reply_to(message, "❌ Недостаточно прав!")
            return

        parts = message.text.split()
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: /warn @username [причина] или /unwarn @username")
            return

        target_username = Utils.extract_username(parts[1])
        if not target_username:
            self.bot.reply_to(message, "❌ Неверный username!")
            return

        # Проверяем, есть ли целевой пользователь в системе
        if not Database.user_exists(target_username):
            self.bot.reply_to(message, "❌ Пользователь не найден в системе!")
            return

        # Проверяем права на варн
        can_warn, error_msg = Database.can_warn_user(username, target_username)
        if not can_warn:
            self.bot.reply_to(message, f"❌ {error_msg}")
            return

        action = "warn" if parts[0].startswith('/warn') else "unwarn"

        if action == "warn":
            reason = " ".join(parts[2:]) if len(parts) > 2 else ""

            success, result = Database.add_warn(target_username, username, reason)
            if success:
                if result == "banned":
                    self.bot.reply_to(message, f"✅ @{target_username} получил предупреждение и автоматически забанен за достижение лимита")
                else:
                    # Отправляем уведомление пользователю
                    user_data = Database.get_user(target_username)
                    warn_message = (
                        "⚠️ <b>Вы получили предупреждение!</b>\n\n"
                        f"📊 Текущее количество: {user_data['warns']}/{Config.MAX_WARN}\n"
                        f"👮 Кто выдал: @{username}\n"
                    )
                    if reason:
                        warn_message += f"📝 Причина: {reason}"

                    Utils.send_message_to_user(self.bot, target_username, warn_message)

                    self.bot.reply_to(message, f"✅ @{target_username} получил предупреждение ({user_data['warns']}/{Config.MAX_WARN})")
            else:
                self.bot.reply_to(message, f"❌ {result}")

        else:
            # Снятие варна
            if Database.remove_warn(target_username):
                # Отправляем уведомление пользователю
                user_data = Database.get_user(target_username)
                unwarn_message = (
                    "✅ <b>С вас снято предупреждение!</b>\n\n"
                    f"📊 Текущее количество: {user_data['warns']}/{Config.MAX_WARN}"
                )
                Utils.send_message_to_user(self.bot, target_username, unwarn_message)

                self.bot.reply_to(message, f"✅ С @{target_username} снято предупреждение ({user_data['warns']}/{Config.MAX_WARN})")
            else:
                self.bot.reply_to(message, f"❌ Не удалось снять предупреждение с @{target_username}")

    def handle_list(self, message: Message):
        """Обработка команды /list"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_local_admin(username):
            self.bot.reply_to(message, "❌ Недостаточно прав!")
            return

        self.bot.send_message(
            message.chat.id,
            "📋 Выберите список для просмотра:",
            reply_markup=Keyboards.user_list_menu()
        )

    def handle_getinfo(self, message: Message):
        """Обработка команды /getinfo"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_global_admin(username):
            self.bot.reply_to(message, "❌ Недостаточно прав!")
            return

        parts = message.text.split()
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: /getinfo @username")
            return

        target_username = Utils.extract_username(parts[1])
        if not target_username:
            self.bot.reply_to(message, "❌ Неверный username!")
            return

        # Проверяем, есть ли целевой пользователь в системе
        if not Database.user_exists(target_username):
            self.bot.reply_to(message, "❌ Пользователь не найден в системе!")
            return

        user_data = Database.get_user(target_username)
        if not user_data:
            self.bot.reply_to(message, "❌ Ошибка получения данных!")
            return

        rank_text = {
            'operator': '⚡ Оператор',
            'gadmin': '🔧 Глобальный администратор',
            'ladmin': '🪛 Локальный администратор',
            'user': '👤 Пользователь'
        }.get(user_data.get('rank', 'user'), '👤 Пользователь')

        banned_status = "🚫 Забанен" if Database.is_banned(target_username) else "✅ Активен"

        info_text = (
            "👤 <b>Информация о пользователе</b>\n\n"
            f"📧 Username: @{target_username}\n"
            f"👨‍💼 Ранг: {rank_text}\n"
            f"🆔 ID: <code>{user_data['user_id']}</code>\n"
            f"📛 Имя: {user_data['first_name']}"
        )
        if not user_data['rank'] in ['gadmin', 'operator']:
            info_text += (
                f"\n📊 Ограничения: {banned_status}\n"
                f"💢 Предупреждения: {user_data['warns']}/{Config.MAX_WARN}"
            )

        self.bot.reply_to(message, info_text, parse_mode='HTML')

    def handle_reguser(self, message: Message):
        """Обработка команды /reguser - регистрация пользователя"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_global_admin(username):
            self.bot.reply_to(message, "❌ Недостаточно прав!")
            return

        if not message.reply_to_message:
            self.bot.reply_to(message, "❌ Ответьте на сообщение пользователя!")
            return

        reply_username = message.reply_to_message.from_user.username
        if not reply_username:
            self.bot.reply_to(message, "❌ У пользователя нет username!")
            return

        # Добавляем пользователя в систему
        if Database.add_user(
            message.reply_to_message.from_user.id,
            reply_username,
            message.reply_to_message.from_user.first_name
        ):
            self.bot.reply_to(message, f"✅ Пользователь @{reply_username} зарегистрирован в системе")
        else:
            self.bot.reply_to(message, f"ℹ️ Пользователь @{reply_username} уже существует в системе")

    def handle_stats(self, message: Message):
        """Обработка команды /stats"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_operator(username):
            self.bot.reply_to(message, "❌ Только операторы могут просматривать статистику!")
            return

        stats_text = Utils.get_stats()
        self.bot.reply_to(message, stats_text, parse_mode='HTML')

    def handle_alarm(self, message: Message):
        """Обработка команды /alarm - уведомление всех пользователей"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        if not Database.is_operator(username):
            self.bot.reply_to(message, "❌ Только операторы могут отправлять уведомления!")
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: /alarm <сообщение>")
            return

        alarm_message = parts[1]
        users = Database.get_all_users()

        sent_count = 0
        total_count = len(users)

        progress_msg = self.bot.reply_to(message, f"📨 Отправка уведомлений: 0/{total_count}")

        for user_username, user_data in users.items():
            try:
                if not Database.is_banned(user_username) and 'user_id' in user_data:
                    full_message = f"🚨 <b>Важное уведомление от оператора!</b>\n\n{alarm_message}"
                    self.bot.send_message(user_data['user_id'], full_message, parse_mode='HTML')
                    sent_count += 1

                    # Обновляем прогресс каждые 10 отправок
                    if sent_count % 10 == 0:
                        self.bot.edit_message_text(
                            f"📨 Отправка уведомлений: {sent_count}/{total_count}",
                            progress_msg.chat.id,
                            progress_msg.message_id
                        )
                    time.sleep(0.1)  # Задержка чтобы не спамить

            except Exception as e:
                logger.error(f"Ошибка отправки уведомления @{user_username}: {e}")
                continue

        self.bot.edit_message_text(
            f"✅ Уведомления отправлены: {sent_count}/{total_count} пользователей",
            progress_msg.chat.id,
            progress_msg.message_id
        )

    def handle_all_messages(self, message: Message):
        """Обработка всех текстовых сообщений"""
        username = message.from_user.username
        if not username:
            self.bot.reply_to(message, "❌ У вас не установлен username! Установите его в настройках Telegram.")
            return

        # Проверяем, есть ли пользователь в системе
        if not Database.user_exists(username):
            self.bot.reply_to(message, "❌ Вы не зарегистрированы в системе! Обратитесь к администратору.")
            return

        # Проверяем бан
        if Database.is_banned(username):
            self.bot.reply_to(message, "🚫 Вы забанены и не можете использовать бота.")
            return

        # Обычные пользователи в ЛС не могут ничего делать
        if (message.chat.type == 'private' and
            Database.get_user_rank(username) == 'user'):
            self.bot.reply_to(message, "❌ У вас нет доступа к функциям бота.")
            return

    def handle_callback_query(self, call: CallbackQuery):
        """Обработка callback запросов"""
        username = call.from_user.username
        if not username or Database.is_banned(username):
            return

        if call.data.startswith('list_'):
            list_type = call.data.split('_')[1]
            self.handle_list_callback(call, list_type)

        elif call.data.startswith('promote_'):
            rank = call.data.split('_')[1]
            self.handle_promote_callback(call, rank)

        elif call.data.startswith('ladmin_bot_'):
            bot_name = call.data.split('ladmin_bot_')[1]
            self.handle_ladmin_bot_selection(call, bot_name)

        elif call.data == 'cancel_action':
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.answer_callback_query(call.id, "❌ Действие отменено")

    def handle_list_callback(self, call: CallbackQuery, list_type):
        """Обработка callback для списков"""
        ladmins = Database.get_all_ladmins()
        gadmins = Database.get_all_global_admins()
        operators = Database.get_all_operators()

        if list_type == 'ladmin':
            text = Utils.format_user_list(ladmins, 'ladmin')
        elif list_type == 'gadmin':
            text = Utils.format_user_list(gadmins, 'gadmin')
        elif list_type == 'operator':
            text = Utils.format_user_list(operators, 'operator')
        else:
            text = "❌ Неизвестный тип списка"

        self.bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML'
        )

    def handle_promote_callback(self, call: CallbackQuery, rank):
        """Обработка callback для повышения пользователя"""
        username = call.from_user.username
        if not username or Database.is_banned(username):
            self.bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return

        if not Database.is_operator(username):
            self.bot.answer_callback_query(call.id, "❌ Только операторы могут повышать!")
            return

        # Получаем целевого пользователя из сообщения
        message_text = call.message.text
        if "для @" in message_text:
            target_username = message_text.split("для @")[1].split(":")[0].strip()
        else:
            self.bot.answer_callback_query(call.id, "❌ Не удалось определить пользователя")
            return

        if not target_username:
            self.bot.answer_callback_query(call.id, "❌ Неверный username!")
            return

        # Проверяем, есть ли целевой пользователь в системе
        if not Database.user_exists(target_username):
            self.bot.answer_callback_query(call.id, "❌ Пользователь не найден в системе!")
            return

        # Проверяем бан целевого пользователя
        if Database.is_banned(target_username):
            self.bot.answer_callback_query(call.id, "❌ Нельзя повысить забаненного!")
            return

        if rank == 'ladmin':
            # Для локальных админов показываем выбор бота
            bots = Database.get_all_bots()
            if not bots:
                self.bot.answer_callback_query(call.id, "❌ Нет доступных ботов!")
                return

            self.bot.edit_message_text(
                f"🤖 Выберите бота для назначения @{target_username} локальным администратором:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=self.get_bot_selection_keyboard()
            )
            return

        # Обработка глобальных админов и операторов
        rank_translation = {
            'gadmin': 'глобальный администратор',
            'operator': 'оператор'
        }

        success = False
        message = ""

        if rank == 'gadmin':
            # Добавляем в глобальные админы
            success = Database.add_global_admin(target_username)
            message = f"✅ @{target_username} повышен до глобального администратора" if success else f"❌ Не удалось повысить @{target_username}"

        elif rank == 'operator':
            # Повышение до оператора
            success = Database.add_operator(target_username)
            message = f"✅ @{target_username} повышен до оператора" if success else f"❌ Не удалось повысить @{target_username}"

        if success:
            logger.info(f"@{username} повысил @{target_username} до {rank}")

        # Обновляем сообщение
        self.bot.edit_message_text(
            message,
            call.message.chat.id,
            call.message.message_id
        )

        self.bot.answer_callback_query(call.id)

    def handle_op_unop(self, message: Message):
        """Обработка команд op/unop (только через консоль)"""
        # Эти команды обрабатываются только через консоль
        if message.chat.type != 'private':
            self.bot.reply_to(message, "❌ Команды /op и /unop доступны только через консоль!")
        else:
            self.bot.reply_to(message, "❌ Эти команды работают только в консольном режиме!")

    @staticmethod
    def get_bot_selection_keyboard():
        """Клавиатура выбора бота для локального админа"""
        bots = Database.get_all_bots()
        keyboard = types.InlineKeyboardMarkup(row_width=2)

        for bot_name in bots.keys():
            keyboard.add(
                types.InlineKeyboardButton(
                    f"🤖 {bot_name}",
                    callback_data=f"ladmin_bot_{bot_name}"
                )
            )

        keyboard.add(
            types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_action")
        )
        return keyboard

    def handle_ladmin_bot_selection(self, call: CallbackQuery, bot_name):
        """Обработка выбора бота для локального админа"""
        username = call.from_user.username
        if not username or Database.is_banned(username):
            self.bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return

        if not Database.is_operator(username):
            self.bot.answer_callback_query(call.id, "❌ Только операторы могут назначать локальных админов!")
            return

        # Получаем целевого пользователя из сообщения
        message_text = call.message.text
        if "назначения @" in message_text:
            target_username = message_text.split("назначения @")[1].split()[0].strip()
        else:
            self.bot.answer_callback_query(call.id, "❌ Не удалось определить пользователя")
            return

        # Проверяем, есть ли целевой пользователь в системе
        if not Database.user_exists(target_username):
            self.bot.answer_callback_query(call.id, "❌ Пользователь не найден в системе!")
            return

        # Добавляем пользователя как локального админа для выбранного бота
        success = Database.add_ladmin_to_bot(target_username, bot_name)

        if success:
            message = f"✅ @{target_username} назначен локальным администратором для бота {bot_name}"
            logger.info(f"@{username} назначил @{target_username} локальным админом для {bot_name}")
        else:
            message = f"ℹ️ @{target_username} уже локальный администратор для {bot_name}"

        self.bot.edit_message_text(
            message,
            call.message.chat.id,
            call.message.message_id
        )

        self.bot.answer_callback_query(call.id)

    def handle_bot_management(self, message: Message):
        """Обработка управления ботами: addbot, removebot, startbot, stopbot"""
        username = message.from_user.username
        if not username or Database.is_banned(username):
            return

        # Проверяем права - только операторы могут управлять ботами
        if not Database.is_operator(username):
            self.bot.reply_to(message, "❌ Только операторы могут управлять ботами!")
            return

        parts = message.text.split()
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Неверный формат команды!")
            return

        command = parts[0].lower()
        bot_name = parts[1].strip()

        if command == '/addbot':
            self.handle_add_bot(message, bot_name, parts)
        elif command == '/removebot':
            self.handle_remove_bot(message, bot_name)
        elif command == '/startbot':
            self.handle_start_bot(message, bot_name)
        elif command == '/stopbot':
            self.handle_stop_bot(message, bot_name)
        else:
            self.bot.reply_to(message, "❌ Неизвестная команда!")

    def handle_add_bot(self, message: Message, bot_name: str, parts: list):
        """Обработка добавления бота"""
        if len(parts) < 4:
            self.bot.reply_to(message, "❌ Использование: /addbot <имя_бота> <@юзернейм_бота> <тип>")
            return

        bot_username = parts[2]
        bot_type = parts[3]

        exe_path = os.path.join(Config.BOTS_DIR, f'{bot_name}.exe')

        # Проверяем валидность пути
        if not os.path.exists(exe_path):
            self.bot.reply_to(message, f"❌ Файл не найден: {exe_path}")
            return

        if not exe_path.lower().endswith('.exe'):
            self.bot.reply_to(message, "❌ Укажите путь к .exe файлу!")
            return

        # Добавляем бота в базу
        if Database.add_bot(bot_name, exe_path, bot_username, bot_type):
            self.bot.reply_to(message, f"✅ Бот '{bot_name}' успешно добавлен!\n"
                                       f"🤖 Username: {bot_username}\n"
                                       f"🔧 Тип: {bot_type}\n"
                                       f"📁 Путь: {exe_path}")
        else:
            self.bot.reply_to(message, f"❌ Бот '{bot_name}' уже существует!")

    def handle_remove_bot(self, message: Message, bot_name: str):
        """Обработка удаления бота"""
        if Database.remove_bot(bot_name):
            self.bot.reply_to(message, f"✅ Бот '{bot_name}' успешно удален!")
        else:
            self.bot.reply_to(message, f"❌ Бот '{bot_name}' не найден!")

    def handle_start_bot(self, message: Message, bot_name: str):
        """Обработка запуска бота"""
        bots = Database.get_all_bots()

        if bot_name not in bots:
            self.bot.reply_to(message, f"❌ Бот '{bot_name}' не найден!")
            return

        bot = bots[bot_name]
        if not bot.get('exe'):
            self.bot.reply_to(message, f"❌ Для бота '{bot_name}' не указан путь к exe!")
            return

        # Проверяем статус бота
        status = Utils.get_bot_status(bot_name)
        if status == "running":
            self.bot.reply_to(message, f"✅ Бот '{bot_name}' уже запущен!")
            return
        elif status == "error":
            self.bot.reply_to(message, f"❌ Ошибка проверки статуса бота '{bot_name}'!")
            return

        # Запускаем бота
        success, result = Utils.start_bot(bot_name)

        if success:
            # Обновляем статус в базе
            bot['state'] = True
            Database.save_bots(bots)

        self.bot.reply_to(message, result)

    def handle_stop_bot(self, message: Message, bot_name: str):
        """Обработка остановки бота"""
        bots = Database.get_all_bots()

        if bot_name not in bots:
            self.bot.reply_to(message, f"❌ Бот '{bot_name}' не найден!")
            return

        # Проверяем статус бота
        status = Utils.get_bot_status(bot_name)
        if status == "stopped":
            self.bot.reply_to(message, f"✅ Бот '{bot_name}' уже остановлен!")
            return
        elif status == "error":
            self.bot.reply_to(message, f"❌ Ошибка проверки статуса бота '{bot_name}'!")
            return

        # Останавливаем бота
        success, result = Utils.stop_bot(bot_name)

        if success:
            # Обновляем статус в базе
            bot = bots[bot_name]
            bot['state'] = False
            Database.save_bots(bots)

        self.bot.reply_to(message, result)