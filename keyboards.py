from telebot import types
from database import Database


class Keyboards:
    @staticmethod
    def main_menu(username):
        """Главное меню в зависимости от роли"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        rank = Database.get_user_rank(username)

        if rank == 'operator':
            buttons = [
                "📊 Статистика", "📋 Список ботов"
            ]
        elif rank == 'gadmin' or rank == 'ladmin':
            buttons = [
                "📊 Статистика",
            ]
        else:
            buttons = []

        keyboard.add(*buttons)
        return keyboard

    @staticmethod
    def user_list_menu():
        """Меню списков пользователей"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton("🚫 Забаненные", callback_data="list_ban"),
            types.InlineKeyboardButton("👨‍💼 Лок. админы", callback_data="list_ladmin"),
            types.InlineKeyboardButton("👑 Глоб. админы", callback_data="list_gadmin"),
            types.InlineKeyboardButton("⚡ Операторы", callback_data="list_operator")
        ]
        keyboard.add(*buttons)
        return keyboard

    @staticmethod
    def rank_selection(target_username):
        """Выбор ранга для повышения"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton("👨‍💼 Лок. админ", callback_data=f"promote_ladmin_{target_username}"),
            types.InlineKeyboardButton("👑 Глоб. админ", callback_data=f"promote_gadmin_{target_username}"),
            types.InlineKeyboardButton("⚡ Оператор", callback_data=f"promote_operator_{target_username}")
        ]
        keyboard.add(*buttons)

        # Добавляем кнопку отмены
        keyboard.add(
            types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_action")
        )

        return keyboard

    @staticmethod
    def bot_selection(target_username):
        """Выбор бота для локального админа"""
        bots = Database.load_bots()
        keyboard = types.InlineKeyboardMarkup(row_width=2)

        for bot_name in bots.keys():
            keyboard.add(
                types.InlineKeyboardButton(
                    f"🤖 {bot_name}",
                    callback_data=f"ladmin_bot_{bot_name}_{target_username}"
                )
            )

        keyboard.add(
            types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_action")
        )
        return keyboard

    @staticmethod
    def confirm_action(action, target):
        """Клавиатура подтверждения действия"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{action}_{target}"),
            types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_action")
        ]
        keyboard.add(*buttons)
        return keyboard