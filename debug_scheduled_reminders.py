#!/usr/bin/env python3
"""
Script untuk debug scheduled reminders
"""

import sqlite3
from datetime import datetime

def check_chat_groups():
    """Check if chat groups are registered in database"""
    print("=== Checking Chat Groups ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Get all chat groups
        cursor.execute("SELECT * FROM chat_groups")
        chat_groups = cursor.fetchall()
        
        if not chat_groups:
            print("❌ No chat groups found in database!")
            print("This is why scheduled reminders are not working.")
            print("Chat groups need to be registered when bot is added to groups.")
            return False
        
        print(f"✅ Found {len(chat_groups)} chat groups:")
        for group in chat_groups:
            print(f"  Chat ID: {group[1]}, Title: {group[2]}, Type: {group[3]}, Active: {group[4]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_configurations():
    """Check configurations for each chat group"""
    print("\n=== Checking Configurations ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Get all chat groups
        cursor.execute("SELECT chat_id FROM chat_groups")
        chat_ids = [row[0] for row in cursor.fetchall()]
        
        if not chat_ids:
            print("No chat groups to check")
            return
        
        for chat_id in chat_ids:
            print(f"Chat ID: {chat_id}")
            
            # Check clock_in config
            cursor.execute("SELECT * FROM configurations WHERE chat_id = ? AND config_type = 'clock_in'", (chat_id,))
            clock_in_config = cursor.fetchone()
            if clock_in_config:
                print(f"  ✅ Clock In: {clock_in_config[3]}-{clock_in_config[4]}, Interval: {clock_in_config[5]}min, Days: {clock_in_config[6]}")
            else:
                print(f"  ❌ No clock_in configuration")
            
            # Check clock_out config
            cursor.execute("SELECT * FROM configurations WHERE chat_id = ? AND config_type = 'clock_out'", (chat_id,))
            clock_out_config = cursor.fetchone()
            if clock_out_config:
                print(f"  ✅ Clock Out: {clock_out_config[3]}-{clock_out_config[4]}, Interval: {clock_out_config[5]}min, Days: {clock_out_config[6]}")
            else:
                print(f"  ❌ No clock_out configuration")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def check_current_time_conditions():
    """Check if current time meets conditions for reminders"""
    print("\n=== Checking Current Time Conditions ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        current_time = datetime.now()
        current_weekday = current_time.weekday()
        current_time_str = current_time.strftime('%H:%M')
        
        print(f"Current time: {current_time_str}")
        print(f"Current weekday: {current_weekday} ({['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][current_weekday]})")
        print()
        
        # Get all configurations
        cursor.execute("SELECT chat_id, config_type, start_time, end_time, enabled_days FROM configurations")
        configs = cursor.fetchall()
        
        if not configs:
            print("No configurations found")
            return
        
        for config in configs:
            chat_id, config_type, start_time, end_time, enabled_days = config
            
            print(f"Chat {chat_id} - {config_type}:")
            print(f"  Time range: {start_time} - {end_time}")
            print(f"  Enabled days: {enabled_days}")
            
            # Check if today is enabled
            enabled_days_list = [int(x) for x in enabled_days.split(',')]
            if current_weekday in enabled_days_list:
                print(f"  ✅ Today is enabled")
            else:
                print(f"  ❌ Today is not enabled")
            
            # Check if current time is in range
            current_hour, current_minute = map(int, current_time_str.split(':'))
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            current_minutes = current_hour * 60 + current_minute
            start_minutes = start_hour * 60 + start_minute
            end_minutes = end_hour * 60 + end_minute
            
            if start_minutes <= current_minutes <= end_minutes:
                print(f"  ✅ Current time is in range")
            else:
                print(f"  ❌ Current time is not in range")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def add_chat_group_manually():
    """Add a chat group manually"""
    print("\n=== Add Chat Group Manually ===\n")
    
    try:
        chat_id = input("Enter Chat ID: ").strip()
        chat_title = input("Enter Chat Title: ").strip()
        chat_type = input("Enter Chat Type (group/supergroup): ").strip()
        
        if not chat_id or not chat_title:
            print("Chat ID and Title are required")
            return
        
        try:
            chat_id = int(chat_id)
        except ValueError:
            print("Chat ID must be a number")
            return
        
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute("SELECT * FROM chat_groups WHERE chat_id = ?", (chat_id,))
        if cursor.fetchone():
            print(f"Chat group {chat_id} already exists")
        else:
            cursor.execute("""
                INSERT INTO chat_groups (chat_id, chat_title, chat_type, is_active, created_at)
                VALUES (?, ?, ?, 1, ?)
            """, (chat_id, chat_title, chat_type, datetime.now()))
            conn.commit()
            print(f"✅ Chat group {chat_id} added successfully")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    print("Scheduled Reminders Debug Tool\n")
    print("1. Check chat groups")
    print("2. Check configurations")
    print("3. Check current time conditions")
    print("4. Add chat group manually")
    print("5. Exit")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == '1':
        check_chat_groups()
    elif choice == '2':
        check_configurations()
    elif choice == '3':
        check_current_time_conditions()
    elif choice == '4':
        add_chat_group_manually()
    elif choice == '5':
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main() 