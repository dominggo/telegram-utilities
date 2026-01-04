# Telegram Utilities - Project Context

## Project Overview

This is a Python-based toolkit for managing Telegram messages and media across multiple machines. It uses a centralized MySQL database to track all operations, enabling cross-machine coordination and historical tracking.

## Current Status

**Version**: 1.0 (Database integration complete)
**Status**: Production-ready for download tool; other tools planned

### Completed Features
- ✅ Telegram media downloader with parallel downloads (5 concurrent)
- ✅ MySQL database integration with hostname tracking
- ✅ Support for photos, videos, and documents with extension filtering
- ✅ Automatic retry on network failures (3 attempts)
- ✅ Date/time-stamped filenames to prevent overwrites
- ✅ Real-time progress tracking (0%, 25%, 50%, 75%, 100%)
- ✅ Database migration script for upgrades

### Planned Tools (Not Yet Implemented)
- ⏳ Message Analyzer - Analyze message patterns and statistics
- ⏳ Message Archiver - Archive messages for backup
- ⏳ Message Deleter - Bulk delete messages by criteria

## Architecture

### Technology Stack
- **Language**: Python 3.x
- **Telegram API**: Telethon library
- **Database**: MySQL 8.0+ with mysql-connector-python
- **Async Framework**: asyncio for parallel downloads

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `telegram_downloader.py` | Main download tool | ✅ Complete |
| `db_connection.py` | Database connection module | ✅ Complete |
| `database_schema.sql` | MySQL schema (fresh install) | ✅ Complete |
| `database_migration_001_add_hostname.sql` | Migration for hostname columns | ✅ Complete |
| `my.json` | Configuration (not in git) | ✅ Complete |
| `my.json.example` | Configuration template | ✅ Complete |
| `requirements.txt` | Python dependencies | ✅ Complete |
| `README.md` | User documentation | ✅ Complete |

## Database Schema

### Tables

#### 1. `messages` (Main message storage)
**Purpose**: Store all retrieved messages with media metadata and status tracking

**Key Columns**:
- `message_id` + `chat_id` - Unique identifier (composite key)
- `media_type` - ENUM: none, photo, video, document, audio, voice, sticker, animation, other
- `status` - ENUM: retrieved, downloaded, archived, deleted, failed
- `retrieved_hostname` - Machine that scanned the message
- `download_hostname` - Machine that downloaded the file
- `local_file_path` - Where the file was saved
- `retrieved_datetime` - When message was first scanned

**Indexes**: message_id, chat_id, message_date, media_type, status, retrieved_hostname, download_hostname

#### 2. `download_log` (Download history)
**Purpose**: Track every download attempt (success/failure) with hostname

**Key Columns**:
- `message_id` + `chat_id` - Links to messages table
- `download_status` - ENUM: success, failed, retry
- `hostname` - Which machine performed the download
- `error_message` - If failed, what went wrong

#### 3. `chats` (Chat metadata)
**Purpose**: Store chat/group information for reference

**Key Columns**:
- `chat_id` - Unique Telegram chat ID
- `chat_type` - ENUM: user, group, channel, supergroup
- `last_scan_datetime` - Last time this chat was scanned

#### 4. `action_log` (Operation history)
**Purpose**: Track all tool operations for auditing

**Key Columns**:
- `action_type` - ENUM: scan, download, archive, delete, analyze
- `status` - ENUM: started, completed, failed, cancelled
- `hostname` - Which machine performed the action

## Configuration

### my.json Structure
```json
{
  "database": {
    "host": "localhost",
    "user": "telegram_user",
    "password": "secure_password",
    "database": "telegram_utilities"
  },
  "telegram": {
    "api_id": "12345678",
    "api_hash": "abcdef1234567890abcdef1234567890",
    "phone": "+1234567890"
  }
}
```

**Security**: `my.json` is in `.gitignore` - never commit credentials!

## How It Works

### telegram_downloader.py Workflow

1. **Initialization**
   - Load config from `my.json` or environment variables
   - Connect to MySQL database (optional, gracefully degrades)
   - Initialize Telethon client with session file

