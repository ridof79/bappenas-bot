#!/usr/bin/env python3
"""
Comprehensive diagnostic script untuk masalah /setup dan konfigurasi
"""

import sqlite3
import json
from datetime import datetime

def check_database_structure():
    """Check database structure"""
    print("=== Database Structure Check ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Check all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables found:")
        for (table_name,) in tables:
            print(f"  ✅ {table_name}")
        
        print()
        
        # Check chat_groups table structure
        print("=== Chat Groups Table Structure ===")
        cursor.execute("PRAGMA table_info(chat_groups);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - PK: {col[5]}, Not Null: {col[3]}")
        
        print()
        
        # Check configurations table structure
        print("=== Configurations Table Structure ===")
        cursor.execute("PRAGMA table_info(configurations);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - PK: {col[5]}, Not Null: {col[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def check_chat_groups_data():
    """Check chat groups data"""
    print("\n=== Chat Groups Data ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM chat_groups")
        count = cursor.fetchone()[0]
        print(f"Total chat groups: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM chat_groups")
            chat_groups = cursor.fetchall()
            print("Chat groups data:")
            for group in chat_groups:
                print(f"  {group}")
        else:
            print("❌ No chat groups found!")
            print("This is why scheduled reminders don't work.")
            print("Possible causes:")
            print("  1. /setup command not executed")
            print("  2. Bot not added as admin")
            print("  3. Database error during /setup")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def check_configurations_data():
    """Check configurations data"""
    print("\n=== Configurations Data ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM configurations")
        count = cursor.fetchone()[0]
        print(f"Total configurations: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM configurations")
            configs = cursor.fetchall()
            print("Configurations data:")
            for config in configs:
                print(f"  {config}")
                
                # Parse enabled_days
                try:
                    enabled_days = json.loads(config[6]) if config[6] else []
                    print(f"    Enabled days: {enabled_days}")
                except:
                    print(f"    Enabled days: Error parsing {config[6]}")
        else:
            print("❌ No configurations found!")
            print("This means /config settings are not being saved.")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def check_orphaned_configurations():
    """Check for configurations without corresponding chat groups"""
    print("\n=== Orphaned Configurations Check ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT c.chat_id 
            FROM configurations c 
            LEFT JOIN chat_groups g ON c.chat_id = g.chat_id 
            WHERE g.chat_id IS NULL
        """)
        orphaned = cursor.fetchall()
        
        if orphaned:
            print(f"❌ Found {len(orphaned)} orphaned configurations:")
            for (chat_id,) in orphaned:
                print(f"  Chat ID: {chat_id}")
            print("These configurations will not be processed by scheduler.")
        else:
            print("✅ No orphaned configurations found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

    """Test adding chat group manually"""
    print("\n=== Test Add Chat Group ===\n")
    
    try:
        # Test data
        test_chat_id = -1001234567890
        test_chat_title = "Test Group"
        test_chat_type = "supergroup"
        
        print(f"Testing with:")
        print(f"  Chat ID: {test_chat_id}")
        print(f"  Title: {test_chat_title}")
        print(f"  Type: {test_chat_type}")
        
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Test adding chat group
        cursor.execute('''
            INSERT OR REPLACE INTO chat_groups (chat_id, chat_title, chat_type, is_active, created_at)
            VALUES (?, ?, ?, 1, ?)
        ''', (test_chat_id, test_chat_title, test_chat_type, datetime.now()))
        
        conn.commit()
        print("✅ Test chat group added successfully")
        
        # Verify it was saved
        cursor.execute("SELECT * FROM chat_groups WHERE chat_id = ?", (test_chat_id,))
        result = cursor.fetchone()
        if result:
            print(f"✅ Chat group verified: {result}")
        else:
            print("❌ Chat group not found after adding")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing add chat group: {e}")

def main():
    """Main diagnostic function"""
    print("Comprehensive Setup and Configuration Diagnostic\n")
    print("=" * 60)
    
    check_database_structure()
    check_chat_groups_data()
    check_configurations_data()
    check_orphaned_configurations()
    
    print("\n" + "=" * 60)
    print("Testing Database Operations")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("Summary and Recommendations")
    print("=" * 60)
    
    print("\n1. If no chat groups found:")
    print("   - Run /setup in your group as admin")
    print("   - Make sure bot is admin in the group")
    print("   - Check bot logs for errors")
    
    print("\n2. If configurations found but no chat groups:")
    print("   - Run /setup to register the chat group")
    print("   - Or add chat group manually using test function above")
    
    print("\n3. If database operations fail:")
    print("   - Check database permissions")
    print("   - Check disk space")
    print("   - Restart bot and try again")
    
    print("\n4. Next steps:")
    print("   - Restart bot: sudo systemctl restart telegram-bot")
    print("   - Run /setup in your group")
    print("   - Check logs: sudo journalctl -u telegram-bot -f")

if __name__ == "__main__":
    main() 