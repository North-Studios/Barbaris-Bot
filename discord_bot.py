import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from config import Config, logger
from database import db_instance as Database
from utils import Utils
import os


async def send_error(interaction: discord.Interaction, msg: str):
    embed = discord.Embed(
        title=msg,
        color=discord.Color.dark_red()
    )
    await interaction.response.send_message(embed=embed)


class DiscordBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = commands.Bot(
            command_prefix='/',
            intents=intents
        )
        self.setup_events()

    async def setup_commands(self):
        """Настройка слэш-команд Discord бота"""

        @self.bot.tree.command(name="addbot", description="Add new bot")
        @app_commands.describe(name="Bot name", username="Bot username", bot_type="Bot type")
        async def addbot(interaction: discord.Interaction, name: str, username: str, bot_type: str):
            """Добавление нового бота"""
            if not await self.check_op_role(interaction):
                return

            # Проверяем валидность username
            if not username.startswith('@'):
                await send_error(interaction, "❌ Username должен начинаться с @")
                return

            exe_path = f"{Config.BOTS_DIR}/{name}.exe"

            # Проверяем существование файла
            try:
                if not os.path.exists(exe_path):
                    await send_error(interaction,f"❌ Файл не найден: {exe_path}")
                    return
            except Exception as e:
                await send_error(interaction,f"❌ Ошибка проверки файла: {e}")
                return

            # Добавляем бота в базу
            if Database.add_bot(name, exe_path, username, bot_type):
                embed = discord.Embed(
                    title=f"✅ Бот '{name}' успешно добавлен!\n",
                    description=
                        f"🤖 Username: {username}\n"
                        f"🔧 Тип: {bot_type}\n"
                        f"📁 Путь: {exe_path}",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed)
                logger.info(f"DISCORD: {interaction.user.name} added bot {name}")
            else:
                await send_error(interaction,f"❌ Бот '{name}' уже существует!")

        @self.bot.tree.command(name="alarm", description="Mass notification to all users")
        @app_commands.describe(message="Message to send")
        async def alarm(interaction: discord.Interaction, message: str):
            """Массовое уведомление всех пользователей"""
            if not await self.check_op_role(interaction):
                return

            users = Database.get_all_users()
            total_count = len(users)
            sent_count = 0

            embed = discord.Embed(
                title=f"📨 Sending notifications: 0/{total_count}",
                color=discord.Color.brand_red()
            )
            await interaction.response.send_message(embed=embed)
            progress_msg = await interaction.original_response()

            for i, user in enumerate(users, 1):
                username = user.get('username')
                try:
                    if not Database.is_banned(username):
                        # Отправляем уведомление через Telegram бота
                        full_message = f"🚨 <b>Важное уведомление от оператора!</b>\n\n{message}"
                        Utils.send_message_to_user(None, username, full_message)
                        sent_count += 1

                        if sent_count % 10 == 0:
                            embed.title = f"📨 Sending notifications: {sent_count}/{total_count}"
                            await progress_msg.edit(embed=embed)
                        await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"DISCORD: Error sending notification to {username}: {e}")
                    continue

            embed.title = f"✅ Notifications sent: {sent_count}/{total_count} users"
            await progress_msg.edit(embed=embed)
            logger.info(f"DISCORD: {interaction.user.name} sent alarm to {sent_count} users")

        @self.bot.tree.command(name="bantg", description="Ban user in Telegram")
        @app_commands.describe(username="Telegram username", ban_time="Ban duration in hours", reason="Ban reason")
        async def ban(interaction: discord.Interaction, username: str, ban_time: int = 0, reason: str = ""):
            """Бан пользователя"""
            if not await self.check_admin_role(interaction):
                return

            target_username = Utils.extract_username(username)
            if not target_username:
                await send_error(interaction, "❌ Invalid username!")
                return

            # Проверяем существование пользователя
            if not Database.user_exists(target_username):
                await send_error(interaction, "❌ User not found in system!")
                return

            # Проверяем права на бан
            can_ban, error_msg = Database.can_ban_user(interaction.user.name, target_username)
            if not can_ban:
                await send_error(interaction,f"❌ {error_msg}")
                return

            # Баним пользователя
            if Database.ban_user(target_username, interaction.user.name, ban_time):
                # Отправляем уведомление пользователю
                ban_duration = "indefinite" if ban_time == 0 else f"{ban_time} hours"
                ban_message = (
                    "🚫 **You have been banned from our bot network!**\n\n"
                    f"👮 Banned by: {interaction.user.name}\n"
                    f"⏰ Duration: {ban_duration}\n"
                )
                if reason:
                    ban_message += f"📝 Reason: {reason}"

                Utils.send_message_to_user(None, target_username, ban_message)

                embed = discord.Embed(
                    title=f"✅ @{target_username} banned for {ban_duration}",
                    color=discord.Color.brand_red()
                )
                await interaction.response.send_message(embed=embed)
                logger.info(f"DISCORD: {interaction.user.name} banned @{target_username} for {ban_duration}")
            else:
                await send_error(interaction,f"❌ Failed to ban @{target_username}")

        @self.bot.tree.command(name="botlist", description="Show list of all bots")
        async def botlist(interaction: discord.Interaction):
            """Список всех ботов"""
            if not await self.check_op_role(interaction):
                return

            bots = Database.get_all_bots()
            if not bots:
                await send_error(interaction, "❌ No bots added!")
                return

            bot_list = ''
            for i, bot in enumerate(bots, 1):
                status = Utils.get_bot_status(bot)
                status_emoji = "🟢" if status == "running" else "🔴" if status == "stopped" else "⚫"
                bot_list += f"{i}. {bot.get('name')} ({bot.get('username')}) {status_emoji}\n"

            embed = discord.Embed(
                title="🤖 **Bot List:**\n\n",
                description=bot_list,
                color=discord.Color.brand_green()
            )
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="demote", description="Demote user to regular user")
        @app_commands.describe(username="Telegram username")
        async def demote(interaction: discord.Interaction, username: str):
            """Понижение пользователя"""
            if not await self.check_op_role(interaction):
                return

            target_username = Utils.extract_username(username)
            if not target_username:
                await send_error(interaction, "❌ Invalid username!")
                return

            # Проверяем существование пользователя
            if not Database.user_exists(target_username):
                await send_error(interaction, "❌ User not found in system!")
                return

            # Понижаем пользователя
            Database.update_user(target_username, {'rank': 'user'})
            embed = discord.Embed(
                title=f"✅ @{target_username} demoted to user",
                color=discord.Color.dark_gray()
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"DISCORD: {interaction.user.name} demoted @{target_username}")

        @self.bot.tree.command(name="getinfo", description="Get user information")
        @app_commands.describe(username="Telegram username")
        async def getinfo(interaction: discord.Interaction, username: str):
            """Информация о пользователе"""
            if not await self.check_op_role(interaction):
                return

            target_username = Utils.extract_username(username)
            if not target_username:
                await send_error(interaction, "❌ Invalid username!")
                return

            # Проверяем существование пользователя
            if not Database.user_exists(target_username):
                await send_error(interaction, "❌ User not found in system!")
                return

            user_data = Database.get_user(target_username)
            if not user_data:
                await send_error(interaction, "❌ Error getting user data!")
                return

            rank_text = {
                'operator': '⚡ Operator',
                'gadmin': '🔧 Global Admin',
                'ladmin': '🪛 Local Admin',
                'user': '👤 User'
            }.get(user_data.get('rank', 'user'), '👤 User')

            banned_status = "🚫 Banned" if Database.is_banned(target_username) else "✅ Active"
            info_text = (
                f"📧 Username: @{target_username}\n"
                f"👨‍💼 Rank: {rank_text}\n"
                f"🆔 ID: `{user_data['user_id']}`\n"
                f"📛 Name: {user_data['first_name']}"
            )
            if not user_data['rank'] in ['gadmin', 'operator']:
                info_text += (
                    f"📊 Status: {banned_status}\n"
                    f"💢 Warnings: {user_data['warns']}/{Config.MAX_WARN}"
                )

            embed = discord.Embed(
                title="👤 **User Information**\n\n",
                description=info_text,
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="brbhelp", description="Show help for all commands")
        async def help_command(interaction: discord.Interaction):
            """Показать справку по командам"""
            if not await self.check_admin_role(interaction):
                return

            help_text = """
**Global Admin Commands:**
`/bantg <@username> [time] [reason]` - Ban user
`/unban <@username>` - Unban user
`/warn <@username> [reason]` - Warn user
`/unwarn <@username>` - Remove warning
`/botlist` - Show bot list

**Operators Commands:**
`/alarm <message>` - Mass notification
`/stats` - Show system statistics
`/list <type>` - Show user lists (ladmin, gadmin, operator)
`/getinfo <@username>` - Get user info
`/promote <@username>` - Promote user
`/demote <@username>` - Demote user
`/addbot <name> <@username> <type>` - Add new bot
`/removebot <name>` - Remove bot
`/startbot <name>` - Start bot
`/stopbot <name>` - Stop bot

**Utilities:**
`/brbhelp` - Show this help
            """
            embed = discord.Embed(
                title='🤖 **BRB Bot Commands:**',
                description=help_text,
                color=discord.Color.brand_green()
            )
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="list", description="Show user lists")
        @app_commands.describe(list_type="List type (ladmin, gadmin, operator)")
        async def list_command(interaction: discord.Interaction, list_type: str):
            """Показать списки пользователей"""
            if not await self.check_op_role(interaction):
                return

            list_type = list_type.lower()
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
                await send_error(interaction, "❌ Unknown list type! Available: ladmin, gadmin, operator")
                return

            if text == '❌ Список пуст':
                embed = discord.Embed(
                    title=text,
                    color=discord.Color.brand_red()
                )

            else:
                list_text = text.split('</b>')
                embed = discord.Embed(
                    title=list_text[0][3:],
                    description=list_text[1],
                    color=discord.Color.blue()
                )
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="promote", description="Promote user to higher rank")
        @app_commands.describe(username="Telegram username")
        async def promote(interaction: discord.Interaction, username: str):
            """Повышение пользователя"""
            if not await self.check_op_role(interaction):
                return

            target_username = Utils.extract_username(username)
            if not target_username:
                await send_error(interaction, "❌ Invalid username!")
                return

            # Проверяем существование пользователя
            if not Database.user_exists(target_username):
                await send_error(interaction, "❌ User not found in system!")
                return

            # Проверяем бан целевого пользователя
            if Database.is_banned(target_username):
                await send_error(interaction, "❌ Cannot promote banned user!")
                return

            # Создаем меню выбора ранга
            embed = discord.Embed(
                title=f"Select rank for @{target_username}:",
                description="Choose the rank to promote the user to",
                color=discord.Color.blue()
            )

            await interaction.response.send_message(embed=embed, view=RankSelectionView(target_username))
            logger.info(f"DISCORD: {interaction.user.name} started promotion for @{target_username}")

        @self.bot.tree.command(name="removebot", description="Remove bot from system")
        @app_commands.describe(name="Bot name")
        async def removebot(interaction: discord.Interaction, name: str):
            """Удаление бота"""
            if not await self.check_op_role(interaction):
                return

            if Database.remove_bot(name):
                embed = discord.Embed(
                    title=f"✅ Bot '{name}' successfully removed!",
                    color=discord.Color.dark_gray()
                )
                await interaction.response.send_message(embed=embed)
                logger.info(f"DISCORD: {interaction.user.name} removed bot {name}")
            else:
                await send_error(interaction,f"❌ Bot '{name}' not found!")

        @self.bot.tree.command(name="startbot", description="Start bot")
        @app_commands.describe(name="Bot name")
        async def startbot(interaction: discord.Interaction, name: str):
            """Запуск бота"""
            if not await self.check_op_role(interaction):
                return

            result = Utils.start_bot(name)

            embed = discord.Embed(
                title=result,
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"DISCORD: {interaction.user.name} started bot {name} - {result}")

        @self.bot.tree.command(name="stats", description="Show system statistics")
        async def stats(interaction: discord.Interaction):
            """Статистика системы"""
            if not await self.check_op_role(interaction):
                return

            stats_text = Utils.get_stats().split('</b>')
            embed = discord.Embed(
                title='📊 Статистика системы',
                description=stats_text[1],
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="stopbot", description="Stop bot")
        @app_commands.describe(name="Bot name")
        async def stopbot(interaction: discord.Interaction, name: str):
            """Остановка бота"""
            if not await self.check_op_role(interaction):
                return

            result = Utils.stop_bot(name)
            embed = discord.Embed(
                title=result,
                color=discord.Color.dark_gray()
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"DISCORD: {interaction.user.name} stopped bot {name} - {result}")

        @self.bot.tree.command(name="unban", description="Unban user")
        @app_commands.describe(username="Telegram username")
        async def unban(interaction: discord.Interaction, username: str):
            """Разбан пользователя"""
            if not await self.check_admin_role(interaction):
                return

            target_username = Utils.extract_username(username)
            if not target_username:
                await send_error(interaction, "❌ Invalid username!")
                return

            # Проверяем существование пользователя
            if not Database.user_exists(target_username):
                await send_error(interaction, "❌ User not found in system!")
                return

            # Разбаниваем пользователя
            if Database.unban_user(target_username):
                # Отправляем уведомление пользователю
                unban_message = "✅ **You have been unbanned from our bot network!**"
                Utils.send_message_to_user(None, target_username, unban_message)
                embed = discord.Embed(
                    title=f"✅ @{target_username} unbanned",
                    color=discord.Color.brand_red()
                )
                await interaction.response.send_message(embed=embed)
                logger.info(f"DISCORD: {interaction.user.name} unbanned @{target_username}")
            else:
                await send_error(interaction,f"❌ Failed to unban @{target_username}")

        @self.bot.tree.command(name="unwarn", description="Remove warning from user")
        @app_commands.describe(username="Telegram username")
        async def unwarn(interaction: discord.Interaction, username: str):
            """Снятие предупреждения"""
            if not await self.check_admin_role(interaction):
                return

            target_username = Utils.extract_username(username)
            if not target_username:
                await send_error(interaction, "❌ Invalid username!")
                return

            # Проверяем существование пользователя
            if not Database.user_exists(target_username):
                await send_error(interaction, "❌ User not found in system!")
                return

            # Снимаем варн
            if Database.remove_warn(target_username):
                # Отправляем уведомление пользователю
                user_data = Database.get_user(target_username)
                unwarn_message = (
                    "✅ **Warning removed!**\n\n"
                    f"📊 Current warnings: {user_data['warns']}/{Config.MAX_WARN}"
                )
                Utils.send_message_to_user(None, target_username, unwarn_message)

                embed = discord.Embed(
                    title=f"✅ Warning removed from @{target_username} ({user_data['warns']}/{Config.MAX_WARN})",
                    color=discord.Color.brand_red()
                )
                await interaction.response.send_message(embed=embed)
                logger.info(f"DISCORD: {interaction.user.name} removed warning from @{target_username}")
            else:
                await send_error(interaction,f"❌ Failed to remove warning from @{target_username}")

        @self.bot.tree.command(name="warn", description="Warn user")
        @app_commands.describe(username="Telegram username", reason="Warning reason")
        async def warn(interaction: discord.Interaction, username: str, reason: str = ""):
            """Выдача предупреждения"""
            if not await self.check_admin_role(interaction):
                return

            target_username = Utils.extract_username(username)
            if not target_username:
                await send_error(interaction, "❌ Invalid username!")
                return

            # Проверяем существование пользователя
            if not Database.user_exists(target_username):
                await send_error(interaction, "❌ User not found in system!")
                return

            # Проверяем права на варн
            can_warn, error_msg = Database.can_warn_user(interaction.user.name, target_username)
            if not can_warn:
                await send_error(interaction,f"❌ {error_msg}")
                return

            # Выдаем предупреждение
            success, result = Database.add_warn(target_username, interaction.user.name, reason)
            if success:
                if result == "banned":
                    await interaction.response.send_message(
                        f"✅ @{target_username} received warning and was automatically banned for reaching limit")
                else:
                    # Отправляем уведомление пользователю
                    user_data = Database.get_user(target_username)
                    warn_message = (
                        "⚠️ **You received a warning!**\n\n"
                        f"📊 Current count: {user_data['warns']}/{Config.MAX_WARN}\n"
                        f"👮 Issued by: {interaction.user.name}\n"
                    )
                    if reason:
                        warn_message += f"📝 Reason: {reason}"

                    Utils.send_message_to_user(None, target_username, warn_message)

                    embed = discord.Embed(
                        title=f"✅ @{target_username} received warning ({user_data['warns']}/{Config.MAX_WARN})",
                        color=discord.Color.brand_red()
                    )
                    await interaction.response.send_message(embed=embed)
                logger.info(f"DISCORD: {interaction.user.name} warned @{target_username}")
            else:
                await send_error(interaction,f"❌ {result}")

    def setup_events(self):
        """Настройка событий Discord бота"""

        @self.bot.event
        async def on_ready():
            logger.info(f'DISCORD: Logged in as {self.bot.user.name}')
            print(f'🤖 Discord bot {self.bot.user.name} is ready!')
            # Синхронизируем команды при запуске
            try:
                synced = await self.bot.tree.sync()
                logger.info(f"DISCORD: Synced {len(synced)} commands")
                print(f"✅ Synced {len(synced)} Discord commands")
            except Exception as e:
                logger.error(f"DISCORD: Error syncing commands: {e}")
                print(f"❌ Error syncing Discord commands: {e}")

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                embed = discord.Embed(
                    title="❌ Command not found! Use `/brbhelp` for available commands.",
                    color=discord.Color.brand_red()
                )
                await ctx.send(embed=embed)
            elif isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(
                    title="❌ Missing required arguments! Use `/brbhelp` for command usage.",
                    color=discord.Color.brand_red()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"❌ Error executing command:",
                    description=error,
                    color=discord.Color.brand_red()
                )
                await ctx.send(embed=embed)
                logger.error(f"DISCORD: Command error: {error}")

    async def check_op_role(self, interaction: discord.Interaction):
        """Проверка роли Operator у пользователя"""
        # Проверяем, есть ли у пользователя роль Operator
        op_role = discord.utils.get(interaction.user.roles, name="Operator")
        if not op_role:
            await send_error(interaction, "❌ Access denied! Only users with 'Operator' role can use this bot.")
            logger.warning(f"DISCORD: Access denied for {interaction.user.name} - No Operator role")
            return False
        return True

    async def check_admin_role(self, interaction: discord.Interaction):
        """Проверка роли gadmin у пользователя"""
        # Проверяем, есть ли у пользователя роль Global Admin
        gadmin_role = discord.utils.get(interaction.user.roles, name="Global Admin")
        op_role = discord.utils.get(interaction.user.roles, name="Operator")
        if not gadmin_role and not op_role:
            await send_error(interaction, "❌ Access denied! Only users with 'Global Admin' role or higher can use this bot.")
            logger.warning(f"DISCORD: Access denied for {interaction.user.name} - No gadmin role")
            return False
        return True

    def run(self):
        """Запуск Discord бота"""
        try:
            # Настраиваем команды перед запуском
            asyncio.run(self.setup_commands())
            self.bot.run(Config.DS_BRB_TOKEN)
        except Exception as e:
            logger.error(f"DISCORD: Error starting bot: {e}")
            print(f"❌ Discord bot error: {e}")


