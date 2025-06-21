import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.database.database import Database
from src.config.settings import Settings
from src.utils.helpers import (
    get_current_time, format_configuration_display, 
    validate_configuration, get_enabled_days_display
)

logger = logging.getLogger(__name__)

class CallbackHandlers:
    def __init__(self, database: Database):
        self.db = database
        self.config_states = {}  # Store configuration state for each user
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("config_"):
            await self.handle_config_callback(update, context, data)
        elif data.startswith("view_"):
            await self.handle_view_callback(update, context, data)
        elif data.startswith("set_"):
            await self.handle_set_callback(update, context, data)
        elif data.startswith("day_"):
            await self.handle_day_callback(update, context, data)
        elif data.startswith("save_"):
            await self.handle_save_callback(update, context, data)
        elif data.startswith("cancel_"):
            await self.handle_cancel_callback(update, context, data)
    
    async def handle_config_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle configuration menu callbacks"""
        query = update.callback_query
        user_id = query.from_user.id
        chat_id = query.message.chat.id
        
        if data == "config_clock_in":
            await self.show_clock_in_config(update, context)
        elif data == "config_clock_out":
            await self.show_clock_out_config(update, context)
        elif data == "view_config":
            await self.show_current_config(update, context)
    
    async def handle_view_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle view callbacks"""
        if data == "view_config":
            await self.show_current_config(update, context)
    
    async def show_clock_in_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show clock in configuration menu"""
        query = update.callback_query
        chat_id = query.message.chat.id
        
        # Get current configuration
        current_config = self.db.get_configuration(chat_id, 'clock_in')
        
        if current_config:
            start_time = current_config['start_time']
            end_time = current_config['end_time']
            interval = current_config['reminder_interval']
            enabled_days = current_config['enabled_days']
        else:
            start_time = Settings.DEFAULT_CLOCK_IN_START
            end_time = Settings.DEFAULT_CLOCK_IN_END
            interval = Settings.DEFAULT_REMINDER_INTERVAL
            enabled_days = Settings.DEFAULT_ENABLED_DAYS
        
        keyboard = [
            [
                InlineKeyboardButton(f"🕐 Waktu: {start_time} - {end_time}", callback_data="set_clock_in_time")
            ],
            [
                InlineKeyboardButton(f"⏰ Interval: {interval} menit", callback_data="set_clock_in_interval")
            ],
            [
                InlineKeyboardButton(f"📅 Hari: {get_enabled_days_display(enabled_days)}", callback_data="set_clock_in_days")
            ],
            [
                InlineKeyboardButton("💾 Simpan", callback_data="save_clock_in"),
                InlineKeyboardButton("❌ Batal", callback_data="cancel_config")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "⚙️ **Konfigurasi Clock In**\n\n"
        message += "Atur pengaturan untuk clock in otomatis:"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def show_clock_out_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show clock out configuration menu"""
        query = update.callback_query
        chat_id = query.message.chat.id
        
        # Get current configuration
        current_config = self.db.get_configuration(chat_id, 'clock_out')
        
        if current_config:
            start_time = current_config['start_time']
            end_time = current_config['end_time']
            interval = current_config['reminder_interval']
            enabled_days = current_config['enabled_days']
        else:
            start_time = Settings.DEFAULT_CLOCK_OUT_START
            end_time = Settings.DEFAULT_CLOCK_OUT_END
            interval = Settings.DEFAULT_REMINDER_INTERVAL
            enabled_days = Settings.DEFAULT_ENABLED_DAYS
        
        keyboard = [
            [
                InlineKeyboardButton(f"🕐 Waktu: {start_time} - {end_time}", callback_data="set_clock_out_time")
            ],
            [
                InlineKeyboardButton(f"⏰ Interval: {interval} menit", callback_data="set_clock_out_interval")
            ],
            [
                InlineKeyboardButton(f"📅 Hari: {get_enabled_days_display(enabled_days)}", callback_data="set_clock_out_days")
            ],
            [
                InlineKeyboardButton("💾 Simpan", callback_data="save_clock_out"),
                InlineKeyboardButton("❌ Batal", callback_data="cancel_config")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "⚙️ **Konfigurasi Clock Out**\n\n"
        message += "Atur pengaturan untuk clock out otomatis:"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def show_current_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current configuration"""
        query = update.callback_query
        chat_id = query.message.chat.id
        
        clock_in_config = self.db.get_configuration(chat_id, 'clock_in')
        clock_out_config = self.db.get_configuration(chat_id, 'clock_out')
        
        message = "📊 **Konfigurasi Saat Ini**\n\n"
        
        if clock_in_config:
            message += format_configuration_display(clock_in_config)
        else:
            message += "🟢 **Clock In:** Belum dikonfigurasi\n\n"
        
        if clock_out_config:
            message += format_configuration_display(clock_out_config)
        else:
            message += "🔴 **Clock Out:** Belum dikonfigurasi\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="config_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_set_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle set configuration callbacks"""
        query = update.callback_query
        
        if data == "set_clock_in_time":
            await self.show_time_setup(update, context, "clock_in")
        elif data == "set_clock_out_time":
            await self.show_time_setup(update, context, "clock_out")
        elif data == "set_clock_in_interval":
            await self.show_interval_setup(update, context, "clock_in")
        elif data == "set_clock_out_interval":
            await self.show_interval_setup(update, context, "clock_out")
        elif data == "set_clock_in_days":
            await self.show_days_setup(update, context, "clock_in")
        elif data == "set_clock_out_days":
            await self.show_days_setup(update, context, "clock_out")
    
    async def show_time_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, config_type: str):
        """Show time setup interface"""
        query = update.callback_query
        
        message = f"🕐 **Atur Waktu {Settings.get_clock_type_name(config_type)}**\n\n"
        message += "Kirim waktu dalam format HH:MM\n"
        message += "Contoh: 08:00 untuk jam 8 pagi\n\n"
        message += "Format: START_TIME-END_TIME\n"
        message += "Contoh: 08:00-09:00"
        
        # Store state for this user
        user_id = query.from_user.id
        self.config_states[user_id] = {
            'type': 'time',
            'config_type': config_type,
            'chat_id': query.message.chat.id
        }
        
        keyboard = [
            [InlineKeyboardButton("❌ Batal", callback_data="cancel_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def show_interval_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, config_type: str):
        """Show interval setup interface"""
        query = update.callback_query
        
        message = f"⏰ **Atur Interval Pengingat {Settings.get_clock_type_name(config_type)}**\n\n"
        message += "Kirim interval dalam menit (1-1440)\n"
        message += "Contoh: 15 untuk setiap 15 menit"
        
        # Store state for this user
        user_id = query.from_user.id
        self.config_states[user_id] = {
            'type': 'interval',
            'config_type': config_type,
            'chat_id': query.message.chat.id
        }
        
        keyboard = [
            [InlineKeyboardButton("❌ Batal", callback_data="cancel_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def show_days_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, config_type: str):
        """Show days setup interface"""
        query = update.callback_query
        
        # Get current configuration
        chat_id = query.message.chat.id
        current_config = self.db.get_configuration(chat_id, config_type)
        enabled_days = current_config['enabled_days'] if current_config else Settings.DEFAULT_ENABLED_DAYS
        
        keyboard = []
        for day_num in range(7):
            day_name = Settings.get_day_name(day_num)
            is_enabled = day_num in enabled_days
            button_text = f"{'✅' if is_enabled else '❌'} {day_name}"
            callback_data = f"day_{config_type}_{day_num}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        keyboard.append([
            InlineKeyboardButton("💾 Simpan", callback_data=f"save_{config_type}"),
            InlineKeyboardButton("❌ Batal", callback_data="cancel_config")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"📅 **Atur Hari Aktif {Settings.get_clock_type_name(config_type)}**\n\n"
        message += "Pilih hari yang aktif untuk pengingat otomatis:"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_day_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle day selection callbacks"""
        query = update.callback_query
        parts = data.split('_')
        config_type = parts[1]
        day_num = int(parts[2])
        chat_id = query.message.chat.id
        
        # Get current configuration
        current_config = self.db.get_configuration(chat_id, config_type)
        enabled_days = current_config['enabled_days'] if current_config else Settings.DEFAULT_ENABLED_DAYS.copy()
        
        # Toggle day
        if day_num in enabled_days:
            enabled_days.remove(day_num)
        else:
            enabled_days.append(day_num)
        
        # Update configuration
        if current_config:
            start_time = current_config['start_time']
            end_time = current_config['end_time']
            interval = current_config['reminder_interval']
        else:
            if config_type == 'clock_in':
                start_time = Settings.DEFAULT_CLOCK_IN_START
                end_time = Settings.DEFAULT_CLOCK_IN_END
            else:
                start_time = Settings.DEFAULT_CLOCK_OUT_START
                end_time = Settings.DEFAULT_CLOCK_OUT_END
            interval = Settings.DEFAULT_REMINDER_INTERVAL
        
        # Save configuration
        success = self.db.save_configuration(chat_id, config_type, start_time, end_time, interval, enabled_days)
        
        if success:
            await query.answer(f"Hari {Settings.get_day_name(day_num)} {'diaktifkan' if day_num in enabled_days else 'dinonaktifkan'}")
            # Refresh the days setup interface
            await self.show_days_setup(update, context, config_type)
        else:
            await query.answer("❌ Gagal menyimpan konfigurasi")
    
    async def handle_save_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle save configuration callbacks"""
        query = update.callback_query
        parts = data.split('_')
        config_type = parts[1]
        chat_id = query.message.chat.id
        
        # Get current configuration
        current_config = self.db.get_configuration(chat_id, config_type)
        
        if current_config:
            await query.answer("✅ Konfigurasi berhasil disimpan!")
            await self.show_current_config(update, context)
        else:
            await query.answer("❌ Tidak ada konfigurasi untuk disimpan")
    
    async def handle_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle cancel callbacks"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Clear user state
        if user_id in self.config_states:
            del self.config_states[user_id]
        
        await query.answer("❌ Dibatalkan")
        await self.show_current_config(update, context)
    
    def get_user_state(self, user_id: int):
        """Get user configuration state"""
        return self.config_states.get(user_id)
    
    def clear_user_state(self, user_id: int):
        """Clear user configuration state"""
        if user_id in self.config_states:
            del self.config_states[user_id] 