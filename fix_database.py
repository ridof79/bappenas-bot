#!/usr/bin/env python3
"""
Fix database schema script
"""

import sqlite3
import os
from datetime import datetime

def fix_database():
    """Fix database schema by recreating tables"""
    
    db_path = "data/attendance.db"
    
    # Backup old database if exists
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"💾 Backing up database to {backup_path}")
        os.rename(db_path, backup_path)
    
    # Create new database
    print("🔄 Creating new database with correct schema...")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create attendance table with correct schema
        cursor.execute('''
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                username TEXT,
                clock_type TEXT NOT NULL,
                clock_time DATETIME NOT NULL,
                date_only TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, user_id, clock_type, date_only)
            )
        ''')
        
        # Create configuration table
        cursor.execute('''
            CREATE TABLE configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                config_type TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                reminder_interval INTEGER NOT NULL,
                enabled_days TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, config_type)
            )
        ''')
        
        # Create chat groups table
        cursor.execute('''
            CREATE TABLE chat_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                chat_title TEXT,
                chat_type TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    
    print("✅ Database schema fixed successfully!")

if __name__ == "__main__":
    fix_database() 