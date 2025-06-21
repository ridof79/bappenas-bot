import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.database.database import Database
from src.config.settings import Settings
from src.utils.helpers import (
    get_current_time, format_attendance_report, 
    format_configuration_display, get_enabled_days_display
)

logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self, database: Database):
        self.db = database
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "👋 **Selamat datang di Attendance Bot!**\n\n"
            "🤖 Saya adalah bot untuk mengelola kehadiran anggota grup.\n\n"
            "📋 **Fitur Utama:**\n"
            "• ⏰ Clock in/out otomatis dengan pengingat\n"
            "• 📊 Laporan kehadiran harian\n"
            "• ⚙️ Konfigurasi waktu yang fleksibel\n"
            "• 📅 Pengaturan hari kerja\n\n"
            "🔧 **Perintah yang tersedia:**\n"
            "• /ping - Cek status bot\n"
            "• /clockin - Clock in manual\n"
            "• /clockout - Clock out manual\n"
            "• /check - Cek kehadiran hari ini\n"
            "• /status - Laporan kehadiran detail\n"
            "• /config - Konfigurasi clock in/out\n"
            "• /help - Bantuan penggunaan\n\n"
            "💡 **Tips:** Tambahkan saya sebagai admin grup untuk fitur lengkap!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ping command"""
        current_time = get_current_time().strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(
            f"🟢 **Bot aktif!**\n"
            f"⏰ Waktu sekarang: {current_time} (WIB)\n"
            f"💾 Database: Terhubung"
        )
    
    async def clockin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clockin command"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ Perintah ini hanya berfungsi di grup!")
            return
        
        current_time = get_current_time()
        today_attendance = self.db.get_today_attendance(chat.id, current_time)
        
        # Check if already clocked in today
        if str(user.id) in today_attendance.get('clock_in', {}):
            clock_in_time = today_attendance['clock_in'][str(user.id)]['time']
            await update.message.reply_text(
                f"⚠️ {user.first_name}, Anda sudah clock in hari ini pada {clock_in_time}"
            )
            return
        
        # Record clock in
        success = self.db.record_attendance(
            chat_id=chat.id,
            user_id=user.id,
            user_name=user.first_name or user.username or 'Unknown',
            username=user.username,
            clock_type='in',
            clock_time=current_time
        )
        
        if success:
            await update.message.reply_text(
                f"✅ **{user.first_name}** berhasil clock in pada {current_time.strftime('%H:%M:%S')}"
            )
        else:
            await update.message.reply_text("❌ Gagal mencatat clock in. Silakan coba lagi.")
    
    async def clockout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clockout command"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ Perintah ini hanya berfungsi di grup!")
            return
        
        current_time = get_current_time()
        today_attendance = self.db.get_today_attendance(chat.id, current_time)
        
        # Check if already clocked in
        if str(user.id) not in today_attendance.get('clock_in', {}):
            await update.message.reply_text(
                f"⚠️ {user.first_name}, Anda harus clock in terlebih dahulu!"
            )
            return
        
        # Check if already clocked out
        if str(user.id) in today_attendance.get('clock_out', {}):
            clock_out_time = today_attendance['clock_out'][str(user.id)]['time']
            await update.message.reply_text(
                f"⚠️ {user.first_name}, Anda sudah clock out hari ini pada {clock_out_time}"
            )
            return
        
        # Record clock out
        success = self.db.record_attendance(
            chat_id=chat.id,
            user_id=user.id,
            user_name=user.first_name or user.username or 'Unknown',
            username=user.username,
            clock_type='out',
            clock_time=current_time
        )
        
        if success:
            await update.message.reply_text(
                f"✅ **{user.first_name}** berhasil clock out pada {current_time.strftime('%H:%M:%S')}"
            )
        else:
            await update.message.reply_text("❌ Gagal mencatat clock out. Silakan coba lagi.")
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ Perintah ini hanya berfungsi di grup!")
            return
        
        current_time = get_current_time()
        today_attendance = self.db.get_today_attendance(chat.id, current_time)
        
        clock_in_count = len(today_attendance.get('clock_in', {}))
        clock_out_count = len(today_attendance.get('clock_out', {}))
        
        await update.message.reply_text(
            f"📊 **Status Kehadiran Hari Ini**\n\n"
            f"🟢 **Clock In:** {clock_in_count} orang\n"
            f"🔴 **Clock Out:** {clock_out_count} orang\n"
            f"📅 Tanggal: {current_time.strftime('%d/%m/%Y')}\n"
            f"⏰ Waktu: {current_time.strftime('%H:%M:%S')}"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ Perintah ini hanya berfungsi di grup!")
            return
        
        # Check if user is admin
        user = update.effective_user
        try:
            chat_member = await context.bot.get_chat_member(chat.id, user.id)
            if chat_member.status not in ['administrator', 'creator']:
                await update.message.reply_text("⚠️ Hanya administrator yang dapat menggunakan perintah ini.")
                return
        except Exception:
            await update.message.reply_text("❌ Tidak dapat memverifikasi status admin.")
            return
        
        current_time = get_current_time()
        today_attendance = self.db.get_today_attendance(chat.id, current_time)
        
        report = format_attendance_report(today_attendance, current_time)
        await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)
    
    async def config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /config command"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ Perintah ini hanya berfungsi di grup!")
            return
        
        # Check if user is admin
        user = update.effective_user
        try:
            chat_member = await context.bot.get_chat_member(chat.id, user.id)
            if chat_member.status not in ['administrator', 'creator']:
                await update.message.reply_text("⚠️ Hanya administrator yang dapat menggunakan perintah ini.")
                return
        except Exception:
            await update.message.reply_text("❌ Tidak dapat memverifikasi status admin.")
            return
        
        # Get current configurations
        clock_in_config = self.db.get_configuration(chat.id, 'clock_in')
        clock_out_config = self.db.get_configuration(chat.id, 'clock_out')
        
        keyboard = [
            [
                InlineKeyboardButton("⚙️ Konfigurasi Clock In", callback_data="config_clock_in"),
                InlineKeyboardButton("⚙️ Konfigurasi Clock Out", callback_data="config_clock_out")
            ],
            [
                InlineKeyboardButton("📊 Lihat Konfigurasi", callback_data="view_config")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "⚙️ **Menu Konfigurasi**\n\n"
        message += "Pilih opsi di bawah ini untuk mengatur konfigurasi clock in/out:"
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **Bantuan Penggunaan Bot**

**Commands:**
/start - Mulai bot
/ping - Cek status bot
/clockin - Clock in manual
/clockout - Clock out manual
/check - Cek kehadiran hari ini
/status - Laporan kehadiran detail
/config - Konfigurasi clock in/out
/setup - Setup pengingat otomatis
/trigger_clockin - Kirim pengingat clock in manual
/trigger_clockout - Kirim pengingat clock out manual
/help - Bantuan penggunaan

**Fitur:**
• Pengingat otomatis clock in/out
• Konfigurasi waktu dan interval
• Laporan kehadiran real-time
• Tombol cepat untuk clock in/out
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def trigger_clockin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trigger_clockin command - manual trigger for clock in reminder"""
        chat = update.effective_chat
        user = update.effective_user
        
        # Check if user is admin
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Hanya admin yang dapat menggunakan command ini.")
            return
        
        try:
            current_time = get_current_time()
            
            # Get configuration
            config = self.db.get_configuration(chat.id, 'clock_in')
            if not config:
                await update.message.reply_text("❌ Konfigurasi clock in belum diatur. Gunakan /config untuk mengatur.")
                return
            
            # Get today's attendance
            today_attendance = self.db.get_today_attendance(chat.id, current_time)
            clock_in_count = len(today_attendance.get('clock_in', {}))
            
            # Create reminder message
            message = (
                f"⏰ **Pengingat Clock In Manual** - {current_time.strftime('%H:%M')}\n\n"
                f"Admin {user.first_name} mengirim pengingat clock in.\n\n"
            )
            
            if clock_in_count == 0:
                message += "Belum ada yang clock in hari ini!\n\n"
            else:
                message += f"Sudah ada {clock_in_count} orang yang clock in.\n\n"
            
            message += "Silakan gunakan /clockin untuk mencatat kehadiran."
            
            keyboard = [
                [InlineKeyboardButton("🕐 Clock In", callback_data="clock_in_button")],
                [InlineKeyboardButton("📊 Cek Status", callback_data="refresh_attendance")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            logger.info(f"Manual clock-in reminder triggered by {user.first_name} in chat {chat.id}")
            
        except Exception as e:
            logger.error(f"Error in trigger_clockin_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengirim pengingat.")
    
    async def trigger_clockout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trigger_clockout command - manual trigger for clock out reminder"""
        chat = update.effective_chat
        user = update.effective_user
        
        # Check if user is admin
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Hanya admin yang dapat menggunakan command ini.")
            return
        
        try:
            current_time = get_current_time()
            
            # Get configuration
            config = self.db.get_configuration(chat.id, 'clock_out')
            if not config:
                await update.message.reply_text("❌ Konfigurasi clock out belum diatur. Gunakan /config untuk mengatur.")
                return
            
            # Get today's attendance
            today_attendance = self.db.get_today_attendance(chat.id, current_time)
            clock_in_count = len(today_attendance.get('clock_in', {}))
            clock_out_count = len(today_attendance.get('clock_out', {}))
            
            # Create reminder message
            message = (
                f"🌆 **Pengingat Clock Out Manual** - {current_time.strftime('%H:%M')}\n\n"
                f"Admin {user.first_name} mengirim pengingat clock out.\n\n"
                f"🟢 Clock In: {clock_in_count} orang\n"
                f"🔴 Clock Out: {clock_out_count} orang\n\n"
                f"Jangan lupa clock out sebelum pulang!"
            )
            
            keyboard = [
                [InlineKeyboardButton("🕕 Clock Out", callback_data="clock_out_button")],
                [InlineKeyboardButton("📊 Cek Status", callback_data="refresh_attendance")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            logger.info(f"Manual clock-out reminder triggered by {user.first_name} in chat {chat.id}")
            
        except Exception as e:
            logger.error(f"Error in trigger_clockout_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengirim pengingat.")
    
    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is admin in the chat"""
        try:
            chat = update.effective_chat
            user = update.effective_user
            
            # Check if context.bot exists
            if not context or not context.bot:
                logger.warning("Context or bot is None, cannot verify admin status")
                return False
            
            # Get chat member info
            chat_member = await context.bot.get_chat_member(chat.id, user.id)
            
            # Check if user is admin or creator
            return chat_member.status in ['administrator', 'creator']
            
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False 