class RankSelectionView(discord.ui.View):
    """View для выбора ранга при повышении пользователя"""

    def __init__(self, target_username):
        super().__init__()
        self.target_username = target_username

    @discord.ui.button(label="Local Admin", style=discord.ButtonStyle.primary, emoji="👨‍💼")
    async def local_admin_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_promotion(interaction, "ladmin")

    @discord.ui.button(label="Global Admin", style=discord.ButtonStyle.primary, emoji="👑")
    async def global_admin_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_promotion(interaction, "gadmin")

    async def handle_promotion(self, interaction, rank):
        """Обработка выбора ранга"""
        # Проверяем роль Dev
        dev_role = discord.utils.get(interaction.user.roles, name="Dev")
        if not dev_role:
            await send_error(interaction, "❌ Access denied! Only users with 'Dev' role can use this bot.")
            return

        success = False
        message = ""

        if rank == "ladmin":
            # Для локальных админов нужно выбрать бота
            bots = Database.get_all_bots()
            if not bots:
                await send_error(interaction, "❌ No available bots!")
                return

            # Создаем меню выбора бота
            embed = discord.Embed(
                title=f"Select bot for @{self.target_username}:",
                description="Choose the bot to assign as local administrator",
                color=discord.Color.blue()
            )

            view = BotSelectionView(self.target_username)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return

        elif rank == "gadmin":
            success = Database.add_global_admin(self.target_username)
            message = f"✅ @{self.target_username} promoted to Global Admin" if success else f"❌ Failed to promote @{self.target_username}"

        if success:
            logger.info(f"DISCORD: {interaction.user.name} promoted @{self.target_username} to {rank}")

        await interaction.response.send_message(message, ephemeral=True)
        # Обновляем оригинальное сообщение
        await interaction.message.edit(content=message, view=None)


