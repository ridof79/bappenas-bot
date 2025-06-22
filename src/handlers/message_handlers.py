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
    def __init__(self, database: Database, callback_handlers, scheduled_handlers=None):
        self.db = database
        self.callback_handlers = callback_handlers
        self.scheduled_handlers = scheduled_handlers

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
            # Reload scheduler with new configuration
            if self.scheduled_handlers:
                self.scheduled_handlers.schedule_daily_messages(chat_id, context)
                logger.info(f"Reloaded scheduler for chat {chat_id} after time configuration change")

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
            # Reload scheduler with new configuration
            if self.scheduled_handlers:
                self.scheduled_handlers.schedule_daily_messages(chat_id, context)
                logger.info(f"Reloaded scheduler for chat {chat_id} after interval configuration change")

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
        logger.info(f"=== DEBUG: send_clock_in_reminder called at {current_time} ===")

        # Get all chat groups
        chat_groups = self.db.get_all_chat_groups()
        logger.info(f"DEBUG: Found {len(chat_groups)} chat groups")

        for chat_group in chat_groups:
            chat_id = chat_group['chat_id']
            logger.info(f"DEBUG: Processing chat {chat_id}")

            try:
                # Get configuration
                config = self.db.get_configuration(chat_id, 'clock_in')
                if not config:
                    logger.info(f"DEBUG: No clock_in config for chat {chat_id}")
                    continue

                logger.info(f"DEBUG: Config found for chat {chat_id}: {config}")

                # Check if today is enabled day
                current_weekday = current_time.weekday()
                logger.info(f"DEBUG: Current weekday: {current_weekday}, Enabled days: {config['enabled_days']}")

                if current_weekday not in config['enabled_days']:
                    logger.info(f"DEBUG: Today ({current_weekday}) not in enabled days for chat {chat_id}")
                    continue

                # Check if current time is within the configured time range
                start_time = parse_time_string(config['start_time'])
                end_time = parse_time_string(config['end_time'])
                current_time_obj = current_time.time()

                logger.info(f"DEBUG: Time check - Current: {current_time_obj}, Start: {start_time}, End: {end_time}")

                if not (start_time <= current_time_obj <= end_time):
                    logger.info(f"DEBUG: Current time not in range for chat {chat_id}")
                    continue

                # Get today's attendance
                today_attendance = self.db.get_today_attendance(chat_id, current_time)

                # Check if reminder should be sent (simplified logic)
                clock_in_count = len(today_attendance.get('clock_in', {}))
                logger.info(f"DEBUG: Clock in count for chat {chat_id}: {clock_in_count}")

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
                    logger.info(f"✅ Clock-in reminder sent to chat {chat_id}")
                else:
                    logger.info(f"DEBUG: Skipping reminder for chat {chat_id} - already {clock_in_count} people clocked in")

            except Exception as e:
                logger.error(f"Error sending clock-in reminder to {chat_id}: {e}")

        logger.info("=== DEBUG: send_clock_in_reminder completed ===")

    async def send_clock_out_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send clock out reminder to all active chats"""
        current_time = get_current_time()
        logger.info(f"=== DEBUG: send_clock_out_reminder called at {current_time} ===")

        # Get all chat groups
        chat_groups = self.db.get_all_chat_groups()
        logger.info(f"DEBUG: Found {len(chat_groups)} chat groups")

        for chat_group in chat_groups:
            chat_id = chat_group['chat_id']
            logger.info(f"DEBUG: Processing chat {chat_id}")

            try:
                # Get configuration
                config = self.db.get_configuration(chat_id, 'clock_out')
                if not config:
                    logger.info(f"DEBUG: No clock_out config for chat {chat_id}")
                    continue

                logger.info(f"DEBUG: Config found for chat {chat_id}: {config}")

                # Check if today is enabled day
                current_weekday = current_time.weekday()
                logger.info(f"DEBUG: Current weekday: {current_weekday}, Enabled days: {config['enabled_days']}")

                if current_weekday not in config['enabled_days']:
                    logger.info(f"DEBUG: Today ({current_weekday}) not in enabled days for chat {chat_id}")
                    continue

                # Check if current time is within the configured time range
                start_time = parse_time_string(config['start_time'])
                end_time = parse_time_string(config['end_time'])
                current_time_obj = current_time.time()

                logger.info(f"DEBUG: Time check - Current: {current_time_obj}, Start: {start_time}, End: {end_time}")

                if not (start_time <= current_time_obj <= end_time):
                    logger.info(f"DEBUG: Current time not in range for chat {chat_id}")
                    continue

                # Get today's attendance
                today_attendance = self.db.get_today_attendance(chat_id, current_time)

                # Check if reminder should be sent
                clock_in_count = len(today_attendance.get('clock_in', {}))
                clock_out_count = len(today_attendance.get('clock_out', {}))
                logger.info(f"DEBUG: Attendance for chat {chat_id} - Clock in: {clock_in_count}, Clock out: {clock_out_count}")

                # Send reminder if it's time for clock out, regardless of clock in status
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
                logger.info(f"✅ Clock-out reminder sent to chat {chat_id}")

            except Exception as e:
                logger.error(f"Error sending clock-out reminder to {chat_id}: {e}")

        logger.info("=== DEBUG: send_clock_out_reminder completed ===") 
