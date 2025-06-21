#!/usr/bin/env python3
"""
Simple script to check database directly
"""

import sqlite3

def check_database():
    """Check database tables and data"""
    print("=== Database Check ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Check all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:")
        for (table_name,) in tables:
            print(f"  {table_name}")
        
        print()
        
        # Check chat_groups table
        print("=== Chat Groups Table ===")
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
            print("No chat groups found!")
        
        print()
        
        # Check configurations table
        print("=== Configurations Table ===")
        cursor.execute("SELECT COUNT(*) FROM configurations")
        count = cursor.fetchone()[0]
        print(f"Total configurations: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM configurations")
            configs = cursor.fetchall()
            print("Configurations data:")
            for config in configs:
                print(f"  {config}")
        else:
            print("No configurations found!")
        
        print()
        
        # Check attendance table
        print("=== Attendance Table ===")
        cursor.execute("SELECT COUNT(*) FROM attendance")
        count = cursor.fetchone()[0]
        print(f"Total attendance records: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM attendance LIMIT 5")
            attendance = cursor.fetchall()
            print("Recent attendance data:")
            for record in attendance:
                print(f"  {record}")
        else:
            print("No attendance records found!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def add_test_chat_group():
    """Add a test chat group"""
    print("\n=== Add Test Chat Group ===\n")
    
    try:
        chat_id = input("Enter test chat ID (e.g., -1001234567890): ").strip()
        chat_title = input("Enter test chat title: ").strip()
        
        if not chat_id or not chat_title:
            print("Chat ID and title are required")
            return
        
        try:
            chat_id = int(chat_id)
        except ValueError:
            print("Chat ID must be a number")
            return
        
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO chat_groups (chat_id, chat_title, chat_type, is_active, created_at)
            VALUES (?, ?, 'supergroup', 1, datetime('now'))
        """, (chat_id, chat_title))
        
        conn.commit()
        print(f"✅ Test chat group {chat_id} added successfully")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    print("Simple Database Check\n")
    
    check_database()
    
    print("\nOptions:")
    print("1. Add test chat group")
    print("2. Exit")
    
    choice = input("\nChoose option (1-2): ").strip()
    
    if choice == '1':
        add_test_chat_group()
        print("\nChecking database again...")
        check_database()
    elif choice == '2':
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main() 