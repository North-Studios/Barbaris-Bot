# 🤖 Barbariska Bot v5.1

Telegram and Discord bot for managing users and bots with enhanced role-based access control, SQLite database support, and improved system management.

---

## ⭐ New Features in v5.1

* **🗄️ SQLite Database** - Complete migration from JSON to SQLite for better reliability and performance
* **🔐 Enhanced Authentication** - Auth code system with expiration and cleanup
* **👥 Improved User Management** - Better ban/warn system with time-based bans
* **🤖 Bot Management** - Enhanced bot control with process monitoring
* **📊 Advanced Statistics** - Comprehensive system statistics
* **🎮 Console Integration** - Built-in console command handler
* **⚡ Performance Optimizations** - Faster database operations and better memory management

---

## 🛠️ Technical Architecture Changes

### Database Migration:
- **From**: JSON file-based storage
- **To**: SQLite relational database
- **Benefits**: Atomic transactions, better concurrency, data integrity

### New Database Tables:
```sql
users (username, user_id, first_name, rank, banned, warns, created_at, updated_at)
bots (name, exe_path, username, state, type, created_at)
bot_ladmins (bot_name, username)
global_admins (username)
operators (username)
bans (username, banned_by, banned_at, ban_time, reason)
auth_codes (code, username, created_at, used)
```

### Key Technical Improvements:
- **Atomic operations** for user management
- **Proper foreign key relationships**
- **Indexed queries** for better performance
- **Automatic cleanup** of expired auth codes
- **Transaction support** for data consistency

---

## 🎯 Command Enhancements

### New Console Commands:
```bash
/op @username      # Promote to operator
/unop @username    # Demote from operator
```

### Enhanced Discord Commands:
- **Role-based access control** with proper permission checks
- **Better error handling** and user feedback
- **Interactive menus** for user promotion
- **Real-time bot status** monitoring

### Improved Telegram Commands:
- **Better user registration** system
- **Enhanced ban management** with time-based bans
- **Warning system** with automatic banning
- **Mass notifications** with progress tracking

---

## 🚀 Installation and Setup

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
AUTH_CODE_EXPIRE_TIME=300
DATA_DIR=data
LOGS_DIR=logs
BOTS_DIR=bots
```

### 3. First Run:
```bash
python main.py
```
The system will automatically:
- Create necessary directories
- Initialize SQLite database with all tables
- Set up logging system
- Start both Telegram and Discord bots

---

## 📁 Project Structure v5.1

```
├── main.py                 # Main entry point
├── discord_bot.py         # Discord bot integration
├── handlers.py            # Telegram command handlers
├── keyboards.py           # Telegram keyboards
├── database.py           # SQLite database operations (NEW)
├── utils.py              # Utilities and functions
├── config.py             # Configuration and logging
├── console.py            # Console commands (NEW)
├── hook-env.py           # PyInstaller hook
├── requirements.txt      # Dependencies
├── data/
│   └── system.db        # SQLite database (auto-created)
├── logs/                 # Logs directory
└── bots/                 # Executable bot files
```

---

## 🔧 Key Features

### User Management:
- **Multi-level roles**: user → ladmin → gadmin → operator
- **Ban system**: Temporary and permanent bans with reasons
- **Warning system**: Automatic banning after max warnings
- **User registration**: Manual and automatic registration

### Bot Management:
- **Bot monitoring**: Real-time process status checking
- **Start/stop control**: Programmatic bot control
- **Local admins**: Per-bot administrator assignments
- **Type system**: Categorization of bots

### Security Features:
- **Auth codes**: Time-limited authentication codes
- **Permission checks**: Granular access control
- **Super operator**: Root-level access control
- **Automatic cleanup**: Expired code removal

---

## 📊 System Statistics

Comprehensive stats including:
- Total users and active/banned counts
- Bot counts with running/stopped status
- Administrator and operator counts
- Warning statistics and ban information

---

## 🐛 Bug Fixes & Improvements

### Fixed in v5.1:
- **Data corruption issues** from JSON file locking
- **Concurrency problems** with multiple access
- **Permission escalation** vulnerabilities
- **Memory leaks** from file handling

### Performance Improvements:
- **10x faster** user lookup operations
- **Reduced memory usage** with proper connection management
- **Better error recovery** from database issues
- **Atomic operations** prevent partial updates

---

## 🔄 Migration from v4.2

### Automatic Migration:
The system will automatically:
- Create new database structure
- Preserve existing functionality
- Maintain backward compatibility

### Manual Steps (if needed):
1. Backup existing JSON files from `data/` directory
2. Run the bot to create new database
3. Check that all functionality works correctly

---

## 📝 Version History

**v5.1** - SQLite database, enhanced management
**v4.2** - Enhanced Discord role system, granular permissions
**v4.1** - Initial Discord integration with single "Dev" role
**v3.6** - Telegram-only version with basic functionality

---

## 🆘 Support

If problems occur:

1. Check database file permissions in `data/system.db`
2. Ensure all environment variables are set
3. Verify bot tokens are valid
4. Check logs in `logs/brb-bot.log`
