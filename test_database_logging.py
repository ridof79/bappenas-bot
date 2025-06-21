#!/usr/bin/env python3
"""
Test script untuk mengecek logging database operations
"""

import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database import Database
from src.config.settings import Settings
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_test.log')
    ]
)

logger = logging.getLogger(__name__)

def test_database_logging():
    """Test semua operasi database dengan logging"""
    
    print("🧪 Testing Database Logging Operations")
    print("=" * 50)
    
    # Initialize database
    db = Database("test_attendance.db")
    db.init_database()
    
    # Test 1: Add chat group
    print("\n1️⃣ Testing add_chat_group...")
    success = db.add_chat_group(123456789, "Test Group", "supergroup")
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 2: Save configuration
    print("\n2️⃣ Testing save_configuration...")
    success = db.save_configuration(
        chat_id=123456789,
        config_type='clock_in',
        start_time='08:00',
        end_time='09:00',
        reminder_interval=15,
        enabled_days=[0, 1, 2, 3, 4]
    )
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: Record attendance
    print("\n3️⃣ Testing record_attendance...")
    current_time = datetime.now()
    success = db.record_attendance(
        chat_id=123456789,
        user_id=987654321,
        user_name="Test User",
        username="testuser",
        clock_type='in',
        clock_time=current_time
    )
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 4: Get configuration
    print("\n4️⃣ Testing get_configuration...")
    config = db.get_configuration(123456789, 'clock_in')
    if config:
        print(f"✅ Config found: {config}")
    else:
        print("❌ No config found")
    
    # Test 5: Get chat groups
    print("\n5️⃣ Testing get_all_chat_groups...")
    chat_groups = db.get_all_chat_groups()
    print(f"✅ Found {len(chat_groups)} chat groups")
    for group in chat_groups:
        print(f"   - {group['chat_title']} (ID: {group['chat_id']})")
    
    print("\n📝 Check 'database_test.log' file for detailed logs!")
    print("=" * 50)

if __name__ == "__main__":
    test_database_logging() 