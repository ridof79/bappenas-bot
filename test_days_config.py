#!/usr/bin/env python3
"""
Test script for day configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database import Database
from src.config.settings import Settings

def test_day_configuration():
    """Test day configuration functionality"""
    
    print("🧪 Testing day configuration...")
    
    # Initialize database
    db = Database("data/attendance.db")
    
    # Test chat ID
    test_chat_id = 123456789
    
    print(f"📊 Testing with chat ID: {test_chat_id}")
    
    # Test 1: Get configuration when none exists
    print("\n1. Testing get_configuration when none exists...")
    config = db.get_configuration(test_chat_id, 'clock_in')
    print(f"   Result: {config}")
    
    # Test 2: Save configuration with default days
    print("\n2. Testing save_configuration with default days...")
    success = db.save_configuration(
        chat_id=test_chat_id,
        config_type='clock_in',
        start_time="07:00",
        end_time="09:00",
        reminder_interval=15,
        enabled_days=[0, 1, 2, 3, 4]  # Monday to Friday
    )
    print(f"   Result: {success}")
    
    # Test 3: Get configuration after saving
    print("\n3. Testing get_configuration after saving...")
    config = db.get_configuration(test_chat_id, 'clock_in')
    print(f"   Result: {config}")
    
    if config:
        print(f"   Enabled days: {config.get('enabled_days', [])}")
        print(f"   Start time: {config.get('start_time', 'N/A')}")
        print(f"   End time: {config.get('end_time', 'N/A')}")
    
    # Test 4: Update configuration with different days
    print("\n4. Testing update configuration with different days...")
    success = db.save_configuration(
        chat_id=test_chat_id,
        config_type='clock_in',
        start_time="07:00",
        end_time="09:00",
        reminder_interval=15,
        enabled_days=[0, 1, 2, 3, 4, 5]  # Monday to Saturday
    )
    print(f"   Result: {success}")
    
    # Test 5: Get updated configuration
    print("\n5. Testing get_configuration after update...")
    config = db.get_configuration(test_chat_id, 'clock_in')
    print(f"   Result: {config}")
    
    if config:
        print(f"   Enabled days: {config.get('enabled_days', [])}")
    
    # Test 6: Test day names
    print("\n6. Testing day names...")
    for day_num in range(7):
        day_name = Settings.get_day_name(day_num)
        print(f"   Day {day_num}: {day_name}")
    
    print("\n✅ Day configuration test completed!")

if __name__ == "__main__":
    test_day_configuration() 