class BotSelectionView(discord.ui.View):
    """View для выбора бота при назначении локального админа"""

    def __init__(self, target_username):
        super().__init__()
        self.target_username = target_username
        self.add_bot_buttons()

    def add_bot_buttons(self):
        """Добавляем кнопки для выбора бота"""
        bots = Database.get_all_bots()
        for bot_name in bots.keys():
            self.add_item(BotButton(bot_name, self.target_username))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=4)
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_error(interaction, "❌ Action cancelled")
        await interaction.message.delete()


class BotButton(discord.ui.Button):
    """Кнопка выбора бота"""

    def __init__(self, bot_name, target_username):
        super().__init__(label=f"🤖 {bot_name}", style=discord.ButtonStyle.secondary)
        self.bot_name = bot_name
        self.target_username = target_username

    async def callback(self, interaction: discord.Interaction):
        # Проверяем роль Dev
        dev_role = discord.utils.get(interaction.user.roles, name="Dev")
        if not dev_role:
            await send_error(interaction, "❌ Access denied! Only users with 'Dev' role can use this bot.")
            return

        # Назначаем локального админа
        success = Database.add_ladmin_to_bot(self.target_username, self.bot_name)

        if success:
            message = f"✅ @{self.target_username} assigned as Local Admin for {self.bot_name}"
            logger.info(
                f"DISCORD: {interaction.user.name} assigned @{self.target_username} as local admin for {self.bot_name}")
        else:
            message = f"ℹ️ @{self.target_username} is already Local Admin for {self.bot_name}"

        await interaction.response.send_message(message, ephemeral=True)
        await interaction.message.delete()


# Функция для запуска Discord бота в отдельном потоке
def start_discord_bot():
    """Запуск Discord бота"""
    discord_bot = DiscordBot()
    discord_bot.run()


if __name__ == "__main__":
    start_discord_bot()