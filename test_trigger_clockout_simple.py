#!/usr/bin/env python3
"""
Simple test untuk debug trigger_clockout command
"""

import sqlite3
from datetime import datetime

def test_database():
    """Test database untuk melihat konfigurasi"""
    print("=== Testing Database Configuration ===\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Get all configurations
        cursor.execute("SELECT * FROM configurations")
        configs = cursor.fetchall()
        
        print("All configurations in database:")
        for config in configs:
            print(f"  {config}")
        
        print()
        
        # Get clock_out configurations specifically
        cursor.execute("SELECT * FROM configurations WHERE config_type = 'clock_out'")
        clock_out_configs = cursor.fetchall()
        
        print("Clock out configurations:")
        for config in clock_out_configs:
            print(f"  {config}")
        
        if not clock_out_configs:
            print("  ❌ No clock_out configuration found!")
            print("  This is likely why /trigger_clockout doesn't work.")
            print("  You need to run /config and set up clock out configuration first.")
        
        print()
        
        # Get today's attendance
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT * FROM attendance WHERE date_only = ?", (today,))
        today_attendance = cursor.fetchall()
        
        print(f"Today's attendance ({today}):")
        for attendance in today_attendance:
            print(f"  {attendance}")
        
        if not today_attendance:
            print("  No attendance records for today")
        
        conn.close()
        
    except Exception as e:
        print(f"Error accessing database: {e}")

def test_command_registration():
    """Test apakah command terdaftar dengan benar"""
    print("=== Testing Command Registration ===\n")
    
    try:
        # Check main.py for command registration
        with open('main.py', 'r') as f:
            content = f.read()
        
        if 'trigger_clockout' in content:
            print("✅ trigger_clockout command found in main.py")
        else:
            print("❌ trigger_clockout command NOT found in main.py")
        
        if 'trigger_clockin' in content:
            print("✅ trigger_clockin command found in main.py")
        else:
            print("❌ trigger_clockin command NOT found in main.py")
        
        # Check command_handlers.py
        with open('src/handlers/command_handlers.py', 'r') as f:
            content = f.read()
        
        if 'trigger_clockout_command' in content:
            print("✅ trigger_clockout_command method found in command_handlers.py")
        else:
            print("❌ trigger_clockout_command method NOT found in command_handlers.py")
        
        if 'trigger_clockin_command' in content:
            print("✅ trigger_clockin_command method found in command_handlers.py")
        else:
            print("❌ trigger_clockin_command method NOT found in command_handlers.py")
        
    except Exception as e:
        print(f"Error checking files: {e}")

def main():
    """Main test function"""
    print("Debug Test for /trigger_clockout command\n")
    print("=" * 50)
    
    test_database()
    print("=" * 50)
    test_command_registration()
    print("=" * 50)
    
    print("\n=== Recommendations ===")
    print("1. If no clock_out configuration found:")
    print("   - Run /config in your group")
    print("   - Set up clock out configuration")
    print("   - Make sure to save the configuration")
    print()
    print("2. If command not registered:")
    print("   - Restart the bot: sudo systemctl restart telegram-bot")
    print("   - Check logs: sudo journalctl -u telegram-bot -f")
    print()
    print("3. Test the command:")
    print("   - Make sure you're admin in the group")
    print("   - Try /trigger_clockout in the group")
    print("   - Check if any error messages appear")

if __name__ == "__main__":
    main() 