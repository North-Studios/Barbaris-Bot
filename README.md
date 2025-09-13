# 🤖 Barbariska Bot v4.2

Telegram and Discord bot for managing users and bots with enhanced role-based access control and improved Discord integration.

---

## ✨ New Features in v4.2

* **🎯 Enhanced Role System** - Two-tier Discord role system (Operator + Global Admin)
* **🔒 Improved Security** - Separate permission levels for different commands
* **👮‍♂️ Granular Access Control** - Different Discord roles for different command sets
* **📊 Better Error Handling** - Improved user feedback and error messages
* **🔄 Streamlined Command Structure** - More logical command organization

---

## 📌 Command Changes in v4.2

### Discord Role Requirements Changed:

**v4.1:** Only "Dev" role could access all commands  
**v4.2:** Two distinct roles with different permissions:

* **👨‍💻 Operator Role** - Basic management commands
* **🔧 Global Admin Role** - Advanced administrative commands + Operator access

### Discord Command Access Matrix:

#### 👨‍💻 Operator Commands (Available to both roles):
* `/alarm <message>` - Mass notification
* `/stats` - Show system statistics  
* `/list <type>` - Show user lists (ladmin, gadmin, operator)
* `/getinfo @username` - Get user info
* `/promote @username` - Promote user
* `/demote @username` - Demote user
* `/addbot <name> <@username> <type>` - Add new bot
* `/removebot <name>` - Remove bot
* `/startbot <name>` - Start bot
* `/stopbot <name>` - Stop bot

#### 🔧 Global Admin Commands (Additional to Operator):
* `/bantg <@username> [time] [reason]` - Ban user
* `/unban @username` - Unban user  
* `/warn @username [reason]` - Warn user
* `/unwarn @username` - Remove warning
* `/botlist` - Show bot list

---

## ⚙️ Installation and Setup

### 1. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure `.env` File:
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

### 3. Discord Server Setup:

**Create Required Roles:**
- `Operator` - Basic management access
- `Global Admin` - Full administrative access

**Bot Permissions Required:**
- `Applications.commands`
- `Send Messages` 
- `Read Message History`
- `Use Slash Commands`

**Enable Intents:**
- `SERVER MEMBERS INTENT`
- `MESSAGE CONTENT INTENT`

### 4. Run the Bot:
```bash
python main.py
```

---

## 🗂️ Project Structure v4.2

```
├── main.py                 # Main entry point
├── discord_bot.py         # Updated Discord bot (v4.2)
├── discord_bot v4.1.py    # Previous version (backup)
├── handlers.py            # Telegram command handlers
├── keyboards.py           # Telegram keyboards
├── database.py            # JSON database operations
├── utils.py               # Utilities and functions
├── config.py              # Configuration and logging
├── console.py             # Console commands
├── hook-env.py           # PyInstaller hook
├── requirements.txt       # Dependencies
├── logs/                  # Logs directory
├── data/                  # Data files (JSON)
└── bots/                  # Executable bot files
```

---

## 🔧 Key Technical Changes

### Security Enhancements:
- **Dual role verification** in Discord (`check_op_role()` + `check_admin_role()`)
- **Command-specific access control** based on role hierarchy
- **Improved error messages** for permission denied cases

### Code Improvements:
- **Separated permission checks** for different command categories
- **Better role validation** with specific error messages
- **Enhanced logging** for Discord role-based access attempts

### User Experience:
- **Clearer help text** showing command categories by role
- **Better feedback** when users lack required permissions
- **Consistent error handling** across both Telegram and Discord

---

## 🚀 Migration from v4.1 to v4.2

### Required Changes:
1. **Create new Discord roles**: `Operator` and `Global Admin`
2. **Assign roles appropriately** to team members
3. **Update role mentions** in documentation
4. **Verify permission levels** for all users

### Backward Compatibility:
- ✅ Telegram commands unchanged
- ✅ Database structure unchanged  
- ✅ Console commands unchanged
- ✅ Configuration format unchanged

---

## 📝 Version History

**v4.2** - Enhanced Discord role system, granular permissions, improved security
**v4.1** - Initial Discord integration with single "Dev" role
**v3.6** - Telegram-only version with basic functionality

---

## 🆘 Support

If problems occur:

1. Check all dependencies
2. Ensure tokens in `.env` are correct
3. Verify bot permissions on Discord server
4. Ensure "Dev" role is created and assigned

For diagnostics, use logs in the `logs/` directory