2. **Message Collection Phase**
   - Iterate through all messages in specified chat
   - Filter by date range (if specified)
   - Filter by media type (photo/video/document)
   - For each matching message:
     - Generate timestamped filename (YYYYMMDD_HHMMSS format)
     - Save message metadata to database with `retrieved_hostname`
     - Add to download queue

3. **Parallel Download Phase**
   - Use asyncio.Semaphore to maintain exactly 5 concurrent downloads
   - For each file:
     - Download with progress callback (show at 0%, 25%, 50%, 75%, 100%)
     - Retry up to 3 times on network errors (2 second delay between retries)
     - On success: Update database with `downloaded` status and `download_hostname`
     - On failure: Update database with `failed` status and error message
     - Log to `download_log` table

4. **Cleanup**
   - Disconnect Telegram client (ignore database lock errors on session)
   - Disconnect MySQL connection

### Database Integration

**save_message_to_db()**:
- Called during message collection phase
- Uses `ON DUPLICATE KEY UPDATE` for idempotent re-scans
- Records: message metadata, media info, retrieved_hostname

**update_download_status()**:
- Called when download completes (success or failure)
- Updates message status and download_hostname
- Inserts record into download_log with hostname

## Common Tasks

### Adding New Features to telegram_downloader.py
1. Update argument parser if adding CLI options
2. Add new logic in `download_media()` method
3. Update database if new columns needed (create migration script)
4. Update README.md with examples

### Creating a New Tool (e.g., message_analyzer.py)
1. Import `DatabaseConnection` from `db_connection.py`
2. Use same `my.json` configuration structure
3. Update database using existing tables or add new ones
4. Always record `hostname` for operations
5. Use `action_log` table to track tool runs
6. Update README.md with new tool documentation

### Database Migrations
1. Create new file: `database_migration_XXX_description.sql`
2. Use `IF NOT EXISTS` clauses for safety
3. Update `README.md` with migration instructions
4. Test on a copy of production database first

## Code Patterns & Conventions

### Error Handling
```python
# Always wrap database operations in try-except
try:
    with self.db.get_cursor() as cursor:
        cursor.execute(sql, params)
except Exception as e:
    print(f"  Warning: Database operation failed: {e}")
    # Continue execution - database is optional
```

### Hostname Tracking
```python
import socket
self.hostname = socket.gethostname()
# Always save hostname with database operations
```

### Async Operations
```python
# Use semaphore for concurrent limits
semaphore = asyncio.Semaphore(5)
async with semaphore:
    await download_file()
```

### Progress Display
```python
# Show progress at key milestones only (not every percentage)
milestones = [0, 25, 50, 75]  # 100% shown separately
```

## Known Issues & Gotchas

1. **SQLite database lock on disconnect**: Normal and harmless. Occurs when Telegram session database is busy during cleanup. Already handled with try-except.

2. **Timezone-aware datetimes**: Always use `timezone.utc` for datetime objects to match Telegram API:
   ```python
   from datetime import timezone
   dt = datetime.now(timezone.utc)
   ```

3. **File overwrites**: Same filename sent multiple times - solved by adding `HHMMSS` timestamp to all filenames

4. **Network timeouts**: "semaphore timeout period has expired" - solved with retry logic (3 attempts, 2s delay)

5. **Database is optional**: Code must work even if database connection fails. All database operations wrapped in try-except.

## Git Workflow

### Protected Files (in .gitignore)
- `my.json` - Contains credentials
- `.claude/` - Claude Code settings
- `session_*` - Telethon session files
- `downloads/` - Downloaded media files

### Branch Strategy
- `master` - Main branch, always production-ready
- Feature branches not currently used (solo developer)

