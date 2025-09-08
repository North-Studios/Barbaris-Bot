# 🤖 Barbariska Bot v4.1

Telegram and Discord bot for managing users and bots. Supports role system, access rights, database operations, console commands, and Discord integration.

---

## ✨ New Features in v4.1

* **🤖 Discord Integration** - full synchronization of commands between Telegram and Discord
* **👮‍♂️ Discord Role System** - access only for users with the "Dev" role
* **🔄 Automatic Command Sync** - slash commands in Discord
* **📊 Improved Statistics** - extended system information
* **🎮 Interactive Menus** - selection buttons in Discord

---

## 📌 Commands

### 👤 Basic Commands (Telegram & Discord)

* **`/start`**, **`/help`** - greeting and help
* **`/me`** - info about yourself
* **`/stats`** - system statistics
* **`/getinfo @username`** - user information

### 🔧 Administrative Commands

* **`/list [type]`** - view lists (ladmin, gadmin, operator)
* **`/alarm [text]`** - mass notification
* **`/promote @username`** - promote a user
* **`/demote @username`** - demote a user
* **`/ban @username [time] [reason]`** - block a user
* **`/unban @username`** - unblock a user
* **`/warn @username [reason]`** - issue a warning
* **`/unwarn @username`** - remove a warning

### 🤖 Bot Management

* **`/addbot <name> @username <type>`** - add a bot
* **`/removebot <name>`** - remove a bot
* **`/startbot <name>`** - start a bot
* **`/stopbot <name>`** - stop a bot
* **`/botlist`** - list all bots

### 🖥️ Console Commands

* **`/op @username`** - assign operator
* **`/unop @username`** - remove operator

---

## 👥 Role System

### Telegram Roles:

* **👤 User** - regular user
* **🪛 Local Admin (ladmin)** - local rights for a specific bot
* **🔧 Global Admin (gadmin)** - extended rights
* **⚡ Operator (operator)** - full access to management
* **🌟 Super-Operator** - main administrator (configured in `.env`)

### Discord Roles:

* **👨‍💻 Dev** - required role for bot commands

---

## ⚙️ Installation and Launch

1. Clone the project:

```bash
git clone <repo_url>
cd brb-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure `.env` file:

```env
BRB_TOKEN=your_telegram_bot_token
DS_BRB_TOKEN=your_discord_bot_token
SUPER_OPERATOR=your_username
MAX_WARN=3
DEFAULT_BAN_TIME=0
DATA_DIR=data
LOGS_DIR=logs
BOTS_DIR=bots
```

4. Configure Discord bot:

   * Create an application on [Discord Developer Portal](https://discord.com/developers/applications)
   * Enable `SERVER MEMBERS INTENT` and `MESSAGE CONTENT INTENT`
   * Create "Dev" role on the server
   * Assign the role to users who should have access to the bot

5. Run:

```bash
python main.py
```

---

## 🗂️ Project Structure

```
├── main.py              # Entry point
├── discord_bot.py       # Discord bot and commands
├── handlers.py          # Telegram command handlers
├── keyboards.py         # Telegram keyboards
├── database.py          # Work with JSON database
├── utils.py             # Utilities and functions
├── config.py            # Configuration and logging
├── console.py           # Console commands
├── hook-env.py          # Script for PyInstaller
├── requirements.txt     # Dependencies
├── logs/                # Logs directory
├── data/                # Data (JSON files)
└── bots/                # Executable bot files
```

---

## 🔧 Discord Setup

### Required Bot Permissions:

* `Applications.commands`
* `Send Messages`
* `Read Message History`
* `Use Slash Commands`

### Required Intents:

* `SERVER MEMBERS INTENT`
* `MESSAGE CONTENT INTENT`

### Discord Commands:

All commands are available via slash (`/`) with autocomplete:

* `/addbot` - add a bot
* `/alarm` - mass notification
* `/bantg` - ban a Telegram user
* `/botlist` - list of bots
* And all other commands from Telegram

---

## 🚀 Features v4.1

* **🔐 Security** - double rights check (Telegram + Discord)
* **📱 Cross-platform** - works via Telegram and Discord
* **⚡ Performance** - multithreaded architecture
* **📊 Monitoring** - detailed logging of all actions
* **🎯 Usability** - intuitive interfaces and hints

---

## 📝 Versions

**v4.1** - Full Discord integration, interactive menus, improved security
**v3.6** - Basic version with Telegram functionality

---

## 🆘 Support

If problems occur:

1. Check all dependencies
2. Ensure tokens in `.env` are correct
3. Verify bot permissions on Discord server
4. Ensure "Dev" role is created and assigned

For diagnostics, use logs in the `logs/` directory
