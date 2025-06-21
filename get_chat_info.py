#!/usr/bin/env python3
"""
Script untuk mendapatkan Chat ID dan User ID dari database
"""

import sqlite3
from datetime import datetime

def get_chat_info():
    """Get chat information from database"""
    print("=== Chat Information from Database ===\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Get all unique chat IDs from configurations
        cursor.execute("SELECT DISTINCT chat_id FROM configurations")
        chat_ids = cursor.fetchall()
        
        print("Chat IDs found in configurations:")
        for (chat_id,) in chat_ids:
            print(f"  {chat_id}")
        
        print()
        
        # Get all unique chat IDs from attendance
        cursor.execute("SELECT DISTINCT chat_id FROM attendance")
        attendance_chat_ids = cursor.fetchall()
        
        print("Chat IDs found in attendance:")
        for (chat_id,) in attendance_chat_ids:
            print(f"  {chat_id}")
        
        print()
        
        # Get user information from attendance
        cursor.execute("""
            SELECT DISTINCT chat_id, user_id, user_name, username 
            FROM attendance 
            ORDER BY chat_id, user_id
        """)
        users = cursor.fetchall()
        
        print("Users found in attendance:")
        for chat_id, user_id, user_name, username in users:
            print(f"  Chat ID: {chat_id}, User ID: {user_id}, Name: {user_name}, Username: {username}")
        
        print()
        
        # Get recent attendance records
        cursor.execute("""
            SELECT chat_id, user_id, user_name, clock_type, clock_time, date_only
            FROM attendance 
            ORDER BY clock_time DESC 
            LIMIT 10
        """)
        recent = cursor.fetchall()
        
        print("Recent attendance records:")
        for chat_id, user_id, user_name, clock_type, clock_time, date_only in recent:
            print(f"  {date_only} {clock_time} - Chat: {chat_id}, User: {user_name} ({user_id}), {clock_type}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def get_config_details():
    """Get detailed configuration information"""
    print("\n=== Configuration Details ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT chat_id, config_type, time, interval_minutes, enabled, created_at, updated_at
            FROM configurations 
            ORDER BY chat_id, config_type
        """)
        configs = cursor.fetchall()
        
        if not configs:
            print("No configurations found")
        else:
            for config in configs:
                chat_id, config_type, time, interval, enabled, created, updated = config
                status = "✅ Enabled" if enabled else "❌ Disabled"
                print(f"Chat ID: {chat_id}")
                print(f"  Type: {config_type}")
                print(f"  Time: {time}")
                print(f"  Interval: {interval} minutes")
                print(f"  Status: {status}")
                print(f"  Created: {created}")
                print(f"  Updated: {updated}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    get_chat_info()
    get_config_details()
    
    print("=== Instructions ===")
    print("1. Use the Chat ID and User ID from above in your test scripts")
    print("2. If no clock_out configuration exists, run: python add_clockout_config.py")
    print("3. Update test_trigger_clockout_fixed.py with your actual Chat ID and User ID")

if __name__ == "__main__":
    main() 