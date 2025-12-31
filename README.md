# Telegram Media Downloader

A Python script that acts as a Telegram client to download photos, videos, and documents from groups/chats based on chat ID, date filters, and file extensions.

## Features

- Download photos, videos, documents, or any combination from Telegram chats/groups
- Filter by date range (start date and end date)
- Filter documents by file extension (e.g., PDF, DOCX, ZIP)
- Files renamed with date+time prefix: `YYYYMMDD_HHMMSS_<original_filename>.<ext>` (prevents overwrites)
- List all your available chats to find chat IDs
- Automatic folder organization by chat name
- Progress tracking and download summary
- Support for multiple video formats (mp4, mov, etc.)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click on "API development tools"
4. Create a new application (if you haven't already)
5. Note down your `api_id` and `api_hash`

### 3. Configure Credentials

You can provide credentials in two ways:

**Option A: Environment Variables (Recommended)**
```bash
# Windows
set TELEGRAM_API_ID=your_api_id
set TELEGRAM_API_HASH=your_api_hash
set TELEGRAM_PHONE=+1234567890

# Linux/Mac
export TELEGRAM_API_ID=your_api_id
export TELEGRAM_API_HASH=your_api_hash
export TELEGRAM_PHONE=+1234567890
```

**Option B: Command Line Arguments**
```bash
python telegram_photo_downloader.py --api-id YOUR_API_ID --api-hash YOUR_API_HASH --phone +1234567890
```

## Usage

### List All Your Chats

First, find the chat ID you want to download from:

```bash
python telegram_downloader.py --list-chats
```

This will display all your chats with their IDs.

### Download All Photos from a Chat

```bash
python telegram_downloader.py --chat-id CHAT_ID
```

### Download All Videos from a Chat

```bash
python telegram_downloader.py --chat-id CHAT_ID --media-type video
```

### Download Both Photos and Videos

```bash
python telegram_downloader.py --chat-id CHAT_ID --media-type both
```

### Download Documents (All Types)

```bash
python telegram_downloader.py --chat-id CHAT_ID --media-type document
```

### Download Specific File Types

```bash
# Download only PDF files
python telegram_downloader.py --chat-id CHAT_ID --media-type document --extensions pdf

# Download PDF and DOCX files
python telegram_downloader.py --chat-id CHAT_ID --media-type document --extensions pdf,docx

# Download multiple file types
python telegram_downloader.py --chat-id CHAT_ID --media-type document --extensions pdf,docx,zip,xlsx
```

### Download Media from a Specific Date Range

```bash
# Download photos from January 2024
python telegram_downloader.py --chat-id CHAT_ID --start-date 2024-01-01 --end-date 2024-01-31

# Download videos from December 2024
python telegram_downloader.py --chat-id CHAT_ID --start-date 2024-12-01 --end-date 2024-12-31 --media-type video

# Download PDF files from December 2024
python telegram_downloader.py --chat-id CHAT_ID --start-date 2024-12-01 --end-date 2024-12-31 --media-type document --extensions pdf

# Download all media types from a specific date with time
python telegram_downloader.py --chat-id CHAT_ID --start-date "2024-01-01 10:00:00" --end-date "2024-01-01 18:00:00" --media-type all
```

### Download Everything

```bash
# Download photos, videos, and all documents
python telegram_downloader.py --chat-id CHAT_ID --media-type all

# Download everything from the last 7 days
python telegram_downloader.py --chat-id CHAT_ID --start-date 2025-12-23 --media-type all
```

### Specify Custom Output Directory

```bash
python telegram_downloader.py --chat-id CHAT_ID --output-dir my_media --media-type both
```

## Examples

```bash
# List all chats
python telegram_downloader.py --list-chats

# Download all photos from a group
python telegram_downloader.py --chat-id -1001234567890

# Download all videos from a group
python telegram_downloader.py --chat-id -1001234567890 --media-type video

# Download all PDF files from a group
python telegram_downloader.py --chat-id -1001234567890 --media-type document --extensions pdf

# Download PDF and DOCX files from December 2024
python telegram_downloader.py --chat-id -1001234567890 --start-date 2024-12-01 --end-date 2024-12-31 --media-type document --extensions pdf,docx

# Download both photos and videos
python telegram_downloader.py --chat-id -1001234567890 --media-type both

# Download everything (photos, videos, all documents)
python telegram_downloader.py --chat-id -1001234567890 --media-type all

# Download all documents (any file type) from a specific date
python telegram_downloader.py --chat-id username --start-date 2024-01-01 --media-type document
```

## Notes

- **Chat ID**: Can be a numeric ID (e.g., `-1001234567890` for groups) or a username (e.g., `@username`)
- **First Run**: On first run, you'll receive a code on Telegram to authenticate
- **Session**: Authentication is saved in a session file, so you won't need to login again
- **File Names**:
  - Photos: `YYYYMMDD_HHMMSS_msgID.jpg`
  - Videos: `YYYYMMDD_HHMMSS_<original_filename>.<ext>`
  - Documents: `YYYYMMDD_HHMMSS_<original_filename>.<ext>`
- **Folders**: Media files are organized in folders named after the chat
- **Media Types**:
  - `--media-type photo` - Photos only
  - `--media-type video` - Videos only
  - `--media-type document` - Documents only
  - `--media-type both` - Photos + Videos
  - `--media-type all` - Photos + Videos + Documents
- **File Extensions**: Use `--extensions` to filter specific document types (e.g., `--extensions pdf,docx,zip`)

## Troubleshooting

**"Missing required credentials"**
- Make sure you've set the environment variables or provided command line arguments

**"Error accessing chat"**
- Verify the chat ID is correct
- Make sure you're a member of the group/chat
- For private chats, use the username or numeric ID

**"Failed to download"**
- Some photos might be deleted or restricted
- Check your internet connection
- Ensure you have sufficient disk space

## License

MIT License - Feel free to use and modify as needed.
