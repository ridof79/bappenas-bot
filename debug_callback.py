#!/usr/bin/env python3
"""
Debug script for callback data parsing
"""

def test_callback_parsing():
    """Test callback data parsing"""
    
    print("🔍 Testing callback data parsing...")
    
    # Test cases
    test_cases = [
        "day_clock_in_0",
        "day_clock_out_1", 
        "day_clock_in_5",
        "clock_in_button",
        "clock_out_button",
        "refresh_attendance",
        "config_clock_in",
        "set_clock_in_time",
        "save_clock_in",
        "cancel_config"
    ]
    
    for data in test_cases:
        print(f"\n📝 Testing: {data}")
        
        try:
            parts = data.split('_')
            print(f"   Parts: {parts}")
            
            if data.startswith("day_"):
                if len(parts) == 3:
                    config_type = parts[1]
                    day_num_str = parts[2]
                    
                    print(f"   Config type: {config_type}")
                    print(f"   Day num string: {day_num_str}")
                    
                    # Validate config_type
                    if config_type not in ['clock_in', 'clock_out']:
                        print(f"   ❌ Invalid config_type: {config_type}")
                        continue
                    
                    # Validate and convert day_num
                    try:
                        day_num = int(day_num_str)
                        if day_num < 0 or day_num > 6:
                            print(f"   ❌ Invalid day number: {day_num}")
                            continue
                        print(f"   ✅ Valid day number: {day_num}")
                    except ValueError:
                        print(f"   ❌ Cannot convert to int: {day_num_str}")
                        continue
                else:
                    print(f"   ❌ Invalid day callback format: {len(parts)} parts")
                    
            elif data in ["clock_in_button", "clock_out_button"]:
                print(f"   ✅ Clock button callback")
                
            elif data == "refresh_attendance":
                print(f"   ✅ Refresh attendance callback")
                
            elif data.startswith("config_"):
                print(f"   ✅ Config callback")
                
            elif data.startswith("set_"):
                print(f"   ✅ Set callback")
                
            elif data.startswith("save_"):
                print(f"   ✅ Save callback")
                
            elif data.startswith("cancel_"):
                print(f"   ✅ Cancel callback")
                
            else:
                print(f"   ❓ Unknown callback type")
                
        except Exception as e:
            print(f"   ❌ Error parsing: {e}")
    
    print("\n✅ Callback parsing test completed!")

if __name__ == "__main__":
    test_callback_parsing() 