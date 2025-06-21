#!/usr/bin/env python3
"""
Improved test untuk debug trigger_clockout command dengan mock yang benar
"""

import asyncio
import logging
from datetime import datetime

from src.database.database import Database
from src.config.settings import Settings
from src.handlers.command_handlers import CommandHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MockBot:
    """Mock bot untuk testing"""
    async def get_chat_member(self, chat_id, user_id):
        """Mock get_chat_member"""
        class MockChatMember:
            def __init__(self):
                self.status = 'administrator'  # Assume admin for testing
        return MockChatMember()

class MockContext:
    """Mock context untuk testing"""
    def __init__(self):
        self.bot = MockBot()

class MockUpdate:
    """Mock update untuk testing"""
    def __init__(self, chat_id, user_id, user_name, is_private=False):
        self.effective_chat = MockChat(chat_id, is_private)
        self.effective_user = MockUser(user_id, user_name)
        self.message = MockMessage()
    
    async def reply_text(self, text, **kwargs):
        """Mock reply_text"""
        print(f"Bot reply: {text}")
        if 'reply_markup' in kwargs:
            print(f"Reply markup: {kwargs['reply_markup']}")

class MockChat:
    """Mock chat untuk testing"""
    def __init__(self, chat_id, is_private=False):
        self.id = chat_id
        self.type = 'private' if is_private else 'group'

class MockUser:
    """Mock user untuk testing"""
    def __init__(self, user_id, user_name):
        self.id = user_id
        self.first_name = user_name
        self.username = f"user_{user_id}"

class MockMessage:
    """Mock message untuk testing"""
    def __init__(self):
        pass
    
    async def reply_text(self, text, **kwargs):
        """Mock reply_text"""
        print(f"Bot reply: {text}")
        if 'reply_markup' in kwargs:
            print(f"Reply markup: {kwargs['reply_markup']}")

async def test_trigger_clockout():
    """Test trigger_clockout command"""
    print("=== Testing trigger_clockout command (Fixed) ===\n")
    
    # Initialize database and handlers
    db = Database(Settings.DATABASE_PATH)
    command_handlers = CommandHandlers(db)
    
    # Test data - GANTI DENGAN CHAT ID DAN USER ID YANG SEBENARNYA
    chat_id = -1001234567890  # Ganti dengan chat ID grup Anda
    user_id = 123456789  # Ganti dengan user ID Anda
    user_name = "Test Admin"
    
    # Create mock objects
    update = MockUpdate(chat_id, user_id, user_name, is_private=False)
    context = MockContext()
    
    print(f"Testing with:")
    print(f"Chat ID: {chat_id}")
    print(f"User ID: {user_id}")
    print(f"User Name: {user_name}")
    print(f"Chat Type: {update.effective_chat.type}")
    print()
    
    # Test 1: Check if configuration exists
    print("1. Checking clock_out configuration...")
    config = db.get_configuration(chat_id, 'clock_out')
    if config:
        print(f"✅ Configuration found: {config}")
    else:
        print("❌ No clock_out configuration found")
        print("You need to add configuration first!")
        print("Run: python add_clockout_config.py")
        return
    
    print()
    
    # Test 2: Check today's attendance
    print("2. Checking today's attendance...")
    current_time = datetime.now()
    today_attendance = db.get_today_attendance(chat_id, current_time)
    clock_in_count = len(today_attendance.get('clock_in', {}))
    clock_out_count = len(today_attendance.get('clock_out', {}))
    print(f"Clock In: {clock_in_count} people")
    print(f"Clock Out: {clock_out_count} people")
    
    print()
    
    # Test 3: Test admin check
    print("3. Testing admin check...")
    try:
        is_admin = await command_handlers.is_admin(update, context)
        print(f"Admin check result: {is_admin}")
    except Exception as e:
        print(f"❌ Error in admin check: {e}")
        return
    
    print()
    
    # Test 4: Try to execute the command
    print("4. Executing trigger_clockout command...")
    try:
        await command_handlers.trigger_clockout_command(update, context)
        print("✅ Command executed successfully")
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        logger.error(f"Error: {e}", exc_info=True)
    
    print()
    print("=== Test completed ===")

if __name__ == "__main__":
    asyncio.run(test_trigger_clockout()) 