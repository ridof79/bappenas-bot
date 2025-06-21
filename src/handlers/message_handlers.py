import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.database.database import Database
from src.config.settings import Settings
from src.utils.helpers import (
    get_current_time, parse_time_string, validate_configuration,
    get_enabled_days_display, format_configuration_display
)

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, database: Database, callback_handlers):
        self.db = database
        self.callback_handlers = callback_handlers
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user = update.effective_user
        message_text = update.message.text
        
        # Check if user is in configuration state
        user_state = self.callback_handlers.get_user_state(user.id)
        if user_state:
            await self.handle_configuration_input(update, context, user_state, message_text)
            return
        
        # Handle other text messages
        await update.message.reply_text(
            "Gunakan perintah /help untuk melihat daftar perintah yang tersedia."
        )
    
    async def handle_configuration_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                       user_state: dict, message_text: str):
        """Handle configuration input from user"""
        user = update.effective_user
        chat_id = user_state['chat_id']
        config_type = user_state['config_type']
        input_type = user_state['type']
        
        try:
            if input_type == 'time':
                await self.handle_time_input(update, context, user_state, message_text)
            elif input_type == 'interval':
                await self.handle_interval_input(update, context, user_state, message_text)
            else:
                await update.message.reply_text("❌ Jenis input tidak valid")
                
        except Exception as e:
            logger.error(f"Error handling configuration input: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat memproses input")
        finally:
            # Clear user state
            self.callback_handlers.clear_user_state(user.id)
    
    async def handle_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              user_state: dict, message_text: str):
        """Handle time input for configuration"""
        user = update.effective_user
        chat_id = user_state['chat_id']
        config_type = user_state['config_type']
        
        # Parse time input (format: HH:MM-HH:MM)
        if '-' not in message_text:
            await update.message.reply_text(
                "❌ Format waktu salah!\n\n"
                "Gunakan format: START_TIME-END_TIME\n"
                "Contoh: 08:00-09:00"
            )
            return
        
        start_time_str, end_time_str = message_text.split('-', 1)
        
        # Validate time format
        start_time = parse_time_string(start_time_str.strip())
        end_time = parse_time_string(end_time_str.strip())
        
        if not start_time or not end_time:
            await update.message.reply_text(
                "❌ Format waktu tidak valid!\n\n"
                "Gunakan format HH:MM\n"
                "Contoh: 08:00, 17:30"
            )
            return
        
        if start_time >= end_time:
            await update.message.reply_text(
                "❌ Waktu mulai harus lebih awal dari waktu selesai!"
            )
            return
        
        # Get current configuration
        current_config = self.db.get_configuration(chat_id, config_type)
        
        if current_config:
            interval = current_config['reminder_interval']
            enabled_days = current_config['enabled_days']
        else:
            interval = Settings.DEFAULT_REMINDER_INTERVAL
            enabled_days = Settings.DEFAULT_ENABLED_DAYS
        
        # Save configuration
        success = self.db.save_configuration(
            chat_id, config_type, 
            start_time_str.strip(), end_time_str.strip(), 
            interval, enabled_days
        )
        
        if success:
            await update.message.reply_text(
                f"✅ Waktu {Settings.get_clock_type_name(config_type)} berhasil diatur!\n\n"
                f"🕐 **{start_time_str.strip()} - {end_time_str.strip()}**\n\n"
                f"Gunakan /config untuk melihat konfigurasi lengkap.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text("❌ Gagal menyimpan konfigurasi")
    
    async def handle_interval_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  user_state: dict, message_text: str):
        """Handle interval input for configuration"""
        user = update.effective_user
        chat_id = user_state['chat_id']
        config_type = user_state['config_type']
        
        try:
            interval = int(message_text.strip())
        except ValueError:
            await update.message.reply_text(
                "❌ Interval harus berupa angka!\n\n"
                "Contoh: 15 untuk setiap 15 menit"
            )
            return
        
        if interval < 1 or interval > 1440:
            await update.message.reply_text(
                "❌ Interval harus antara 1-1440 menit!\n\n"
                "Contoh: 15 untuk setiap 15 menit"
            )
            return
        
        # Get current configuration
        current_config = self.db.get_configuration(chat_id, config_type)
        
        if current_config:
            start_time = current_config['start_time']
            end_time = current_config['end_time']
            enabled_days = current_config['enabled_days']
        else:
            if config_type == 'clock_in':
                start_time = Settings.DEFAULT_CLOCK_IN_START
                end_time = Settings.DEFAULT_CLOCK_IN_END
            else:
                start_time = Settings.DEFAULT_CLOCK_OUT_START
                end_time = Settings.DEFAULT_CLOCK_OUT_END
            enabled_days = Settings.DEFAULT_ENABLED_DAYS
        
        # Save configuration
        success = self.db.save_configuration(
            chat_id, config_type, start_time, end_time, interval, enabled_days
        )
        
        if success:
            await update.message.reply_text(
                f"✅ Interval {Settings.get_clock_type_name(config_type)} berhasil diatur!\n\n"
                f"⏰ **Setiap {interval} menit**\n\n"
                f"Gunakan /config untuk melihat konfigurasi lengkap.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text("❌ Gagal menyimpan konfigurasi")
    
    async def send_clock_in_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send clock in reminder to all active chats"""
        current_time = get_current_time()
        
        # Get all chat groups
        chat_groups = self.db.get_all_chat_groups()
        
        for chat_group in chat_groups:
            chat_id = chat_group['chat_id']
            
            try:
                # Get configuration
                config = self.db.get_configuration(chat_id, 'clock_in')
                if not config:
                    continue
                
                # Check if today is enabled day
                if current_time.weekday() not in config['enabled_days']:
                    continue
                
                # Check if current time is within the configured time range
                start_time = parse_time_string(config['start_time'])
                end_time = parse_time_string(config['end_time'])
                current_time_obj = current_time.time()
                
                if not (start_time <= current_time_obj <= end_time):
                    continue
                
                # Get today's attendance
                today_attendance = self.db.get_today_attendance(chat_id, current_time)
                
                # Check if reminder should be sent (simplified logic)
                clock_in_count = len(today_attendance.get('clock_in', {}))
                
                if clock_in_count == 0:
                    # No one has clocked in yet, send reminder
                    message = (
                        f"⏰ **Pengingat Clock In** - {current_time.strftime('%H:%M')}\n\n"
                        f"Belum ada yang clock in hari ini!\n\n"
                        f"Silakan gunakan /clockin untuk mencatat kehadiran."
                    )
                    
                    keyboard = [
                        [InlineKeyboardButton("🕐 Clock In", callback_data="clock_in_button")],
                        [InlineKeyboardButton("📊 Cek Status", callback_data="refresh_attendance")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    logger.info(f"Clock-in reminder sent to chat {chat_id}")
                
            except Exception as e:
                logger.error(f"Error sending clock-in reminder to {chat_id}: {e}")
    
    async def send_clock_out_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send clock out reminder to all active chats"""
        current_time = get_current_time()
        
        # Get all chat groups
        chat_groups = self.db.get_all_chat_groups()
        
        for chat_group in chat_groups:
            chat_id = chat_group['chat_id']
            
            try:
                # Get configuration
                config = self.db.get_configuration(chat_id, 'clock_out')
                if not config:
                    continue
                
                # Check if today is enabled day
                if current_time.weekday() not in config['enabled_days']:
                    continue
                
                # Check if current time is within the configured time range
                start_time = parse_time_string(config['start_time'])
                end_time = parse_time_string(config['end_time'])
                current_time_obj = current_time.time()
                
                if not (start_time <= current_time_obj <= end_time):
                    continue
                
                # Get today's attendance
                today_attendance = self.db.get_today_attendance(chat_id, current_time)
                
                # Check if reminder should be sent
                clock_in_count = len(today_attendance.get('clock_in', {}))
                clock_out_count = len(today_attendance.get('clock_out', {}))
                
-21 08:08:10.555282+00:00)
Jun 21 15:08:10 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:10,565 - apscheduler.executors.default - INFO - Running job "clock_out_reminder_job (trigger: interval[0:05:00], next run at: 2025-06-21 08:13:10 UTC)" (scheduled at 2025-06-21 08:08:10.557102+00:00)
Jun 21 15:08:10 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:10,567 - apscheduler.executors.default - INFO - Job "clock_in_reminder_job (trigger: interval[0:05:00], next run at: 2025-06-21 08:13:10 UTC)" executed successfully
Jun 21 15:08:10 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:10,567 - apscheduler.executors.default - INFO - Job "clock_out_reminder_job (trigger: interval[0:05:00], next run at: 2025-06-21 08:13:10 UTC)" executed successfully
Jun 21 15:08:11 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:11,438 - httpx - INFO - HTTP Request: POST https://api.telegram.org/bot8088809720:AAEHRay1cECIgswQaQNfZ0ioHsXRY5ZJl4k/getUpdates "HTTP/1.1 200 OK"
Jun 21 15:08:16 ip-172-31-95-75 systemd[1]: Stopping telegram-bot.service - Telegram Attendance Bot...
Jun 21 15:08:16 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:16,965 - httpx - INFO - HTTP Request: POST https://api.telegram.org/bot8088809720:AAEHRay1cECIgswQaQNfZ0ioHsXRY5ZJl4k/getUpdates "HTTP/1.1 200 OK"
Jun 21 15:08:16 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:16,966 - telegram.ext.Application - INFO - Application is stopping. This might take a moment.
Jun 21 15:08:16 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:16,966 - apscheduler.scheduler - INFO - Scheduler has been shut down
Jun 21 15:08:16 ip-172-31-95-75 telegram-bot[27862]: 2025-06-21 08:08:16,977 - telegram.ext.Application - INFO - Application.stop() complete
Jun 21 15:08:17 ip-172-31-95-75 systemd[1]: telegram-bot.service: Deactivated successfully.
Jun 21 15:08:17 ip-172-31-95-75 systemd[1]: Stopped telegram-bot.service - Telegram Attendance Bot.
Jun 21 15:08:17 ip-172-31-95-75 systemd[1]: Started telegram-bot.service - Telegram Attendance Bot.
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,408 - src.database.database - INFO - Database initialized successfully
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,493 - apscheduler.scheduler - INFO - Adding job tentatively -- it will be properly scheduled when the scheduler starts
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,493 - apscheduler.scheduler - INFO - Adding job tentatively -- it will be properly scheduled when the scheduler starts
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,494 - __main__ - INFO - Starting Attendance Bot...
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,756 - httpx - INFO - HTTP Request: POST https://api.telegram.org/bot8088809720:AAEHRay1cECIgswQaQNfZ0ioHsXRY5ZJl4k/getMe "HTTP/1.1 200 OK"
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,841 - httpx - INFO - HTTP Request: POST https://api.telegram.org/bot8088809720:AAEHRay1cECIgswQaQNfZ0ioHsXRY5ZJl4k/deleteWebhook "HTTP/1.1 200 OK"
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,843 - apscheduler.scheduler - INFO - Added job "clock_in_reminder_job" to job store "default"
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,843 - apscheduler.scheduler - INFO - Added job "clock_out_reminder_job" to job store "default"
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,843 - apscheduler.scheduler - INFO - Scheduler started
Jun 21 15:08:17 ip-172-31-95-75 telegram-bot[28156]: 2025-06-21 15:08:17,843 - telegram.ext.Application - INFO - Application started                # Send reminder if it's time for clock out, regardless of clock in status
                message = (
                    f"🌆 **Pengingat Clock Out** - {current_time.strftime('%H:%M')}\n\n"
                    f"Jangan lupa clock out!\n\n"
                    f"🟢 Clock In: {clock_in_count} orang\n"
                    f"🔴 Clock Out: {clock_out_count} orang\n\n"
                    f"Gunakan /clockout untuk mencatat pulang."
                )
                
                keyboard = [
                    [InlineKeyboardButton("🕕 Clock Out", callback_data="clock_out_button")],
                    [InlineKeyboardButton("📊 Cek Status", callback_data="refresh_attendance")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Clock-out reminder sent to chat {chat_id}")
                
            except Exception as e:
                logger.error(f"Error sending clock-out reminder to {chat_id}: {e}") 