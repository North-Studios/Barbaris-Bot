# 🤖 Barbariska Bot v3.6

Telegram bot for user administration and bot management. Supports roles, permission system, database operations, and console commands.

---

## ✨ Features

### 📌 Commands

#### 👤 Basic Commands

* **`/start` and `/help`** — greeting and help message.
* **`/me`** — get info about yourself.

#### 🔧 Administrator Commands

* **`/stats`** — view statistics.
* **`/getinfo @username`** — get user information.
* **`/list`** — view lists.
* **`/alarm [text]`** — send a broadcast message.
* **`/promote @username` / `/demote @username`** — grant or revoke privileges.
* **`/ban @username` / `/unban @username`** — block or unblock a user.
* **`/warn @username` / `/unwarn @username`** — issue or remove warnings.
* **`/addbot` / `/removebot`** — add or remove a bot from the system.
* **`/startbot` / `/stopbot`** — start or stop a bot.

### 👥 Roles

* **User** — standard role.
* **Local Admin (ladmin)** — limited rights.
* **Global Admin (gadmin)** — extended rights.
* **Operator (operator)** — full access to bot management.
* **Super-Operator** — main administrator (configured via `.env`).

### 🖥️ Console Commands

* **`/op @username`** — grant operator role.
* **`/unop @username`** — revoke operator role.

### 🗂️ Keyboards

* Main menu (depends on the role).
* View lists of local and global admins.

### 💾 Database

* Users (`users.json`).
* Administrators (`admins.json`).
* Bots and their statuses (`bots_data.json`).
* Banned users (`banned.json`).

### 🔧 Utilities

* Extract username from text.
* Check bot process status (`running`, `stopped`, `not_found`).

---

## ⚙️ Installation and Run

1. Clone the project:

```bash
 git clone <repo_url>
 cd brb-bot
```

2. Install dependencies:

```bash
 pip install -r requirements.txt
```

3. Create a `.env` file and specify the parameters:

```env
BRB_TOKEN=your_bot_token
SUPER_OPERATOR=your_username
MAX_WARN=3
DEFAULT_BAN_TIME=0
```

4. Run the bot:

```bash
 python main.py
```

---

## 🗃️ Project Structure

```
├── main.py          # Entry point
├── handlers.py      # Command and message handlers
├── keyboards.py     # Telegram keyboards
├── database.py      # Work with JSON database
├── utils.py         # Utility functions
├── config.py        # Configuration and logging
├── console.py       # Console commands
├── hook-env.py      # PyInstaller script
├── logs/            # Directory for log files
└── data/            # Directory for data files
```

---

## 🏷️ Version

**Barbariska Bot v3.6**
