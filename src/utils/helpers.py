from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
import pytz
from src.config.settings import Settings

def get_current_time() -> datetime:
    """Get current time in configured timezone"""
    return datetime.now(Settings.get_timezone())

def parse_time_string(time_str: str) -> Optional[time]:
    """Parse time string in HH:MM format to time object"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)
    except (ValueError, AttributeError):
        return None

def format_time_display(time_obj: time) -> str:
    """Format time object to HH:MM display string"""
    return time_obj.strftime('%H:%M')

def is_time_between(current_time: time, start_time: time, end_time: time) -> bool:
    """
    Check if current time is between start and end time

    Handles both same-day ranges (start_time <= end_time) and
    overnight ranges (start_time > end_time, e.g., 22:00 to 06:00)
    """
    # Convert all times to minutes since midnight for easier comparison
    current_mins = current_time.hour * 60 + current_time.minute
    start_mins = start_time.hour * 60 + start_time.minute
    end_mins = end_time.hour * 60 + end_time.minute

    if start_mins <= end_mins:
        # Same day range (e.g., 09:00 to 17:00)
        return start_mins <= current_mins <= end_mins
    else:
        # Overnight range (e.g., 22:00 to 06:00)
        return current_mins >= start_mins or current_mins <= end_mins

def is_workday(date: datetime) -> bool:
    """Check if given date is a workday (Monday-Friday)"""
    return date.weekday() < 5

def get_enabled_days_display(enabled_days: List[int]) -> str:
    """Convert enabled days list to display string"""
    day_names = []
    for day in sorted(enabled_days):
        day_names.append(Settings.get_day_name(day))
    return ', '.join(day_names)

def format_attendance_report(attendance_data: Dict, date: datetime) -> str:
    """Format attendance data into a readable report"""
    date_str = date.strftime('%d/%m/%Y')
    report = f"📊 **Laporan Kehadiran - {date_str}**\n\n"

    # Clock in section
    clock_in_count = len(attendance_data.get('clock_in', {}))
    report += f"🟢 **Clock In ({clock_in_count} orang):**\n"
    if clock_in_count > 0:
        for user_id, data in attendance_data['clock_in'].items():
            report += f"• {data['name']} - {data['time']}\n"
    else:
        report += "Belum ada yang clock in\n"

    report += "\n"

    # Clock out section
    clock_out_count = len(attendance_data.get('clock_out', {}))
    report += f"🔴 **Clock Out ({clock_out_count} orang):**\n"
    if clock_out_count > 0:
        for user_id, data in attendance_data['clock_out'].items():
            report += f"• {data['name']} - {data['time']}\n"
    else:
        report += "Belum ada yang clock out\n"

    return report

def create_mention_list(user_ids: List[int]) -> str:
    """
    Create mention list for users using Telegram's tg://user?id= format
    This creates clickable mentions that work even without knowing the username
    """
    mentions = []
    for user_id in user_ids:
        # Use Telegram's internal mention format that works with user IDs
        mentions.append(f"[User {user_id}](tg://user?id={user_id})")
    return ' '.join(mentions)

def validate_configuration(start_time: str, end_time: str, 
                         reminder_interval: int, enabled_days: List[int]) -> Dict[str, str]:
    """Validate configuration parameters and return error messages"""
    errors = {}

    if not Settings.validate_time_format(start_time):
        errors['start_time'] = "Format waktu tidak valid. Gunakan format HH:MM"

    if not Settings.validate_time_format(end_time):
        errors['end_time'] = "Format waktu tidak valid. Gunakan format HH:MM"

    if not Settings.validate_reminder_interval(reminder_interval):
        errors['reminder_interval'] = "Interval pengingat harus antara 1-1440 menit"

    if not Settings.validate_enabled_days(enabled_days):
        errors['enabled_days'] = "Hari yang diaktifkan tidak valid"

    return errors

def get_next_reminder_time(current_time: datetime, reminder_interval: int) -> datetime:
    """Calculate next reminder time based on current time and interval"""
    return current_time + timedelta(minutes=reminder_interval)

def format_configuration_display(config: dict) -> str:
    """Format configuration for display"""
    config_type = config.get('config_type', 'unknown')
    start_time = config.get('start_time', 'N/A')
    end_time = config.get('end_time', 'N/A')
    interval = config.get('reminder_interval', 'N/A')
    enabled_days = config.get('enabled_days', [])

    # Get clock type name
    if config_type == 'clock_in':
        clock_name = "🟢 **Clock In**"
    elif config_type == 'clock_out':
        clock_name = "🔴 **Clock Out**"
    else:
        clock_name = f"⚙️ **{config_type.replace('_', ' ').title()}**"

    # Format enabled days
    days_display = get_enabled_days_display(enabled_days)

    formatted = f"{clock_name}:\n"
    formatted += f"🕐 Waktu: {start_time} - {end_time}\n"
    formatted += f"⏰ Interval: {interval} menit\n"
    formatted += f"📅 Hari: {days_display}\n\n"

    return formatted 
