#!/home/ubuntu/telegram-clock-bot/bot_env/bin/python3

import logging
import asyncio
import json
import os
from datetime import datetime, time, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import pytz

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Timezone (adjust according to your location)
TIMEZONE = pytz.timezone('Asia/Jakarta')  # Change this to your timezone

# Data storage file
DATA_FILE = 'attendance_data.json'

class ClockBot:
    def __init__(self):
        self.application = None
        self.scheduled_jobs = {}
        self.attendance_data = self.load_attendance_data()
    
    def load_attendance_data(self):
        """Load attendance data from file"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading attendance data: {e}")
            return {}
    
    def save_attendance_data(self):
        """Save attendance data to file"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.attendance_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving attendance data: {e}")
    
    def get_today_key(self):
        """Get today's date key"""
        return datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    
    def get_chat_data(self, chat_id):
        """Get or create chat data"""
        chat_id_str = str(chat_id)
        if chat_id_str not in self.attendance_data:
            self.attendance_data[chat_id_str] = {}
        return self.attendance_data[chat_id_str]
    
    def get_today_attendance(self, chat_id):
        """Get today's attendance for a chat"""
        chat_data = self.get_chat_data(chat_id)
        today = self.get_today_key()
        if today not in chat_data:
            chat_data[today] = {'clock_in': {}, 'clock_out': {}}
        return chat_data[today]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        await update.message.reply_text(
            "Hello! I'm your Clock Bot 🕐\n\n"
            "Features:\n"
            "• Automatic clock-in reminder at 08:00\n"
            "• Automatic clock-out reminder at 17:30\n"
            "• Use /ping to check if I'm active\n"
            "• Use /clockin to manually clock in\n"
            "• Use /clockout to manually clock out\n"
            "• Use /check to see attendance status\n"
            "• Use /status to get detailed attendance report\n"
            "• Add me as admin to your group to enable all features"
        )
    
    async def ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ping command handler"""
        current_time = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(
            f"🟢 Bot is active!\n"
            f"Current time: {current_time} (Jakarta)"
        )
    
    async def manual_clock_in(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manual clock in command"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("This command only works in groups!")
            return
        
        today_attendance = self.get_today_attendance(chat.id)
        user_id_str = str(user.id)
        
        if user_id_str in today_attendance['clock_in']:
            clock_in_time = today_attendance['clock_in'][user_id_str]['time']
            await update.message.reply_text(
                f"⚠️ {user.first_name}, you already clocked in today at {clock_in_time}"
            )
            return
        
        current_time = datetime.now(TIMEZONE)
        today_attendance['clock_in'][user_id_str] = {
            'name': user.first_name or user.username or 'Unknown',
            'username': user.username,
            'time': current_time.strftime("%H:%M:%S"),
            'timestamp': current_time.isoformat()
        }
        
        self.save_attendance_data()
        
        await update.message.reply_text(
            f"✅ {user.first_name} clocked in at {current_time.strftime('%H:%M:%S')}"
        )
    
    async def manual_clock_out(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manual clock out command"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("This command only works in groups!")
            return
        
        today_attendance = self.get_today_attendance(chat.id)
        user_id_str = str(user.id)
        
        if user_id_str not in today_attendance['clock_in']:
            await update.message.reply_text(
                f"⚠️ {user.first_name}, you need to clock in first!"
            )
            return
        
        if user_id_str in today_attendance['clock_out']:
            clock_out_time = today_attendance['clock_out'][user_id_str]['time']
            await update.message.reply_text(
                f"⚠️ {user.first_name}, you already clocked out today at {clock_out_time}"
            )
            return
        
        current_time = datetime.now(TIMEZONE)
        today_attendance['clock_out'][user_id_str] = {
            'name': user.first_name or user.username or 'Unknown',
            'username': user.username,
            'time': current_time.strftime("%H:%M:%S"),
            'timestamp': current_time.isoformat()
        }
        
        self.save_attendance_data()
        
        await update.message.reply_text(
            f"✅ {user.first_name} clocked out at {current_time.strftime('%H:%M:%S')}"
        )
    
    async def check_attendance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check attendance status and mention who hasn't clocked in/out"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("This command only works in groups!")
            return
        
        # Check if user is admin
        user = update.effective_user
        try:
            chat_member = await context.bot.get_chat_member(chat.id, user.id)
            if chat_member.status not in ['administrator', 'creator']:
                await update.message.reply_text("⚠️ Only administrators can use this command.")
                return
        except Exception:
            await update.message.reply_text("❌ Unable to verify admin status.")
            return
        
        try:
            # Get all chat members (this might be limited for large groups)
            chat_members = []
            admins = await context.bot.get_chat_administrators(chat.id)
            for member in admins:
                if not member.user.is_bot:
                    chat_members.append(member.user)
            
            # Note: For regular members, we can only track those who have interacted
            # with the bot or are in our attendance records
            today_attendance = self.get_today_attendance(chat.id)
            
            # Create attendance report
            message = f"📊 **Attendance Report - {self.get_today_key()}**\n\n"
            
            # Lists for tracking
            clocked_in = []
            clocked_out = []
            not_clocked_in = []
            not_clocked_out = []
            
            # Check administrators attendance
            for member in chat_members:
                user_id_str = str(member.id)
                user_name = member.first_name or member.username or 'Unknown'
                
                if user_id_str in today_attendance['clock_in']:
                    clocked_in.append(user_name)
                    if user_id_str in today_attendance['clock_out']:
                        clocked_out.append(user_name)
                    else:
                        not_clocked_out.append(f"@{member.username}" if member.username else user_name)
                else:
                    not_clocked_in.append(f"@{member.username}" if member.username else user_name)
            
            # Add people who clocked in but aren't admins (from our records)
            for user_id, data in today_attendance['clock_in'].items():
                if user_id not in [str(m.id) for m in chat_members]:
                    clocked_in.append(data['name'])
                    if user_id in today_attendance['clock_out']:
                        clocked_out.append(data['name'])
            
            # Build the message
            if clocked_in:
                message += f"✅ **Clocked In ({len(clocked_in)}):**\n"
                for name in clocked_in:
                    clock_time = None
                    for uid, data in today_attendance['clock_in'].items():
                        if data['name'] == name:
                            clock_time = data['time']
                            break
                    message += f"• {name}" + (f" - {clock_time}" if clock_time else "") + "\n"
                message += "\n"
            
            if clocked_out:
                message += f"🏁 **Clocked Out ({len(clocked_out)}):**\n"
                for name in clocked_out:
                    clock_time = None
                    for uid, data in today_attendance['clock_out'].items():
                        if data['name'] == name:
                            clock_time = data['time']
                            break
                    message += f"• {name}" + (f" - {clock_time}" if clock_time else "") + "\n"
                message += "\n"
            
            if not_clocked_in:
                message += f"❌ **Haven't Clocked In ({len(not_clocked_in)}):**\n"
                message += " ".join(not_clocked_in) + "\n"
                message += "👆 Please clock in!\n\n"
            
            if not_clocked_out:
                message += f"⏰ **Haven't Clocked Out ({len(not_clocked_out)}):**\n"
                message += " ".join(not_clocked_out) + "\n"
                message += "👆 Don't forget to clock out!\n\n"
            
            if not clocked_in and not not_clocked_out:
                message += "🎉 Everyone is up to date with their attendance!"
            
            # Add buttons for actions
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_attendance")],
                [InlineKeyboardButton("📈 Detailed Report", callback_data="detailed_report")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error in check_attendance: {e}")
            await update.message.reply_text(
                "❌ Error checking attendance. Make sure the bot has proper permissions."
            )
    
    async def detailed_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed attendance status"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("This command only works in groups!")
            return
        
        today_attendance = self.get_today_attendance(chat.id)
        
        message = f"📋 **Detailed Attendance Report**\n"
        message += f"📅 Date: {self.get_today_key()}\n\n"
        
        if today_attendance['clock_in']:
            message += "🕐 **Clock In Records:**\n"
            for user_id, data in today_attendance['clock_in'].items():
                message += f"• {data['name']} - {data['time']}\n"
            message += "\n"
        
        if today_attendance['clock_out']:
            message += "🕕 **Clock Out Records:**\n"
            for user_id, data in today_attendance['clock_out'].items():
                message += f"• {data['name']} - {data['time']}\n"
            message += "\n"
        
        if not today_attendance['clock_in'] and not today_attendance['clock_out']:
            message += "📝 No attendance records for today yet."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "refresh_attendance":
            # Simulate the check command
            await self.check_attendance(update, context)
        elif query.data == "detailed_report":
            await self.detailed_status(update, context)
    
    async def send_clock_in_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Send clock-in reminder message with button"""
        chat_id = context.job.chat_id
        
        keyboard = [
            [InlineKeyboardButton("🕐 Clock In", callback_data="clock_in_button")],
            [InlineKeyboardButton("📊 Check Status", callback_data="refresh_attendance")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "🌅 **Good Morning! Time to Clock In!** ⏰\n\n"
            "⏰ It's 08:00 - Don't forget to clock in for work!\n"
            "Click the button below or use /clockin command\n"
            "Have a productive day! 💪"
        )
        try:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            logger.info(f"Clock-in message sent to chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send clock-in message to {chat_id}: {e}")
    
    async def send_clock_out_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Send clock-out reminder message with button"""
        chat_id = context.job.chat_id
        
        keyboard = [
            [InlineKeyboardButton("🕕 Clock Out", callback_data="clock_out_button")],
            [InlineKeyboardButton("📊 Check Status", callback_data="refresh_attendance")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "🌆 **End of Work Day! Time to Clock Out!** ⏰\n\n"
            "⏰ It's 17:30 - Don't forget to clock out!\n"
            "Click the button below or use /clockout command\n"
            "Great work today! Time to relax! 🎉"
        )
        try:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            logger.info(f"Clock-out message sent to chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send clock-out message to {chat_id}: {e}")
    
    async def handle_clock_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle clock in/out button presses"""
        query = update.callback_query
        user = query.from_user
        chat = query.message.chat
        
        if query.data == "clock_in_button":
            today_attendance = self.get_today_attendance(chat.id)
            user_id_str = str(user.id)
            
            if user_id_str in today_attendance['clock_in']:
                await query.answer("You already clocked in today!", show_alert=True)
                return
            
            current_time = datetime.now(TIMEZONE)
            today_attendance['clock_in'][user_id_str] = {
                'name': user.first_name or user.username or 'Unknown',
                'username': user.username,
                'time': current_time.strftime("%H:%M:%S"),
                'timestamp': current_time.isoformat()
            }
            
            self.save_attendance_data()
            await query.answer(f"✅ Clocked in at {current_time.strftime('%H:%M:%S')}")
            
        elif query.data == "clock_out_button":
            today_attendance = self.get_today_attendance(chat.id)
            user_id_str = str(user.id)
            
            if user_id_str not in today_attendance['clock_in']:
                await query.answer("You need to clock in first!", show_alert=True)
                return
            
            if user_id_str in today_attendance['clock_out']:
                await query.answer("You already clocked out today!", show_alert=True)
                return
            
            current_time = datetime.now(TIMEZONE)
            today_attendance['clock_out'][user_id_str] = {
                'name': user.first_name or user.username or 'Unknown',
                'username': user.username,
                'time': current_time.strftime("%H:%M:%S"),
                'timestamp': current_time.isoformat()
            }
            
            self.save_attendance_data()
            await query.answer(f"✅ Clocked out at {current_time.strftime('%H:%M:%S')}")
    
    async def send_clock_in_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder for members who haven't clocked in"""
        chat_id = context.job.chat_id
        current_hour = datetime.now(TIMEZONE).hour
        
        # Only send reminders between 8:30 and 12:30
        if current_hour < 8 or current_hour > 12:
            return
        
        try:
            # Get all administrators
            chat_members = []
            async for member in context.bot.get_chat_administrators(chat_id):
                if not member.user.is_bot:
                    chat_members.append(member.user)
            
            today_attendance = self.get_today_attendance(chat_id)
            not_clocked_in = []
            
            # Check who hasn't clocked in
            for member in chat_members:
                user_id_str = str(member.id)
                if user_id_str not in today_attendance['clock_in']:
                    mention = f"@{member.username}" if member.username else member.first_name
                    not_clocked_in.append(mention)
            
            if not_clocked_in:
                current_time = datetime.now(TIMEZONE).strftime("%H:%M")
                message = (
                    f"⏰ **Clock In Reminder** - {current_time}\n\n"
                    f"❗ Anggota yang belum clock in:\n"
                    f"{' '.join(not_clocked_in)}\n\n"
                    f"Silakan gunakan /clockin atau klik tombol di pesan pagi hari!"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🕐 Clock In", callback_data="clock_in_button")],
                    [InlineKeyboardButton("📊 Check Status", callback_data="refresh_attendance")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                logger.info(f"Clock-in reminder sent to chat {chat_id}")
        
        except Exception as e:
            logger.error(f"Error sending clock-in reminder to {chat_id}: {e}")
    
    async def send_clock_out_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder for members who haven't clocked out"""
        chat_id = context.job.chat_id
        current_hour = datetime.now(TIMEZONE).hour
        
        # Only send reminders between 17:00 and 21:00
        if current_hour < 17 or current_hour > 21:
            return
        
        try:
            # Get all administrators
            chat_members = []
            async for member in context.bot.get_chat_administrators(chat_id):
                if not member.user.is_bot:
                    chat_members.append(member.user)
            
            today_attendance = self.get_today_attendance(chat_id)
            not_clocked_out = []
            
            # Check who has clocked in but not clocked out
            for member in chat_members:
                user_id_str = str(member.id)
                if (user_id_str in today_attendance['clock_in'] and 
                    user_id_str not in today_attendance['clock_out']):
                    mention = f"@{member.username}" if member.username else member.first_name
                    not_clocked_out.append(mention)
            
            if not_clocked_out:
                current_time = datetime.now(TIMEZONE).strftime("%H:%M")
                message = (
                    f"🌆 **Clock Out Reminder** - {current_time}\n\n"
                    f"❗ Anggota yang belum clock out:\n"
                    f"{' '.join(not_clocked_out)}\n\n"
                    f"Jangan lupa clock out! Gunakan /clockout atau klik tombol!"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🕕 Clock Out", callback_data="clock_out_button")],
                    [InlineKeyboardButton("📊 Check Status", callback_data="refresh_attendance")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                logger.info(f"Clock-out reminder sent to chat {chat_id}")
        
        except Exception as e:
            logger.error(f"Error sending clock-out reminder to {chat_id}: {e}")
    
    async def schedule_daily_messages(self, chat_id, context: ContextTypes.DEFAULT_TYPE):
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
        
        # Schedule clock-in message at 08:00 daily
        clock_in_time = time(hour=8, minute=0, tzinfo=TIMEZONE)
        job_queue.run_daily(
            self.send_clock_in_message,
            clock_in_time,
            chat_id=chat_id,
            name=f"clock_in_{chat_id}"
        )
        
        # Schedule clock-out message at 17:30 daily
        clock_out_time = time(hour=17, minute=30, tzinfo=TIMEZONE)
        job_queue.run_daily(
            self.send_clock_out_message,
            clock_out_time,
            chat_id=chat_id,
            name=f"clock_out_{chat_id}"
        )
        
        # Schedule hourly clock-in reminders from 08:30 to 12:30
        for hour in range(8, 13):  # 8:30, 9:30, 10:30, 11:30, 12:30
            if hour == 8:
                minute = 30  # First reminder at 8:30
            else:
                minute = 30  # Then every hour at :30
            
            reminder_time = time(hour=hour, minute=minute, tzinfo=TIMEZONE)
            job_queue.run_daily(
                self.send_clock_in_reminder,
                reminder_time,
                chat_id=chat_id,
                name=f"clock_in_reminder_{chat_id}_{hour}"
            )
        
        # Schedule hourly clock-out reminders from 17:00 to 21:00
        for hour in range(17, 22):  # 17:00, 18:00, 19:00, 20:00, 21:00
            reminder_time = time(hour=hour, minute=0, tzinfo=TIMEZONE)
            job_queue.run_daily(
                self.send_clock_out_reminder,
                reminder_time,
                chat_id=chat_id,
                name=f"clock_out_reminder_{chat_id}_{hour}"
            )
        
        logger.info(f"Scheduled daily messages and reminders for chat {chat_id}")
    
    async def handle_my_chat_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot being added to or removed from groups"""
        result = update.my_chat_member
        chat = result.chat
        new_status = result.new_chat_member.status
        old_status = result.old_chat_member.status
        
        if chat.type in ['group', 'supergroup']:
            if new_status == 'administrator' and old_status != 'administrator':
                # Bot was made admin
                await self.schedule_daily_messages(chat.id, context)
                
                # Send confirmation message
                welcome_message = (
                    "✅ **Clock Bot has been added as admin!**\n\n"
                    "🕐 I will now send daily reminders:\n"
                    "• Clock In: 08:00 every day\n"
                    "• Clock Out: 17:30 every day\n\n"
                    "**Available Commands:**\n"
                    "• /clockin - Manual clock in\n"
                    "• /clockout - Manual clock out\n"
                    "• /check - Check attendance (Admin only)\n"
                    "• /status - Detailed report\n"
                    "• /ping - Check if bot is active\n\n"
                    "Use /ping to check if I'm active!"
                )
                try:
                    await context.bot.send_message(chat_id=chat.id, text=welcome_message, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Failed to send welcome message to {chat.id}: {e}")
            
            elif old_status == 'administrator' and new_status != 'administrator':
                # Bot admin rights were removed
                job_queue = context.application.job_queue
                
                # Remove all scheduled jobs for this chat
                job_patterns = [
                    f"clock_in_{chat.id}",
                    f"clock_out_{chat.id}",
                    f"clock_in_reminder_{chat.id}",
                    f"clock_out_reminder_{chat.id}"
                ]
                
                for pattern in job_patterns:
                    current_jobs = job_queue.get_jobs_by_name(pattern)
                    for job in current_jobs:
                        job.schedule_removal()
                
                # Also remove numbered reminder jobs
                for hour in range(8, 22):
                    job_name = f"clock_in_reminder_{chat.id}_{hour}"
                    current_jobs = job_queue.get_jobs_by_name(job_name)
                    for job in current_jobs:
                        job.schedule_removal()
                    
                    job_name = f"clock_out_reminder_{chat.id}_{hour}"
                    current_jobs = job_queue.get_jobs_by_name(job_name)
                    for job in current_jobs:
                        job.schedule_removal()
                
                logger.info(f"Removed all scheduled jobs for chat {chat.id}")
    
    async def setup_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Setup command for manual scheduling (admin only)"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type in ['group', 'supergroup']:
            # Check if user is admin
            try:
                chat_member = await context.bot.get_chat_member(chat.id, user.id)
                if chat_member.status not in ['administrator', 'creator']:
                    await update.message.reply_text("⚠️ Only administrators can use this command.")
                    return
            except Exception:
                await update.message.reply_text("❌ Unable to verify admin status.")
                return
            
            # Check if bot is admin
            try:
                bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
                if bot_member.status != 'administrator':
                    await update.message.reply_text(
                        "⚠️ Please make me an administrator first to enable scheduled messages."
                    )
                    return
            except Exception:
                await update.message.reply_text("❌ Unable to check bot admin status.")
                return
            
            # Setup scheduling
            await self.schedule_daily_messages(chat.id, context)
            await update.message.reply_text(
                "✅ Daily clock reminders have been set up!\n"
                "• Clock In: 08:00\n"
                "• Clock Out: 17:30"
            )
        else:
            await update.message.reply_text("This command only works in groups!")
    
    def run(self):
        """Run the bot"""
        # Create application
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("ping", self.ping))
        self.application.add_handler(CommandHandler("setup", self.setup_commands))
        self.application.add_handler(CommandHandler("clockin", self.manual_clock_in))
        self.application.add_handler(CommandHandler("clockout", self.manual_clock_out))
        self.application.add_handler(CommandHandler("check", self.check_attendance))
        self.application.add_handler(CommandHandler("status", self.detailed_status))
        
        # Add callback handlers for buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback, pattern="^(refresh_attendance|detailed_report)$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_clock_buttons, pattern="^(clock_in_button|clock_out_button)$"))
        
        # Handle chat member updates (when bot is added/removed as admin)
        from telegram.ext import ChatMemberHandler
        self.application.add_handler(
            ChatMemberHandler(self.handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER)
        )
        
        # Run the bot
        print("🤖 Clock Bot is starting...")
        print("Make sure to:")
        print("1. Replace BOT_TOKEN with your actual bot token")
        print("2. Adjust TIMEZONE if needed")
        print("3. Add the bot to your group as an administrator")
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = ClockBot()
    bot.run()