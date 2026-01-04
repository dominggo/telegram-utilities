# Telegram Utilities

A comprehensive Python toolkit for Telegram automation with MySQL database integration.

## Features

### Current Tools:
1. **Media Downloader** (`telegram_downloader.py`)
   - Download photos, videos, documents from chats/groups
   - Filter by date range and file extension
   - Parallel downloads with progress tracking
   - Automatic retry on failures

### Planned Tools:
2. **Message Analyzer** (Coming soon)
   - Analyze message patterns and statistics
   - Export analytics reports

3. **Message Archiver** (Coming soon)
   - Archive messages to database
   - Full-text search capabilities

4. **Message Deleter** (Coming soon)
   - Bulk delete messages by criteria
   - Safe deletion with confirmation

## Database Structure

All tools use a centralized MySQL database to:
- Store retrieved message metadata
- Track download/archive/delete status
- Enable cross-tool functionality
- Maintain operation history
- Track which machine performed each operation (hostname tracking)

**Key Tables:**
- `messages` - All retrieved message data with status tracking
  - `retrieved_hostname` - Machine that scanned/retrieved the message
  - `download_hostname` - Machine that downloaded the file
- `chats` - Chat/group information
- `download_log` - Download operation history with hostname
- `action_log` - All tool operation logs with hostname

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

Create a MySQL database and configure connection:

```bash
# Copy example configuration
cp my.json.example my.json

# Edit my.json with your credentials
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "your_username",
    "password": "your_password",
    "database": "telegram_utilities"
  },
  "telegram": {
    "api_id": "your_api_id",
    "api_hash": "your_api_hash",
    "phone": "+1234567890"
  }
}
```

Initialize the database schema:

```bash
python db_connection.py
```

### 3. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click "API development tools"
4. Create a new application
5. Add credentials to `my.json`

## Usage

### Media Downloader

```bash
# List all your chats
python telegram_downloader.py --list-chats

# Download photos from a date range
python telegram_downloader.py --chat-id CHAT_ID --start-date 2024-01-01 --end-date 2024-12-31

# Download videos
python telegram_downloader.py --chat-id CHAT_ID --media-type video

# Download specific document types
python telegram_downloader.py --chat-id CHAT_ID --media-type document --extensions pdf,docx

# Download everything
python telegram_downloader.py --chat-id CHAT_ID --media-type all
```

**Features:**
- Parallel downloads (5 concurrent)
- Real-time progress tracking
- Automatic retry on network errors
- Date/time-stamped filenames (prevents overwrites)
- Hostname tracking (tracks which machine retrieved/downloaded each file)

### Database Operations

```bash
# Test database connection and initialize schema
python db_connection.py

# Apply database migrations (if upgrading from older version)
mysql -u username -p telegram_utilities < database_migration_001_add_hostname.sql
```

## File Structure

```
telegram-utilities/
├── telegram_downloader.py               # Media download tool
├── db_connection.py                     # Database connection module
├── database_schema.sql                  # MySQL database schema
├── database_migration_001_add_hostname.sql  # Migration: Add hostname tracking
├── my.json                              # Configuration (not tracked in git)
├── my.json.example                      # Configuration template
├── requirements.txt                     # Python dependencies
├── PROJECT_CONTEXT.md                   # Detailed project documentation for developers/AI
└── README.md                            # This file
```

> **Note for Developers**: See `PROJECT_CONTEXT.md` for comprehensive project documentation, architecture details, code patterns, and development guidelines.

## Configuration

### my.json
Contains all sensitive configuration:
- MySQL database credentials
- Telegram API credentials
- **Never commit this file to git!**

### Database Schema
The `database_schema.sql` file contains:
- Complete table definitions
- Indexes for performance
- Foreign key relationships
- Auto-timestamp tracking

## Notes

- **Chat ID**: Can be numeric (e.g., `-1001234567890`) or username
- **Session Files**: Telegram session saved as `session_*.session`
- **File Naming**:
  - Photos: `YYYYMMDD_HHMMSS_msgID.jpg`
  - Videos: `YYYYMMDD_HHMMSS_<filename>.<ext>`
  - Documents: `YYYYMMDD_HHMMSS_<filename>.<ext>`

## Troubleshooting

**"Configuration file not found"**
- Copy `my.json.example` to `my.json` and fill in your credentials

**"Error connecting to MySQL database"**
- Verify MySQL is running
- Check credentials in `my.json`
- Ensure database exists or run `db_connection.py` to create it

**"Missing required credentials"**
- Add Telegram API credentials to `my.json`

## Development

### Adding New Tools

1. Create new `.py` file for your tool
2. Import `db_connection` module
3. Use database to store/retrieve message data
4. Follow existing patterns for error handling
5. Update README with usage instructions

### Database Schema Changes

1. Edit `database_schema.sql`
2. Run `python db_connection.py` to apply changes
3. Test with existing data

## License

MIT License - Feel free to use and modify as needed.
