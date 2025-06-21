#!/usr/bin/env python3
"""
Debug script for callback data parsing
"""

def test_callback_parsing():
    """Test callback data parsing"""
    print("🔍 Testing callback data parsing...")
    
    # Test cases with correct formats
    test_cases = [
        "day_0",           # Day toggle for day 0 (Monday)
        "day_1",           # Day toggle for day 1 (Tuesday)
        "day_5",           # Day toggle for day 5 (Saturday)
        "clock_in_button", # Clock in button
        "clock_out_button", # Clock out button
        "refresh_attendance", # Refresh attendance
        "config_clock_in", # Config callback
        "set_clock_in_time", # Set callback
        "save_clock_in",   # Save callback
        "cancel_config"    # Cancel callback
    ]
    
    for callback_data in test_cases:
        print(f"\n📝 Testing: {callback_data}")
        parts = callback_data.split('_')
        print(f"   Parts: {parts}")
        
        if callback_data.startswith("day_"):
            if len(parts) == 2:
                try:
                    day_num = int(parts[1])
                    if 0 <= day_num <= 6:
                        print(f"   ✅ Valid day callback: day {day_num}")
                    else:
                        print(f"   ❌ Invalid day number: {day_num}")
                except ValueError:
                    print(f"   ❌ Invalid day number format: {parts[1]}")
            else:
                print(f"   ❌ Invalid day callback format: {len(parts)} parts")
        
        elif callback_data in ["clock_in_button", "clock_out_button"]:
            print(f"   ✅ Clock button callback")
        
        elif callback_data == "refresh_attendance":
            print(f"   ✅ Refresh attendance callback")
        
        elif callback_data.startswith("config_"):
            print(f"   ✅ Config callback")
        
        elif callback_data.startswith("set_"):
            print(f"   ✅ Set callback")
        
        elif callback_data.startswith("save_"):
            print(f"   ✅ Save callback")
        
        elif callback_data.startswith("cancel_"):
            print(f"   ✅ Cancel callback")
        
        else:
            print(f"   ❓ Unknown callback format")
    
    print("\n✅ Callback parsing test completed!")

if __name__ == "__main__":
    test_callback_parsing() 