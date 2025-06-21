#!/usr/bin/env python3
"""
Manual test script to trigger reminder
"""

import asyncio
from src.handlers.message_handlers import MessageHandlers
from src.database.database import Database
from src.handlers.callback_handlers import CallbackHandlers
from src.config.settings import Settings

async def test_manual_reminder():
    """Manually trigger reminder for testing"""
    print("🧪 Testing Manual Reminder...")
    
    # Initialize components
    db = Database(Settings.DATABASE_PATH)
    callback_handlers = CallbackHandlers(db)
    message_handlers = MessageHandlers(db, callback_handlers)
    
    # Create a mock context
    class MockContext:
        def __init__(self):
            self.bot = None
    
    context = MockContext()
    
    try:
        print("Testing clock-in reminder...")
        await message_handlers.send_clock_in_reminder(context)
        
        print("Testing clock-out reminder...")
        await message_handlers.send_clock_out_reminder(context)
        
        print("✅ Manual reminder test completed!")
        
    except Exception as e:
        print(f"❌ Error in manual reminder test: {e}")

if __name__ == "__main__":
    asyncio.run(test_manual_reminder()) 