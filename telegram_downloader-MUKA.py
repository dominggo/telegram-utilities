#!/usr/bin/env python3
"""
Telegram Media Downloader
Downloads photos, videos, and documents from Telegram chats/groups based on chat ID, date range, and file extension.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import asyncio
import argparse
import re

class TelegramPhotoDownloader:
    def __init__(self, api_id, api_hash, phone_number):
        """
        Initialize the Telegram client.

        Args:
            api_id: Your Telegram API ID
            api_hash: Your Telegram API Hash
            phone_number: Your phone number for authentication
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        # Use flood_sleep_threshold to handle rate limiting
        self.client = TelegramClient(
            'session_' + phone_number,
            api_id,
            api_hash,
            flood_sleep_threshold=60  # Wait up to 60 seconds if rate limited
        )

    async def download_media(self, chat_id, start_date=None, end_date=None, output_dir='downloads', media_types=['photo'], file_extensions=None):
        """
        Download photos, videos, and documents from a specific chat within a date range.

        Args:
            chat_id: The chat/group ID or username
            start_date: Start date (datetime object or None for no limit)
            end_date: End date (datetime object or None for today)
            output_dir: Directory to save downloaded media
            media_types: List of media types to download ['photo', 'video', 'document', or combinations]
            file_extensions: List of file extensions to filter (e.g., ['pdf', 'docx']) - only for documents
        """
        await self.client.start(phone=self.phone_number)
        print(f"Connected to Telegram as {self.phone_number}")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        # Get the chat entity
        try:
            # Try to convert chat_id to int if it's a string number
            try:
                chat_id_int = int(chat_id)
            except (ValueError, TypeError):
                chat_id_int = chat_id

            chat = await self.client.get_entity(chat_id_int)
            chat_name = getattr(chat, 'title', getattr(chat, 'username', str(chat_id)))
            print(f"Accessing chat: {chat_name} (ID: {chat_id})")
        except ValueError as e:
            print(f"Error accessing chat {chat_id}: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure you're a member of this chat/channel")
            print("2. Try running --list-chats to see the correct chat ID")
            print("3. For public channels, try using the username instead (e.g., @channelname)")
            return
        except Exception as e:
            print(f"Error accessing chat {chat_id}: {e}")
            print("\nTry running --list-chats to verify the chat ID")
            return

        # Create a subdirectory for this chat
        chat_dir = os.path.join(output_dir, f"{chat_name}_{chat_id}".replace('/', '_'))
        if not os.path.exists(chat_dir):
            os.makedirs(chat_dir)

        # Normalize file extensions
        if file_extensions:
            file_extensions = [ext.lower().lstrip('.') for ext in file_extensions]

        # Determine what to search for
        media_type_str = ' and '.join(media_types)
        if file_extensions and 'document' in media_types:
            ext_str = ', '.join(file_extensions)
            print(f"\nScanning for {media_type_str} (extensions: {ext_str})...")
        else:
            print(f"\nScanning for {media_type_str}...")
        if start_date:
            print(f"Start date: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
        if end_date:
            print(f"End date: {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # First pass: Count total files to download
        print("Counting files to download...")
        total_files = 0
        async for message in self.client.iter_messages(chat, reverse=False):
            # Check date range
            if start_date and message.date < start_date:
                continue
            if end_date and message.date > end_date:
                continue

            # Check if message contains media
            if not message.media:
                continue

            # Check for photos
            if 'photo' in media_types and isinstance(message.media, MessageMediaPhoto):
                total_files += 1

            # Check for videos and documents
            elif isinstance(message.media, MessageMediaDocument):
                doc = message.media.document
                mime_type = doc.mime_type if hasattr(doc, 'mime_type') else ''

                # Get original filename from document attributes
                original_filename = None
                for attr in doc.attributes:
                    if hasattr(attr, 'file_name'):
                        original_filename = attr.file_name
                        break

                # Check for videos
                if 'video' in media_types and mime_type.startswith('video/'):
                    total_files += 1

                # Check for documents
                elif 'document' in media_types and original_filename:
                    # Get file extension
                    file_ext = os.path.splitext(original_filename)[1].lstrip('.').lower()

                    # Filter by extension if specified
                    if file_extensions and file_ext not in file_extensions:
                        continue

                    total_files += 1

        print(f"Found {total_files} file(s) to download.\n")

        if total_files == 0:
            print("No files found matching your criteria.")
            return

        # Second pass: Download files
        print("Starting download...\n")
        photo_count = 0
        video_count = 0
        document_count = 0
        skipped_count = 0
        downloaded_count = 0

        # Iterate through messages
        async for message in self.client.iter_messages(chat, reverse=False):
            # Check date range
            if start_date and message.date < start_date:
                continue
            if end_date and message.date > end_date:
                continue

            # Check if message contains media
            if not message.media:
                continue

            downloaded = False

            # Check for photos
            if 'photo' in media_types and isinstance(message.media, MessageMediaPhoto):
                photo_count += 1
                timestamp = message.date.strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_msg{message.id}.jpg"
                filepath = os.path.join(chat_dir, filename)

                try:
                    downloaded_count += 1
                    await self.client.download_media(message.media, filepath)
                    print(f"✓ Downloaded {downloaded_count}/{total_files}: {filename}")
                    downloaded = True
                except asyncio.CancelledError:
                    print(f"\n✗ Download interrupted by user (Ctrl+C)")
                    print(f"Downloaded {downloaded_count - 1}/{total_files} files before interruption")
                    return
                except Exception as e:
                    print(f"✗ Failed {downloaded_count}/{total_files}: {filename} - {e}")
                    skipped_count += 1

            # Check for videos and documents
            elif isinstance(message.media, MessageMediaDocument):
                doc = message.media.document
                mime_type = doc.mime_type if hasattr(doc, 'mime_type') else ''

                # Get original filename from document attributes
                original_filename = None
                for attr in doc.attributes:
                    if hasattr(attr, 'file_name'):
                        original_filename = attr.file_name
                        break

                # Check for videos
                if 'video' in media_types and mime_type.startswith('video/'):
                    video_count += 1
                    timestamp = message.date.strftime('%Y%m%d')

                    # Get file extension from mime type or filename
                    if original_filename:
                        ext = os.path.splitext(original_filename)[1].lstrip('.')
                        base_name = os.path.splitext(original_filename)[0]
                        filename = f"{timestamp}_{base_name}.{ext}"
                    else:
                        ext = mime_type.split('/')[-1] if '/' in mime_type else 'mp4'
                        if ext == 'quicktime':
                            ext = 'mov'
                        filename = f"{timestamp}_msg{message.id}.{ext}"

                    filepath = os.path.join(chat_dir, filename)

                    try:
                        downloaded_count += 1
                        await self.client.download_media(message.media, filepath)
                        print(f"✓ Downloaded {downloaded_count}/{total_files}: {filename}")
                        downloaded = True
                    except asyncio.CancelledError:
                        print(f"\n✗ Download interrupted by user (Ctrl+C)")
                        print(f"Downloaded {downloaded_count - 1}/{total_files} files before interruption")
                        return
                    except Exception as e:
                        print(f"✗ Failed {downloaded_count}/{total_files}: {filename} - {e}")
                        skipped_count += 1

                # Check for documents
                elif 'document' in media_types and original_filename:
                    # Get file extension
                    file_ext = os.path.splitext(original_filename)[1].lstrip('.').lower()

                    # Filter by extension if specified
                    if file_extensions and file_ext not in file_extensions:
                        continue

                    document_count += 1
                    timestamp = message.date.strftime('%Y%m%d')

                    # Use original filename with date prefix
                    filename = f"{timestamp}_{original_filename}"
                    filepath = os.path.join(chat_dir, filename)

                    try:
                        downloaded_count += 1
                        await self.client.download_media(message.media, filepath)
                        print(f"✓ Downloaded {downloaded_count}/{total_files}: {filename}")
                        downloaded = True
                    except asyncio.CancelledError:
                        print(f"\n✗ Download interrupted by user (Ctrl+C)")
                        print(f"Downloaded {downloaded_count - 1}/{total_files} files before interruption")
                        return
                    except Exception as e:
                        print(f"✗ Failed {downloaded_count}/{total_files}: {filename} - {e}")
                        skipped_count += 1

        print(f"\n{'='*50}")
        print(f"Download Summary:")
        if 'photo' in media_types:
            print(f"Total photos downloaded: {photo_count}")
        if 'video' in media_types:
            print(f"Total videos downloaded: {video_count}")
        if 'document' in media_types:
            print(f"Total documents downloaded: {document_count}")
        print(f"Failed downloads: {skipped_count}")
        print(f"Saved to: {chat_dir}")
        print(f"{'='*50}")

    async def list_chats(self):
        """List all available chats/groups."""
        await self.client.start(phone=self.phone_number)
        print("\nYour chats and groups:\n")
        print(f"{'ID':<15} {'Type':<15} {'Name'}")
        print("-" * 60)

        async for dialog in self.client.iter_dialogs():
            chat_type = type(dialog.entity).__name__
            chat_name = dialog.name
            chat_id = dialog.id
            print(f"{chat_id:<15} {chat_type:<15} {chat_name}")

    async def disconnect(self):
        """Disconnect the client."""
        try:
            await self.client.disconnect()
        except Exception as e:
            # Ignore disconnect errors (often session database locks)
            pass


def parse_date(date_string):
    """Parse date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"""
    if not date_string:
        return None

    formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            # Make timezone-aware (UTC) to match Telegram message dates
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD or 'YYYY-MM-DD HH:MM:SS'")


async def main():
    parser = argparse.ArgumentParser(
        description='Download photos, videos, and documents from Telegram chats/groups',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all your chats
  python telegram_downloader.py --list-chats

  # Download all photos from a chat
  python telegram_downloader.py --chat-id -1001234567890

  # Download all videos from a chat
  python telegram_downloader.py --chat-id -1001234567890 --media-type video

  # Download all PDF files from a chat
  python telegram_downloader.py --chat-id -1001234567890 --media-type document --extensions pdf

  # Download PDF and DOCX files from December 2024
  python telegram_downloader.py --chat-id -1001234567890 --media-type document --extensions pdf,docx --start-date 2024-12-01 --end-date 2024-12-31

  # Download all documents (any extension) from a date range
  python telegram_downloader.py --chat-id -1001234567890 --media-type document --start-date 2024-01-01

  # Download photos, videos, and documents
  python telegram_downloader.py --chat-id -1001234567890 --media-type all

Note: You need to create a Telegram app at https://my.telegram.org to get API_ID and API_HASH
        """
    )

    parser.add_argument('--api-id', type=int, help='Telegram API ID (or set TELEGRAM_API_ID env var)')
    parser.add_argument('--api-hash', help='Telegram API Hash (or set TELEGRAM_API_HASH env var)')
    parser.add_argument('--phone', help='Phone number (or set TELEGRAM_PHONE env var)')
    parser.add_argument('--chat-id', help='Chat/Group ID or username to download from')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--output-dir', default='downloads', help='Output directory (default: downloads)')
    parser.add_argument('--media-type',
                        choices=['photo', 'video', 'document', 'both', 'all'],
                        default='photo',
                        help='Media type to download: photo, video, document, both (photo+video), or all (default: photo)')
    parser.add_argument('--extensions',
                        help='File extensions to filter for documents (comma-separated, e.g., pdf,docx,zip). Only applies when media-type is document or all')
    parser.add_argument('--list-chats', action='store_true', help='List all available chats and exit')

    args = parser.parse_args()

    # Get credentials from args or environment variables
    api_id = args.api_id or os.environ.get('TELEGRAM_API_ID')
    api_hash = args.api_hash or os.environ.get('TELEGRAM_API_HASH')
    phone = args.phone or os.environ.get('TELEGRAM_PHONE')

    if not api_id or not api_hash or not phone:
        print("Error: Missing required credentials!")
        print("\nYou must provide either:")
        print("  1. Command line arguments: --api-id, --api-hash, --phone")
        print("  2. Environment variables: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        print("\nTo get API credentials, visit: https://my.telegram.org")
        sys.exit(1)

    # Convert API ID to integer
    try:
        api_id = int(api_id)
    except ValueError:
        print(f"Error: API ID must be a number, got: {api_id}")
        sys.exit(1)

    # Create downloader instance
    downloader = TelegramPhotoDownloader(api_id, api_hash, phone)

    try:
        if args.list_chats:
            await downloader.list_chats()
        else:
            if not args.chat_id:
                print("Error: --chat-id is required when not using --list-chats")
                print("Run with --list-chats to see available chats")
                sys.exit(1)

            # Parse dates
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date) if args.end_date else datetime.now(timezone.utc)

            # Determine media types to download
            if args.media_type == 'both':
                media_types = ['photo', 'video']
            elif args.media_type == 'all':
                media_types = ['photo', 'video', 'document']
            else:
                media_types = [args.media_type]

            # Parse file extensions
            file_extensions = None
            if args.extensions:
                file_extensions = [ext.strip() for ext in args.extensions.split(',')]

            # Download media
            await downloader.download_media(
                args.chat_id,
                start_date=start_date,
                end_date=end_date,
                output_dir=args.output_dir,
                media_types=media_types,
                file_extensions=file_extensions
            )
    finally:
        await downloader.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
