import logging
from telegram import Update
from telegram.ext import ContextTypes, ChatMemberHandler
from telegram.constants import ParseMode

from src.database.database import Database
from src.config.settings import Settings
from src.handlers.scheduled_handlers import ScheduledHandlers

logger = logging.getLogger(__name__)

class ChatHandlers:
    def __init__(self, database: Database, scheduled_handlers: ScheduledHandlers):
        self.db = database
        self.scheduled_handlers = scheduled_handlers
    
    async def handle_my_chat_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot being added to or removed from groups"""
        result = update.my_chat_member
        chat = result.chat
        new_status = result.new_chat_member.status
        old_status = result.old_chat_member.status
        
        if chat.type in ['group', 'supergroup']:
            if new_status == 'administrator' and old_status != 'administrator':
                # Bot was made admin
                await self._handle_bot_added_as_admin(chat, context)
            elif old_status == 'administrator' and new_status != 'administrator':
                # Bot admin rights were removed
                await self._handle_bot_removed_as_admin(chat, context)
    
    async def _handle_bot_added_as_admin(self, chat, context: ContextTypes.DEFAULT_TYPE):
        """Handle when bot is added as admin"""
        try:
            # Add chat group to database
            self.db.add_chat_group(chat.id, chat.title, chat.type)
            
            # Set up default configurations if none exist
            clock_in_config = self.db.get_configuration(chat.id, 'clock_in')
            clock_out_config = self.db.get_configuration(chat.id, 'clock_out')
            
            if not clock_in_config:
                # Set default clock in configuration
                self.db.save_configuration(
                    chat_id=chat.id,
                    config_type='clock_in',
                    start_time=Settings.DEFAULT_CLOCK_IN_START,
                    end_time=Settings.DEFAULT_CLOCK_IN_END,
                    reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                    enabled_days=Settings.DEFAULT_ENABLED_DAYS
                )
            
            if not clock_out_config:
                # Set default clock out configuration
                self.db.save_configuration(
                    chat_id=chat.id,
                    config_type='clock_out',
                    start_time=Settings.DEFAULT_CLOCK_OUT_START,
                    end_time=Settings.DEFAULT_CLOCK_OUT_END,
                    reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                    enabled_days=Settings.DEFAULT_ENABLED_DAYS
                )
            
            # Schedule daily messages and reminders
            self.scheduled_handlers.schedule_daily_messages(chat.id, context)
            
            # Send welcome message
            welcome_message = (
                "✅ **Attendance Bot telah ditambahkan sebagai admin!**\n\n"
                "🕐 Saya akan mengirim pengingat harian:\n"
                f"• Clock In: {Settings.DEFAULT_CLOCK_IN_START} setiap hari kerja\n"
                f"• Clock Out: {Settings.DEFAULT_CLOCK_OUT_START} setiap hari kerja\n\n"
                "**Perintah yang Tersedia:**\n"
                "• /clockin - Clock in manual\n"
                "• /clockout - Clock out manual\n"
                "• /check - Cek kehadiran (Admin only)\n"
                "• /status - Laporan detail\n"
                "• /config - Konfigurasi pengaturan\n"
                "• /ping - Cek status bot\n\n"
                "💡 **Tips:** Gunakan /config untuk mengatur waktu dan interval pengingat!"
            )
            
            try:
                await context.bot.send_message(
                    chat_id=chat.id, 
                    text=welcome_message, 
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Welcome message sent to chat {chat.id}")
            except Exception as e:
                logger.error(f"Failed to send welcome message to {chat.id}: {e}")
            
        except Exception as e:
            logger.error(f"Error handling bot added as admin for chat {chat.id}: {e}")
    
    async def _handle_bot_removed_as_admin(self, chat, context: ContextTypes.DEFAULT_TYPE):
        """Handle when bot admin rights are removed"""
        try:
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
            
        except Exception as e:
            logger.error(f"Error handling bot removed as admin for chat {chat.id}: {e}")
    
    async def setup_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Setup command for manual scheduling (admin only)"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type in ['group', 'supergroup']:
            # Check if user is admin
            try:
                chat_member = await context.bot.get_chat_member(chat.id, user.id)
                if chat_member.status not in ['administrator', 'creator']:
                    await update.message.reply_text("⚠️ Hanya administrator yang dapat menggunakan perintah ini.")
                    return
            except Exception:
                await update.message.reply_text("❌ Tidak dapat memverifikasi status admin.")
                return
            
            # Check if bot is admin
            try:
                bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
                if bot_member.status != 'administrator':
                    await update.message.reply_text(
                        "⚠️ Silakan jadikan saya sebagai administrator terlebih dahulu untuk mengaktifkan pesan terjadwal."
                    )
                    return
            except Exception:
                await update.message.reply_text("❌ Tidak dapat memeriksa status admin bot.")
                return
            
            # Add chat group to database
            try:
                self.db.add_chat_group(chat.id, chat.title, chat.type)
                logger.info(f"Chat group {chat.id} ({chat.title}) added to database via /setup")
            except Exception as e:
                logger.error(f"Error adding chat group to database: {e}")
                await update.message.reply_text("❌ Gagal mendaftarkan grup ke database.")
                return
            
            # Set up default configurations if none exist
            clock_in_config = self.db.get_configuration(chat.id, 'clock_in')
            clock_out_config = self.db.get_configuration(chat.id, 'clock_out')
            
            if not clock_in_config:
                # Set default clock in configuration
                success = self.db.save_configuration(
                    chat_id=chat.id,
                    config_type='clock_in',
                    start_time=Settings.DEFAULT_CLOCK_IN_START,
                    end_time=Settings.DEFAULT_CLOCK_IN_END,
                    reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                    enabled_days=Settings.DEFAULT_ENABLED_DAYS
                )
                if success:
                    logger.info(f"Default clock_in config created for chat {chat.id}")
                else:
                    logger.error(f"Failed to create default clock_in config for chat {chat.id}")
            
            if not clock_out_config:
                # Set default clock out configuration
                success = self.db.save_configuration(
                    chat_id=chat.id,
                    config_type='clock_out',
                    start_time=Settings.DEFAULT_CLOCK_OUT_START,
                    end_time=Settings.DEFAULT_CLOCK_OUT_END,
                    reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                    enabled_days=Settings.DEFAULT_ENABLED_DAYS
                )
                if success:
                    logger.info(f"Default clock_out config created for chat {chat.id}")
                else:
                    logger.error(f"Failed to create default clock_out config for chat {chat.id}")
            
            # Setup scheduling
            self.scheduled_handlers.schedule_daily_messages(chat.id, context)
            
            # Get current configurations (refresh after creating defaults)
            clock_in_config = self.db.get_configuration(chat.id, 'clock_in')
            clock_out_config = self.db.get_configuration(chat.id, 'clock_out')
            
            message = "✅ **Setup berhasil!** Pengingat clock harian telah diatur.\n\n"
            message += f"📝 **Grup:** {chat.title}\n"
            message += f"🆔 **Chat ID:** {chat.id}\n\n"
            
            if clock_in_config:
                message += f"🟢 **Clock In:** {clock_in_config['start_time']} - {clock_in_config['end_time']}\n"
            else:
                message += f"🟢 **Clock In:** {Settings.DEFAULT_CLOCK_IN_START} - {Settings.DEFAULT_CLOCK_IN_END}\n"
            
            if clock_out_config:
                message += f"🔴 **Clock Out:** {clock_out_config['start_time']} - {clock_out_config['end_time']}\n"
            else:
                message += f"🔴 **Clock Out:** {Settings.DEFAULT_CLOCK_OUT_START} - {Settings.DEFAULT_CLOCK_OUT_END}\n"
            
            message += "\n💡 Gunakan /config untuk mengatur pengaturan lebih lanjut!"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("Perintah ini hanya berfungsi di grup!") 