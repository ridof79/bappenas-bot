#!/usr/bin/env python3
"""
Test script to check timezone and current time
"""

import pytz
from datetime import datetime
from src.config.settings import Settings

def test_timezone():
    """Test timezone configuration"""
    print("🌍 Testing Timezone Configuration...")
    
    # Get system timezone
    import os
    system_tz = os.environ.get('TZ', 'Not set')
    print(f"System TZ: {system_tz}")
    
    # Get system time
    system_time = datetime.now()
    print(f"System time: {system_time}")
    
    # Get configured timezone
    configured_tz = Settings.get_timezone()
    print(f"Configured timezone: {configured_tz}")
    
    # Get time in configured timezone
    configured_time = datetime.now(configured_tz)
    print(f"Configured time: {configured_time}")
    
    # Test time parsing
    test_time_str = "15:00"
    from src.utils.helpers import parse_time_string
    parsed_time = parse_time_string(test_time_str)
    print(f"Parsed time '{test_time_str}': {parsed_time}")
    
    # Test time comparison
    current_time_obj = configured_time.time()
    print(f"Current time object: {current_time_obj}")
    
    if parsed_time:
        is_within_range = parsed_time <= current_time_obj <= parsed_time
        print(f"Is current time within range {test_time_str}-{test_time_str}: {is_within_range}")
    
    print("\n✅ Timezone test completed!")

if __name__ == "__main__":
    test_timezone() 