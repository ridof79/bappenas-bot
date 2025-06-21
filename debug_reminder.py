#!/usr/bin/env python3
"""
Debug script to check reminder configuration and logic
"""

import pytz
from datetime import datetime, time
from src.database.database import Database
from src.config.settings import Settings
from src.utils.helpers import get_current_time, parse_time_string

def check_reminder_conditions(config, config_type, current_time, db, chat_id):
    """Check if reminder conditions are met"""
    print(f"    Checking {config_type} conditions:")
    
    # Check if today is enabled day
    enabled_days = config.get('enabled_days', [])
    current_weekday = current_time.weekday()
    is_enabled_day = current_weekday in enabled_days
    print(f"      Enabled days: {enabled_days}")
    print(f"      Current day: {current_weekday} ({Settings.get_day_name(current_weekday)})")
    print(f"      Is enabled day: {is_enabled_day}")
    
    if not is_enabled_day:
        print(f"      ❌ Reminder not sent: Today is not enabled")
        return False
    
    # Check if current time is within the configured time range
    start_time_str = config.get('start_time', '')
    end_time_str = config.get('end_time', '')
    start_time = parse_time_string(start_time_str)
    end_time = parse_time_string(end_time_str)
    current_time_obj = current_time.time()
    
    print(f"      Time range: {start_time_str} - {end_time_str}")
    print(f"      Current time: {current_time_obj}")
    print(f"      Parsed start: {start_time}")
    print(f"      Parsed end: {end_time}")
    
    if not start_time or not end_time:
        print(f"      ❌ Reminder not sent: Invalid time format")
        return False
    
    is_within_range = start_time <= current_time_obj <= end_time
    print(f"      Is within range: {is_within_range}")
    
    if not is_within_range:
        print(f"      ❌ Reminder not sent: Current time not in range")
        return False
    
    # Check attendance
    today_attendance = db.get_today_attendance(chat_id, current_time)
    clock_in_count = len(today_attendance.get('clock_in', {}))
    clock_out_count = len(today_attendance.get('clock_out', {}))
    
    print(f"      Attendance - Clock In: {clock_in_count}, Clock Out: {clock_out_count}")
    
    if config_type == 'clock_in':
        should_send = clock_in_count == 0
        print(f"      Should send clock-in reminder: {should_send}")
    else:  # clock_out
        should_send = True  # Always send for clock out
        print(f"      Should send clock-out reminder: {should_send}")
    
    if should_send:
        print(f"      ✅ Reminder should be sent!")
    else:
        print(f"      ❌ Reminder not sent: Conditions not met")
    
    return should_send

def debug_reminder():
    """Debug reminder configuration and logic"""
    print("🔍 Debugging Reminder Configuration...")
    
    # Initialize database
    db = Database(Settings.DATABASE_PATH)
    
    # Get current time
    current_time = get_current_time()
    print(f"Current time: {current_time}")
    print(f"Current weekday: {current_time.weekday()} ({Settings.get_day_name(current_time.weekday())})")
    
    # Get all chat groups
    chat_groups = db.get_all_chat_groups()
    print(f"Total chat groups: {len(chat_groups)}")
    
    for chat_group in chat_groups:
        chat_id = chat_group['chat_id']
        chat_title = chat_group.get('chat_title', 'Unknown')
        print(f"\n📱 Chat: {chat_title} (ID: {chat_id})")
        
        # Check clock in configuration
        clock_in_config = db.get_configuration(chat_id, 'clock_in')
        if clock_in_config:
            print(f"  🟢 Clock In Config: {clock_in_config}")
            check_reminder_conditions(clock_in_config, 'clock_in', current_time, db, chat_id)
        else:
            print(f"  🟢 Clock In Config: Not configured")
        
        # Check clock out configuration
        clock_out_config = db.get_configuration(chat_id, 'clock_out')
        if clock_out_config:
            print(f"  🔴 Clock Out Config: {clock_out_config}")
            check_reminder_conditions(clock_out_config, 'clock_out', current_time, db, chat_id)
        else:
            print(f"  🔴 Clock Out Config: Not configured")

if __name__ == "__main__":
    debug_reminder() 