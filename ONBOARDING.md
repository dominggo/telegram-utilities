# Telegram Utilities - Onboarding Guide

Welcome! This guide will help you get started with the Telegram Utilities project in minutes.

## Quick Start (5 minutes)

### 1. Prerequisites Check

Before you begin, make sure you have:
- [ ] Python 3.8 or higher installed
- [ ] MySQL 8.0+ installed and running
- [ ] Telegram account with phone number
- [ ] Telegram API credentials (get from https://my.telegram.org)

### 2. Installation

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd 01_telegram

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configuration Setup

Create your configuration file from the template:

```bash
# Copy the example configuration
cp my.json.example my.json
```

Edit `my.json` with your credentials:

```json
{
  "database": {
    "host": "localhost",
    "user": "telegram_user",
    "password": "your_mysql_password",
    "database": "telegram_utilities"
  },
  "telegram": {
    "api_id": "12345678",
    "api_hash": "your_api_hash_from_telegram",
    "phone": "+1234567890"
  }
}
```

**Important**: Never commit `my.json` - it's in `.gitignore` for security.

### 4. Database Setup

Initialize the database:

```bash
# Test database connection and create tables
python db_connection.py
```

If you see "Database initialized successfully!" you're ready to go!

### 5. First Run

Test your setup by listing your Telegram chats:

```bash
python telegram_downloader.py --list-chats
```

On first run, Telegram will send you an authentication code. Enter it to complete the session setup.

## Understanding the Project

### What This Project Does

This toolkit helps you:
1. **Download media** from Telegram chats (photos, videos, documents)
2. **Track operations** in a MySQL database across multiple machines
3. **Manage messages** with planned analyzer, archiver, and deleter tools

### Project Structure

```
01_telegram/
├── telegram_downloader.py       # Main download tool (READY)
├── db_connection.py              # Database connection module
├── database_schema.sql           # Fresh database schema
├── database_migration_*.sql     # Migration scripts
├── my.json                       # Your config (NOT in git)
├── my.json.example              # Config template
├── requirements.txt             # Python dependencies
├── README.md                    # User documentation
├── PROJECT_CONTEXT.md           # Detailed technical context
└── ONBOARDING.md               # This file
```

### Key Concepts

**Hostname Tracking**: Every operation records which machine performed it, enabling multi-machine coordination.

**Idempotent Operations**: You can re-scan the same chat multiple times safely - the database uses `ON DUPLICATE KEY UPDATE`.

**Graceful Degradation**: Tools work even if database connection fails (though tracking is lost).

## Common Tasks

### Download Photos from a Chat

```bash
# First, get your chat ID
python telegram_downloader.py --list-chats

# Download all photos from a specific chat
python telegram_downloader.py --chat-id CHAT_ID
```

### Download Videos from Date Range

```bash
python telegram_downloader.py --chat-id CHAT_ID \
  --media-type video \
  --start-date 2024-01-01 \
  --end-date 2024-12-31
```

### Download Specific Document Types

```bash
# Download only PDFs
python telegram_downloader.py --chat-id CHAT_ID \
  --media-type document \
  --extensions pdf

# Download PDFs and Word documents
python telegram_downloader.py --chat-id CHAT_ID \
  --media-type document \
  --extensions pdf,docx,doc
```

### Download Everything

```bash
python telegram_downloader.py --chat-id CHAT_ID --media-type all
```

## How to Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click on "API development tools"
4. Fill in the application details:
   - App title: "Telegram Utilities" (or any name)
   - Short name: "tg_utils" (or any name)
   - Platform: Desktop
5. Click "Create application"
6. Copy your `api_id` and `api_hash` to `my.json`

## Database Overview

### Tables You'll Use

- **messages**: All retrieved messages with media metadata
- **download_log**: Every download attempt (success/failure)
- **chats**: Chat/group information
- **action_log**: All tool operations for auditing

### Viewing Database Data

```bash
# Connect to MySQL
mysql -u telegram_user -p telegram_utilities

# View recent downloads
SELECT message_id, chat_id, media_type, status, download_hostname
FROM messages
WHERE status = 'downloaded'
ORDER BY downloaded_datetime DESC
LIMIT 10;

# View download success rate
SELECT download_status, COUNT(*) as count
FROM download_log
GROUP BY download_status;
```

## Troubleshooting

### Issue: "Database connection failed"

**Solution**: Check that:
1. MySQL is running
2. Credentials in `my.json` are correct
3. Database `telegram_utilities` exists
4. User has proper permissions

Run `python db_connection.py` to test and auto-create tables.

### Issue: "Can't find chat ID"

**Solution**: Use `--list-chats` to see all available chats:
```bash
python telegram_downloader.py --list-chats
```

### Issue: "Telegram authentication failed"

**Solution**: Delete the session file and try again:
```bash
# Remove old session
rm session_*

# Re-run the tool - you'll get a new auth code
python telegram_downloader.py --list-chats
```

### Issue: "Database is locked" error during disconnect

**Don't worry!** This is normal and harmless. It's the SQLite session file being busy during cleanup. Already handled in code.

### Issue: Network timeouts during downloads

**Already handled!** The tool automatically retries failed downloads 3 times with 2-second delays.

## Development Workflow

### Making Changes

1. **Read context first**: Check `PROJECT_CONTEXT.md` for technical details
2. **Create feature branch**: `git checkout -b feature-name` (optional for solo dev)
3. **Make changes**: Follow the code patterns documented in PROJECT_CONTEXT.md
4. **Test locally**: Run the tool to verify changes work
5. **Commit**: Use the commit format from PROJECT_CONTEXT.md
6. **Push**: `git push origin master` (or your branch)

### Adding a New Tool

Follow this pattern (example: `message_analyzer.py`):

```python
#!/usr/bin/env python3
import socket
from db_connection import DatabaseConnection

class MessageAnalyzer:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.db = DatabaseConnection()

    def analyze(self):
        # Your logic here
        # Always record hostname in action_log
        pass

if __name__ == '__main__':
    analyzer = MessageAnalyzer()
    analyzer.analyze()
```

### Database Migrations

If you need to change the database schema:

1. Create migration file: `database_migration_002_description.sql`
2. Use `IF NOT EXISTS` for safety
3. Test on a copy first
4. Update PROJECT_CONTEXT.md with migration instructions

## Next Steps

Now that you're set up, you can:

1. **Use the downloader**: Start downloading media from your Telegram chats
2. **Explore the database**: Check the data being tracked
3. **Build new tools**: Message analyzer, archiver, or deleter (see PROJECT_CONTEXT.md)
4. **Contribute**: Add features or improvements

## Resources

- **README.md**: User documentation and examples
- **PROJECT_CONTEXT.md**: Complete technical documentation for developers
- **my.json.example**: Configuration template
- **Telethon docs**: https://docs.telethon.dev/
- **MySQL docs**: https://dev.mysql.com/doc/

## Getting Help

If you run into issues:

1. Check the "Troubleshooting Guide" in PROJECT_CONTEXT.md
2. Review error messages carefully - most are self-explanatory
3. Check that your configuration is correct
4. Try with `--list-chats` first to verify basic connectivity

## Project Status

**Current Version**: 1.0 (Database integration complete)

**Production Ready**:
- ✅ telegram_downloader.py - Fully tested and working

**Planned** (not yet implemented):
- ⏳ Message Analyzer - Analyze message patterns and statistics
- ⏳ Message Archiver - Archive messages for backup
- ⏳ Message Deleter - Bulk delete messages by criteria

---

**Welcome aboard!** You're ready to use the Telegram Utilities toolkit.

For detailed technical information, see PROJECT_CONTEXT.md.
