#!/usr/bin/env python3
"""
Test script for trigger commands
"""

import asyncio
from src.handlers.command_handlers import CommandHandlers
from src.database.database import Database
from src.config.settings import Settings

async def test_trigger_commands():
    """Test trigger commands manually"""
    print("🧪 Testing Trigger Commands...")
    
    # Initialize database
    db = Database(Settings.DATABASE_PATH)
    command_handlers = CommandHandlers(db)
    
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
        else:
            print(f"  🟢 Clock In Config: Not configured")
        
        # Check clock out configuration
        clock_out_config = db.get_configuration(chat_id, 'clock_out')
        if clock_out_config:
            print(f"  🔴 Clock Out Config: {clock_out_config}")
        else:
            print(f"  🔴 Clock Out Config: Not configured")
        
        # Check today's attendance
        from src.utils.helpers import get_current_time
        current_time = get_current_time()
        today_attendance = db.get_today_attendance(chat_id, current_time)
        clock_in_count = len(today_attendance.get('clock_in', {}))
        clock_out_count = len(today_attendance.get('clock_out', {}))
        
        print(f"  📊 Today's Attendance:")
        print(f"    Clock In: {clock_in_count} people")
        print(f"    Clock Out: {clock_out_count} people")
        
        # Test trigger conditions
        print(f"  🧪 Trigger Test:")
        
        # Test clock in trigger
        if clock_in_config:
            print(f"    Clock In Trigger: ✅ Would work (config exists)")
        else:
            print(f"    Clock In Trigger: ❌ Would fail (no config)")
        
        # Test clock out trigger
        if clock_out_config:
            print(f"    Clock Out Trigger: ✅ Would work (config exists)")
        else:
            print(f"    Clock Out Trigger: ❌ Would fail (no config)")

if __name__ == "__main__":
    asyncio.run(test_trigger_commands()) 