### Commit Message Format
```
Brief summary of change

Detailed explanation of:
- What changed
- Why it changed
- Any breaking changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Development Environment

### Requirements
- Python 3.8+
- MySQL 8.0+
- Telegram API credentials (from https://my.telegram.org)
- Active Telegram account with phone number

### Setup for New Developers
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `my.json` from `my.json.example`
4. Initialize database: `python db_connection.py`
5. Test connection: `python telegram_downloader.py --list-chats`

## Performance Considerations

### Current Limits
- **5 concurrent downloads** - Balance between speed and API rate limits
- **3 retry attempts** - Good balance between reliability and timeout duration
- **2 second retry delay** - Allows network to recover without excessive waiting

### Scaling Notes
- Database hostname tracking enables running on multiple machines simultaneously
- Telethon handles Telegram rate limiting automatically with `flood_sleep_threshold=60`
- MySQL indexes on chat_id, message_id, status, hostname for fast queries

## Future Enhancements

### Short-term (Next features)
1. Message Analyzer tool
   - Statistics by chat, sender, media type
   - Date range analysis
   - File size summaries

2. Message Archiver tool
   - Export messages to JSON/CSV
   - Backup media files
   - Archive by date range

3. Message Deleter tool
   - Bulk delete by criteria
   - Safety confirmations
   - Undo protection

### Long-term Ideas
- Web UI for database browsing
- Duplicate file detection
- Automatic media organization by type/date
- Integration with cloud storage (S3, Google Drive)
- Message search functionality
- Scheduled automatic downloads

## Testing Strategy

### Manual Testing Checklist
- [ ] List chats works
- [ ] Download photos only
- [ ] Download videos only
- [ ] Download documents with extension filter
- [ ] Download all media types
- [ ] Date range filtering
- [ ] Database tracking (check messages table)
- [ ] Hostname recording (check retrieved_hostname, download_hostname)
- [ ] Retry on network failure
- [ ] Graceful degradation without database

### Database Testing
- [ ] Fresh install with database_schema.sql
- [ ] Migration from old schema with database_migration_001_add_hostname.sql
- [ ] Re-scan same chat (ON DUPLICATE KEY UPDATE works)
- [ ] Multiple machines writing to same database

## Troubleshooting Guide

### "Database is locked" error
- **Cause**: SQLite session file locked by Telethon during cleanup
- **Solution**: Already handled in code, error is harmless, can ignore

### "Can't compare offset-naive and offset-aware datetimes"
- **Cause**: Mixing timezone-aware and naive datetime objects
- **Solution**: Always use `timezone.utc` for datetime objects

### "Server closed the connection: semaphore timeout"
- **Cause**: Network timeout during large file download
- **Solution**: Already handled with retry logic

### Database connection failed
- **Cause**: my.json missing or incorrect credentials
- **Solution**: Check my.json exists and credentials are correct
- **Fallback**: Tool works without database (no tracking)

### Can't find chat ID
- **Cause**: Not a member of chat, or using wrong ID format
- **Solution**: Run `--list-chats` to see available chats and correct IDs

## Quick Reference Commands

```bash
# List all chats
python telegram_downloader.py --list-chats

# Download all photos from a chat
python telegram_downloader.py --chat-id CHAT_ID

# Download videos from date range
python telegram_downloader.py --chat-id CHAT_ID --media-type video --start-date 2024-01-01 --end-date 2024-12-31

# Download PDFs only
python telegram_downloader.py --chat-id CHAT_ID --media-type document --extensions pdf

# Download everything
python telegram_downloader.py --chat-id CHAT_ID --media-type all

# Test database connection
python db_connection.py

# Apply database migration
mysql -u username -p telegram_utilities < database_migration_001_add_hostname.sql
```

## For New Claude Code Sessions

When starting a new Claude Code session, tell Claude to:

1. **Read this file**: `Read PROJECT_CONTEXT.md to understand the project`
2. **Check current status**: Review recent commits with `git log --oneline -10`
3. **Understand the task**: Ask user what they want to accomplish
4. **Review relevant code**: Read the specific files related to the task
5. **Follow conventions**: Use the patterns documented above

**Example prompt for new session**:
```
Read PROJECT_CONTEXT.md to understand this Telegram utilities project.
Then I need help with [describe your task].
```

---

**Last Updated**: 2025-01-04
**Project Lead**: User (with Claude Code assistance)
**Repository**: https://github.com/[username]/telegram-utilities
