#!/usr/bin/env python3
"""
Attendance Bot - Telegram Bot for managing group attendance
"""

import logging
import asyncio
import os
from datetime import datetime, timedelta

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ChatMemberHandler

from src.database.database import Database
from src.config.settings import Settings
from src.handlers.command_handlers import CommandHandlers
from src.handlers.callback_handlers import CallbackHandlers
from src.handlers.message_handlers import MessageHandlers
from src.handlers.scheduled_handlers import ScheduledHandlers
from src.handlers.chat_handlers import ChatHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AttendanceBot:
    def __init__(self):
        """Initialize the bot with all components"""
        self.bot_token = Settings.BOT_TOKEN
        self.database = Database(Settings.DATABASE_PATH)

        # Initialize handlers
        self.command_handlers = CommandHandlers(self.database)
        self.scheduled_handlers = ScheduledHandlers(self.database)
        self.callback_handlers = CallbackHandlers(self.database, self.scheduled_handlers)
        self.chat_handlers = ChatHandlers(self.database, self.scheduled_handlers)
        self.message_handlers = MessageHandlers(self.database, self.callback_handlers, self.scheduled_handlers)

        # Initialize application with startup and shutdown handlers
        self.application = Application.builder().token(self.bot_token).post_init(self.on_startup).post_shutdown(self.on_shutdown).build()

        # Setup handlers
        self.setup_handlers()

        # Setup scheduled jobs
        self.setup_scheduled_jobs()

    def setup_handlers(self):
        """Setup all command and message handlers"""

        # Command handlers
        self.application.add_handler(CommandHandler("start", self.command_handlers.start_command))
        self.application.add_handler(CommandHandler("ping", self.command_handlers.ping_command))
        self.application.add_handler(CommandHandler("clockin", self.command_handlers.clockin_command))
        self.application.add_handler(CommandHandler("clockout", self.command_handlers.clockout_command))
        self.application.add_handler(CommandHandler("check", self.command_handlers.check_command))
        self.application.add_handler(CommandHandler("status", self.command_handlers.status_command))
        self.application.add_handler(CommandHandler("config", self.command_handlers.config_command))
        self.application.add_handler(CommandHandler("help", self.command_handlers.help_command))
        self.application.add_handler(CommandHandler("setup", self.chat_handlers.setup_commands))
        self.application.add_handler(CommandHandler("trigger_clockin", self.command_handlers.trigger_clockin_command))
        self.application.add_handler(CommandHandler("trigger_clockout", self.command_handlers.trigger_clockout_command))

        # Callback query handlers - specific patterns first (most specific to least specific)
        self.application.add_handler(CallbackQueryHandler(
            self.scheduled_handlers.handle_clock_buttons, 
            pattern="^(clock_in_button|clock_out_button)$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.scheduled_handlers.handle_refresh_attendance, 
            pattern="^refresh_attendance$"
        ))

        # Configuration callbacks - specific patterns
        self.application.add_handler(CallbackQueryHandler(
            self.callback_handlers.handle_day_callback_wrapper,
            pattern="^day_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.callback_handlers.handle_save_callback_wrapper,
            pattern="^save_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.callback_handlers.handle_cancel_callback_wrapper,
            pattern="^cancel_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.callback_handlers.handle_set_callback_wrapper,
            pattern="^set_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.callback_handlers.handle_config_callback_wrapper,
            pattern="^config_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.callback_handlers.handle_view_callback_wrapper,
            pattern="^view_"
        ))

        # Message handler for text input
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handlers.handle_text_message))

        # Chat member handler (when bot is added/removed as admin)
        self.application.add_handler(
            ChatMemberHandler(self.chat_handlers.handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER)
        )

        # Error handler
        self.application.add_error_handler(self.error_handler)

    def setup_scheduled_jobs(self):
        """Setup scheduled jobs for reminders"""
        job_queue = self.application.job_queue

        # Check for active configurations and schedule reminders
        self.schedule_reminders_from_config()

        # Schedule a job to refresh configurations every hour
        job_queue.run_repeating(
            self.refresh_configurations_job,
            interval=timedelta(hours=1),
            first=datetime.now() + timedelta(minutes=5)
        )

    async def refresh_configurations_job(self, context):
        """Job to refresh configurations and reschedule reminders"""
        try:
            logger.info("Refreshing configurations and rescheduling reminders")
            self.schedule_reminders_from_config()
        except Exception as e:
            logger.error(f"Error refreshing configurations: {e}")

    def schedule_reminders_from_config(self):
        """Schedule reminders based on active configurations"""
        job_queue = self.application.job_queue

        # Get all active configurations
        configurations = self.database.get_all_active_configurations()

        # Group configurations by chat_id to avoid duplicate scheduling
        chat_configs = {}
        for config in configurations:
            chat_id = config['chat_id']
            if chat_id not in chat_configs:
                chat_configs[chat_id] = []
            chat_configs[chat_id].append(config)

        # Remove all existing reminder jobs
        for job in job_queue.jobs():
            if job.name and ('clock_in_reminder' in job.name or 'clock_out_reminder' in job.name or 
                            'clock_in_' in job.name or 'clock_out_' in job.name):
                job.schedule_removal()

        # Schedule new jobs based on configurations, grouped by chat
        scheduled_chats = 0
        for chat_id, configs in chat_configs.items():
            # Schedule all reminders for this chat
            self.scheduled_handlers.schedule_daily_messages(chat_id, self.application)
            scheduled_chats += 1

        logger.info(f"Scheduled reminders for {scheduled_chats} chats with {len(configurations)} configurations")

    async def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")

        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi kesalahan. Silakan coba lagi nanti."
            )

    async def on_startup(self, application):
        """Called when the bot starts up"""
        logger.info("Bot started successfully!")

        # Set bot commands
        await application.bot.set_my_commands([
            ("start", "Mulai bot"),
            ("ping", "Cek status bot"),
            ("clockin", "Clock in manual"),
            ("clockout", "Clock out manual"),
            ("check", "Cek kehadiran hari ini"),
            ("status", "Laporan kehadiran detail"),
            ("config", "Konfigurasi clock in/out"),
            ("setup", "Setup pengingat otomatis"),
            ("trigger_clockin", "Kirim pengingat clock in manual"),
            ("trigger_clockout", "Kirim pengingat clock out manual"),
            ("help", "Bantuan penggunaan")
        ])

    async def on_shutdown(self, application):
        """Called when the bot shuts down"""
        logger.info("Bot shutting down...")

    def run(self):
        """Run the bot"""
        try:
            # Start the bot
            logger.info("Starting Attendance Bot...")
            self.application.run_polling(
                allowed_updates=["message", "callback_query", "my_chat_member"],
                drop_pending_updates=True
            )

        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise

def main():
    """Main function to run the bot"""
    try:
        # Validate bot token
        try:
            Settings.validate_bot_token()
        except ValueError as e:
            logger.error(f"Bot token validation failed: {e}")
            return

        # Create and run bot
        bot = AttendanceBot()

        # Run the bot
        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main() 
