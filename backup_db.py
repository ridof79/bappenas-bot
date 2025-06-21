#!/usr/bin/env python3
"""
Database backup and restore utility for Attendance Bot
"""

import os
import sys
import sqlite3
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def backup_database(db_path, backup_dir="backups"):
    """Create a backup of the database"""
    try:
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"attendance_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        # Create zip archive
        zip_filename = f"attendance_backup_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, os.path.basename(backup_path))
        
        # Remove the uncompressed backup file
        os.remove(backup_path)
        
        print(f"✅ Database backup created: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def restore_database(backup_path, db_path):
    """Restore database from backup"""
    try:
        # Check if backup file exists
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        # Create backup of current database
        if os.path.exists(db_path):
            current_backup = f"{db_path}.backup"
            shutil.copy2(db_path, current_backup)
            print(f"📦 Current database backed up to: {current_backup}")
        
        # Extract and restore
        if backup_path.endswith('.zip'):
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Extract the database file
                db_filename = None
                for name in zipf.namelist():
                    if name.endswith('.db'):
                        db_filename = name
                        break
                
                if not db_filename:
                    print("❌ No database file found in backup archive")
                    return False
                
                # Extract to temporary location
                temp_path = f"/tmp/{db_filename}"
                with zipf.open(db_filename) as source, open(temp_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                # Move to final location
                shutil.move(temp_path, db_path)
        else:
            # Direct copy if not a zip file
            shutil.copy2(backup_path, db_path)
        
        print(f"✅ Database restored from: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

def list_backups(backup_dir="backups"):
    """List available backups"""
    try:
        if not os.path.exists(backup_dir):
            print("📁 No backup directory found")
            return []
        
        backups = []
        for file in os.listdir(backup_dir):
            if file.endswith('.zip') and file.startswith('attendance_backup_'):
                file_path = os.path.join(backup_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                backups.append({
                    'filename': file,
                    'path': file_path,
                    'size': file_size,
                    'time': file_time
                })
        
        # Sort by time (newest first)
        backups.sort(key=lambda x: x['time'], reverse=True)
        
        if not backups:
            print("📁 No backups found")
        else:
            print("📦 Available backups:")
            print("-" * 80)
            for backup in backups:
                size_mb = backup['size'] / (1024 * 1024)
                print(f"📄 {backup['filename']}")
                print(f"   📅 {backup['time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   📏 {size_mb:.2f} MB")
                print()
        
        return backups
        
    except Exception as e:
        print(f"❌ Error listing backups: {e}")
        return []

def verify_database(db_path):
    """Verify database integrity"""
    try:
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            return False
        
        # Connect to database and check tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if required tables exist
        required_tables = ['attendance', 'configurations', 'chat_groups']
        existing_tables = []
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            existing_tables.append(table[0])
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False
        
        # Check table structure
        for table in required_tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            print(f"✅ Table '{table}' has {len(columns)} columns")
        
        conn.close()
        print("✅ Database verification completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def main():
    """Main function"""
    print("🗄️ Attendance Bot Database Utility")
    print("=" * 40)
    
    # Get database path from environment or use default
    db_path = os.getenv('DATABASE_PATH', 'attendance.db')
    backup_dir = "backups"
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_db.py backup     - Create backup")
        print("  python backup_db.py restore    - Restore from backup")
        print("  python backup_db.py list       - List backups")
        print("  python backup_db.py verify     - Verify database")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        print("📦 Creating database backup...")
        backup_path = backup_database(db_path, backup_dir)
        if backup_path:
            print("✅ Backup completed successfully")
        else:
            print("❌ Backup failed")
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Please specify backup file to restore from")
            print("Example: python backup_db.py restore backups/attendance_backup_20240115_143022.zip")
            return
        
        backup_path = sys.argv[2]
        print(f"🔄 Restoring database from: {backup_path}")
        
        # Confirm restoration
        confirm = input("⚠️ This will overwrite the current database. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Restoration cancelled")
            return
        
        if restore_database(backup_path, db_path):
            print("✅ Restoration completed successfully")
            # Verify the restored database
            verify_database(db_path)
        else:
            print("❌ Restoration failed")
    
    elif command == "list":
        print("📋 Listing available backups...")
        list_backups(backup_dir)
    
    elif command == "verify":
        print("🔍 Verifying database integrity...")
        verify_database(db_path)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: backup, restore, list, verify")

if __name__ == "__main__":
    main() 