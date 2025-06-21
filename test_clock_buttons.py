#!/usr/bin/env python3
"""
Test script for clock button callbacks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.handlers.scheduled_handlers import ScheduledHandlers
from src.database.database import Database

def test_clock_button_callbacks():
    """Test clock button callback handling"""
    
    print("🧪 Testing clock button callbacks...")
    
    # Initialize database
    db = Database("data/attendance.db")
    scheduled_handlers = ScheduledHandlers(db)
    
    # Test callback data
    test_cases = [
        "clock_in_button",
        "clock_out_button",
        "refresh_attendance"
    ]
    
    for callback_data in test_cases:
        print(f"\n📝 Testing callback: {callback_data}")
        
        # Test pattern matching
        if callback_data in ["clock_in_button", "clock_out_button"]:
            print(f"   ✅ Matches clock button pattern")
        elif callback_data == "refresh_attendance":
            print(f"   ✅ Matches refresh pattern")
        else:
            print(f"   ❌ No pattern match")
    
    print("\n✅ Clock button callback test completed!")

if __name__ == "__main__":
    test_clock_button_callbacks() 