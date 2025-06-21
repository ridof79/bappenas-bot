import logging
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.database.database import Database
from src.config.settings import Settings
from src.utils.helpers import get_current_time, parse_time_string

logger = logging.getLogger(__name__)

class ScheduledHandlers:
    def __init__(self, database: Database):
        self.db = database
    
    async def send_clock_in_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Send daily clock in message with interactive buttons"""
        chat_id = context.job.chat_id
        
        try:
            current_time = get_current_time().strftime("%H:%M")
            message = (
                f"🌅 **Selamat Pagi!** - {current_time}\n\n"
                f"⏰ Waktunya untuk clock in!\n\n"
                f"Silakan klik tombol di bawah atau gunakan perintah /clockin"
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
            logger.info(f"Clock-in message sent to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error sending clock-in message to {chat_id}: {e}")
    
    async def send_clock_out_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Send daily clock out message with interactive buttons"""
        chat_id = context.job.chat_id
        
        try:
            current_time = get_current_time().strftime("%H:%M")
            message = (
                f"🌆 **Selamat Sore!** - {current_time}\n\n"
                f"⏰ Waktunya untuk clock out!\n\n"
                f"Silakan klik tombol di bawah atau gunakan perintah /clockout"
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
            logger.info(f"Clock-out message sent to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error sending clock-out message to {chat_id}: {e}")
    
    async def send_clock_in_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder for members who haven't clocked in"""
        chat_id = context.job.chat_id
        current_time = get_current_time()
        
        try:
            # Get configuration for this chat
            config = self.db.get_configuration(chat_id, 'clock_in')
            if not config:
                return  # No configuration set
            
            # Check if today is enabled day
            if current_time.weekday() not in config['enabled_days']:
                return
            
            # Check if current time is within the configured time range
            start_time = parse_time_string(config['start_time'])
            end_time = parse_time_string(config['end_time'])
            current_time_obj = current_time.time()
            
            if not (start_time <= current_time_obj <= end_time):
                return
            
            # Get all administrators (simplified - in real implementation you'd get all members)
            chat_members = []
            try:
                async for member in context.bot.get_chat_administrators(chat_id):
                    if not member.user.is_bot:
                        chat_members.append(member.user)
            except Exception as e:
                logger.error(f"Error getting chat members: {e}")
                return
            
            # Get today's attendance
            today_attendance = self.db.get_today_attendance(chat_id, current_time)
            not_clocked_in = []
            
            # Check who hasn't clocked in
            for member in chat_members:
                user_id_str = str(member.id)
                if user_id_str not in today_attendance.get('clock_in', {}):
                    mention = f"@{member.username}" if member.username else member.first_name
                    not_clocked_in.append(mention)
            
            if not_clocked_in:
                current_time_str = current_time.strftime("%H:%M")
                message = (
                    f"⏰ **Pengingat Clock In** - {current_time_str}\n\n"
                    f"❗ Anggota yang belum clock in:\n"
                    f"{' '.join(not_clocked_in)}\n\n"
                    f"Silakan gunakan /clockin atau klik tombol di bawah!"
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
        """Send reminder for members who haven't clocked out"""
        chat_id = context.job.chat_id
        current_time = get_current_time()
        
        try:
            # Get configuration for this chat
            config = self.db.get_configuration(chat_id, 'clock_out')
            if not config:
                return  # No configuration set
            
            # Check if today is enabled day
            if current_time.weekday() not in config['enabled_days']:
                return
            
            # Check if current time is within the configured time range
            start_time = parse_time_string(config['start_time'])
            end_time = parse_time_string(config['end_time'])
            current_time_obj = current_time.time()
            
            if not (start_time <= current_time_obj <= end_time):
                return
            
            # Get all administrators (simplified - in real implementation you'd get all members)
            chat_members = []
            try:
                async for member in context.bot.get_chat_administrators(chat_id):
                    if not member.user.is_bot:
                        chat_members.append(member.user)
            except Exception as e:
                logger.error(f"Error getting chat members: {e}")
                return
            
            # Get today's attendance
            today_attendance = self.db.get_today_attendance(chat_id, current_time)
            not_clocked_out = []
            
            # Check who has clocked in but not clocked out
            for member in chat_members:
                user_id_str = str(member.id)
                if (user_id_str in today_attendance.get('clock_in', {}) and 
                    user_id_str not in today_attendance.get('clock_out', {})):
                    mention = f"@{member.username}" if member.username else member.first_name
                    not_clocked_out.append(mention)
            
            if not_clocked_out:
                current_time_str = current_time.strftime("%H:%M")
                message = (
                    f"🌆 **Pengingat Clock Out** - {current_time_str}\n\n"
                    f"❗ Anggota yang belum clock out:\n"
                    f"{' '.join(not_clocked_out)}\n\n"
                    f"Jangan lupa clock out! Gunakan /clockout atau klik tombol!"
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
    
    async def handle_clock_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle clock in/out button clicks"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        chat_id = query.message.chat.id
        current_time = get_current_time()
        
        if query.data == "clock_in_button":
            # Handle clock in button
            today_attendance = self.db.get_today_attendance(chat_id, current_time)
            user_id_str = str(user.id)
            
            if user_id_str in today_attendance.get('clock_in', {}):
                await query.answer("Anda sudah clock in hari ini!", show_alert=True)
                return
            
            # Record clock in
            success = self.db.record_attendance(
                chat_id=chat_id,
                user_id=user.id,
                user_name=user.first_name or user.username or 'Unknown',
                username=user.username,
                clock_type='in',
                clock_time=current_time
            )
            
            if success:
                await query.answer(f"✅ Clock in berhasil pada {current_time.strftime('%H:%M:%S')}")
            else:
                await query.answer("❌ Gagal mencatat clock in", show_alert=True)
        
        elif query.data == "clock_out_button":
            # Handle clock out button
            today_attendance = self.db.get_today_attendance(chat_id, current_time)
            user_id_str = str(user.id)
            
            if user_id_str not in today_attendance.get('clock_in', {}):
                await query.answer("Anda harus clock in terlebih dahulu!", show_alert=True)
                return
            
            if user_id_str in today_attendance.get('clock_out', {}):
                await query.answer("Anda sudah clock out hari ini!", show_alert=True)
                return
            
            # Record clock out
            success = self.db.record_attendance(
                chat_id=chat_id,
                user_id=user.id,
                user_name=user.first_name or user.username or 'Unknown',
                username=user.username,
                clock_type='out',
                clock_time=current_time
            )
            
            if success:
                await query.answer(f"✅ Clock out berhasil pada {current_time.strftime('%H:%M:%S')}")
            else:
                await query.answer("❌ Gagal mencatat clock out", show_alert=True)
    
    async def handle_refresh_attendance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle refresh attendance button"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat.id
        current_time = get_current_time()
        today_attendance = self.db.get_today_attendance(chat_id, current_time)
        
        clock_in_count = len(today_attendance.get('clock_in', {}))
        clock_out_count = len(today_attendance.get('clock_out', {}))
        
        message = (
            f"📊 **Status Kehadiran Hari Ini**\n\n"
            f"🟢 **Clock In:** {clock_in_count} orang\n"
            f"🔴 **Clock Out:** {clock_out_count} orang\n"
            f"📅 Tanggal: {current_time.strftime('%d/%m/%Y')}\n"
            f"⏰ Waktu: {current_time.strftime('%H:%M:%S')}"
        )
        
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
    
    def schedule_daily_messages(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Schedule daily clock-in and clock-out messages plus reminders"""
        job_queue = context.application.job_queue
        
        # Remove existing jobs for this chat if any
        job_names = [
            f"clock_in_{chat_id}",
            f"clock_out_{chat_id}",
            f"clock_in_reminder_{chat_id}",
            f"clock_out_reminder_{chat_id}"
        ]
        
        for job_name in job_names:
            current_jobs = job_queue.get_jobs_by_name(job_name)
            for job in current_jobs:
                job.schedule_removal()
        
        # Get configurations
        clock_in_config = self.db.get_configuration(chat_id, 'clock_in')
        clock_out_config = self.db.get_configuration(chat_id, 'clock_out')
        
        # Schedule clock-in message
        if clock_in_config:
            start_time = parse_time_string(clock_in_config['start_time'])
            if start_time:
                job_queue.run_daily(
                    self.send_clock_in_message,
                    start_time,
                    chat_id=chat_id,
                    name=f"clock_in_{chat_id}"
                )
        
        # Schedule clock-out message
        if clock_out_config:
            start_time = parse_time_string(clock_out_config['start_time'])
            if start_time:
                job_queue.run_daily(
                    self.send_clock_out_message,
                    start_time,
                    chat_id=chat_id,
                    name=f"clock_out_{chat_id}"
                )
        
        # Schedule reminders based on configuration
        if clock_in_config:
            self._schedule_reminders(chat_id, context, 'clock_in', clock_in_config)
        
        if clock_out_config:
            self._schedule_reminders(chat_id, context, 'clock_out', clock_out_config)
        
        logger.info(f"Scheduled daily messages and reminders for chat {chat_id}")
    
    def _schedule_reminders(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE, 
                          config_type: str, config: dict):
        """Schedule reminders based on configuration"""
        job_queue = context.application.job_queue
        interval = config['reminder_interval']
        
        # Calculate reminder times based on start and end time
        start_time = parse_time_string(config['start_time'])
        end_time = parse_time_string(config['end_time'])
        
        if not start_time or not end_time:
            return
        
        # Schedule reminders at regular intervals
        current_time = start_time
        reminder_count = 0
        
        while current_time <= end_time and reminder_count < 10:  # Max 10 reminders
            if config_type == 'clock_in':
                job_queue.run_daily(
                    self.send_clock_in_reminder,
                    current_time,
                    chat_id=chat_id,
                    name=f"clock_in_reminder_{chat_id}_{reminder_count}"
                )
            else:
                job_queue.run_daily(
                    self.send_clock_out_reminder,
                    current_time,
                    chat_id=chat_id,
                    name=f"clock_out_reminder_{chat_id}_{reminder_count}"
                )
            
            # Add interval minutes
            current_time = time(
                hour=(current_time.hour + (current_time.minute + interval) // 60) % 24,
                minute=(current_time.minute + interval) % 60
            )
            reminder_count += 1 