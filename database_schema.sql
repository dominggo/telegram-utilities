-- Telegram Utilities Database Schema

CREATE DATABASE IF NOT EXISTS telegram_utilities
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE telegram_utilities;

-- Messages table to store all retrieved messages
CREATE TABLE IF NOT EXISTS messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    message_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    chat_name VARCHAR(255),
    sender_id BIGINT,
    sender_name VARCHAR(255),
    message_date DATETIME NOT NULL,
    message_text TEXT,
    media_type ENUM('none', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation', 'other') DEFAULT 'none',
    media_file_name VARCHAR(500),
    media_file_size BIGINT,
    media_mime_type VARCHAR(100),
    media_duration INT,
    has_media BOOLEAN DEFAULT FALSE,
    retrieved_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retrieved_hostname VARCHAR(255),
    status ENUM('retrieved', 'downloaded', 'archived', 'deleted', 'failed') DEFAULT 'retrieved',
    local_file_path VARCHAR(1000),
    download_hostname VARCHAR(255),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes for performance
    INDEX idx_message_id (message_id),
    INDEX idx_chat_id (chat_id),
    INDEX idx_message_date (message_date),
    INDEX idx_media_type (media_type),
    INDEX idx_status (status),
    INDEX idx_retrieved_datetime (retrieved_datetime),
    INDEX idx_retrieved_hostname (retrieved_hostname),
    INDEX idx_download_hostname (download_hostname),

    -- Composite indexes
    INDEX idx_chat_message (chat_id, message_id),
    INDEX idx_chat_date (chat_id, message_date),

    -- Unique constraint to prevent duplicate messages
    UNIQUE KEY unique_message (chat_id, message_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chats table to store chat information
CREATE TABLE IF NOT EXISTS chats (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    chat_id BIGINT NOT NULL UNIQUE,
    chat_name VARCHAR(255),
    chat_type ENUM('user', 'group', 'channel', 'supergroup') NOT NULL,
    chat_username VARCHAR(255),
    total_messages INT DEFAULT 0,
    last_scan_datetime DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_chat_type (chat_type),
    INDEX idx_last_scan (last_scan_datetime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Download log table to track download operations
CREATE TABLE IF NOT EXISTS download_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    message_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    download_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    download_status ENUM('success', 'failed', 'retry') NOT NULL,
    file_path VARCHAR(1000),
    file_size BIGINT,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    hostname VARCHAR(255),

    INDEX idx_message (message_id),
    INDEX idx_download_datetime (download_datetime),
    INDEX idx_status (download_status),
    INDEX idx_hostname (hostname),

    FOREIGN KEY (chat_id, message_id) REFERENCES messages(chat_id, message_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Action log table to track all operations
CREATE TABLE IF NOT EXISTS action_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    action_type ENUM('scan', 'download', 'archive', 'delete', 'analyze') NOT NULL,
    chat_id BIGINT,
    message_count INT DEFAULT 0,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME,
    status ENUM('started', 'completed', 'failed', 'cancelled') DEFAULT 'started',
    parameters TEXT,
    result_summary TEXT,
    error_message TEXT,
    hostname VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_action_type (action_type),
    INDEX idx_start_datetime (start_datetime),
    INDEX idx_status (status),
    INDEX idx_hostname (hostname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
