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
        data = query.data
        
        # Debug logging
        logger.info(f"Callback received: {data}")
        
        try:
            await query.answer()
            
            # Handle specific callback patterns first
            if data in ["clock_in_button", "clock_out_button"]:
                logger.info(f"Clock button callback: {data}")
                # This should be handled by scheduled_handlers, not here
                await query.answer("❌ Callback tidak dikenali")
                return
                
            elif data == "refresh_attendance":
                logger.info(f"Refresh attendance callback: {data}")
                # This should be handled by scheduled_handlers, not here
                await query.answer("❌ Callback tidak dikenali")
                return
                
            elif data.startswith("config_"):
                logger.info(f"Handling config callback: {data}")
                await self.handle_config_callback(update, context, data)
            elif data.startswith("view_"):
                logger.info(f"Handling view callback: {data}")
                await self.handle_view_callback(update, context, data)
            elif data.startswith("set_"):
                logger.info(f"Handling set callback: {data}")
                await self.handle_set_callback(update, context, data)
            elif data.startswith("day_"):
                logger.info(f"Handling day callback: {data}")
                await self.handle_day_callback(update, context, data)
            elif data.startswith("save_"):
                logger.info(f"Handling save callback: {data}")
                await self.handle_save_callback(update, context, data)
            elif data.startswith("cancel_"):
                logger.info(f"Handling cancel callback: {data}")
                await self.handle_cancel_callback(update, context, data)
            else:
                logger.warning(f"Unknown callback data: {data}")
                await query.answer("❌ Callback tidak dikenali")
                
        except Exception as e:
            logger.error(f"Error in handle_callback: {e}")
            try:
                await query.answer("❌ Terjadi kesalahan")
            except:
                pass
    
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
        elif data == "config_back":
            # Go back to main config menu
            await self.show_main_config_menu(update, context)
        elif data == "config_main":
            # Go back to main config menu
            await self.show_main_config_menu(update, context)
    
    async def handle_config_callback_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wrapper for handle_config_callback that extracts data from callback_query"""
        data = update.callback_query.data
        await self.handle_config_callback(update, context, data)
    
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
            [InlineKeyboardButton("🔙 Kembali", callback_data="config_main")]
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
            [InlineKeyboardButton("🔙 Kembali", callback_data=f"config_{config_type}")]
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
            [InlineKeyboardButton("🔙 Kembali", callback_data=f"config_{config_type}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def show_days_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, config_type: str):
        """Show days setup interface"""
        query = update.callback_query
        
        try:
            # Store state for this user
            user_id = query.from_user.id
            self.config_states[user_id] = {
                'type': 'days',
                'config_type': config_type,
                'chat_id': query.message.chat.id
            }
            
            # Get current configuration
            chat_id = query.message.chat.id
            current_config = self.db.get_configuration(chat_id, config_type)
            
            # Initialize enabled_days with default or current value
            if current_config and 'enabled_days' in current_config:
                enabled_days = current_config['enabled_days']
            else:
                enabled_days = [0, 1, 2, 3, 4]  # Monday to Friday
            
            keyboard = []
            for day_num in range(7):
                day_name = Settings.get_day_name(day_num)
                is_enabled = day_num in enabled_days
                button_text = f"{'✅' if is_enabled else '❌'} {day_name}"
                callback_data = f"day_{day_num}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            keyboard.append([
                InlineKeyboardButton("🔙 Kembali", callback_data=f"config_{config_type}")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"📅 **Atur Hari Aktif {Settings.get_clock_type_name(config_type)}**\n\n"
            message += "Pilih hari yang aktif untuk pengingat otomatis:"
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in show_days_setup: {e}")
            await query.answer("❌ Terjadi kesalahan saat menampilkan pengaturan hari")
    
    async def handle_day_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle day selection callbacks"""
        query = update.callback_query
        
        try:
            parts = data.split('_')
            if len(parts) != 2:
                await query.answer("❌ Format callback tidak valid")
                return
                
            day_num_str = parts[1]
            
            # Get config_type from user state
            user_id = query.from_user.id
            user_state = self.config_states.get(user_id)
            if not user_state or 'config_type' not in user_state:
                await query.answer("❌ Sesi konfigurasi tidak ditemukan")
                return
                
            config_type = user_state['config_type']
            
            # Validate config_type
            if config_type not in ['clock_in', 'clock_out']:
                await query.answer("❌ Tipe konfigurasi tidak valid")
                return
            
            # Validate and convert day_num
            try:
                day_num = int(day_num_str)
                if day_num < 0 or day_num > 6:
                    await query.answer("❌ Nomor hari tidak valid")
                    return
            except ValueError:
                await query.answer("❌ Format nomor hari tidak valid")
                return
            
            chat_id = query.message.chat.id
            
            # Get current configuration
            current_config = self.db.get_configuration(chat_id, config_type)
            
            # Initialize enabled_days with default or current value
            if current_config and 'enabled_days' in current_config:
                enabled_days = current_config['enabled_days'].copy()
            else:
                enabled_days = [0, 1, 2, 3, 4].copy()  # Monday to Friday
            
            # Toggle day
            if day_num in enabled_days:
                enabled_days.remove(day_num)
            else:
                enabled_days.append(day_num)
            
            # Sort enabled_days for consistency
            enabled_days.sort()
            
            # Update configuration
            if current_config:
                start_time = current_config['start_time']
                end_time = current_config['end_time']
                interval = current_config['reminder_interval']
            else:
                if config_type == 'clock_in':
                    start_time = "07:00"
                    end_time = "09:00"
                else:
                    start_time = "16:00"
                    end_time = "18:00"
                interval = 15
            
            # Save configuration
            success = self.db.save_configuration(chat_id, config_type, start_time, end_time, interval, enabled_days)
            
            if success:
                day_name = Settings.get_day_name(day_num)
                status = "diaktifkan" if day_num in enabled_days else "dinonaktifkan"
                await query.answer(f"Hari {day_name} {status}")
                
                # Refresh the days setup interface
                await self.show_days_setup(update, context, config_type)
            else:
                await query.answer("❌ Gagal menyimpan konfigurasi")
                
        except Exception as e:
            logger.error(f"Error in handle_day_callback: {e}")
            await query.answer("❌ Terjadi kesalahan saat mengatur hari")
    
    async def handle_day_callback_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wrapper for handle_day_callback that extracts data from callback_query"""
        data = update.callback_query.data
        await self.handle_day_callback(update, context, data)
    
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
    
    async def handle_save_callback_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wrapper for handle_save_callback that extracts data from callback_query"""
        data = update.callback_query.data
        await self.handle_save_callback(update, context, data)
    
    async def handle_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle cancel callbacks"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Clear user state
        if user_id in self.config_states:
            del self.config_states[user_id]
        
        await query.answer("❌ Dibatalkan")
        await self.show_current_config(update, context)
    
    async def handle_cancel_callback_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wrapper for handle_cancel_callback that extracts data from callback_query"""
        data = update.callback_query.data
        await self.handle_cancel_callback(update, context, data)
    
    def get_user_state(self, user_id: int):
        """Get user configuration state"""
        return self.config_states.get(user_id)
    
    def clear_user_state(self, user_id: int):
        """Clear user configuration state"""
        if user_id in self.config_states:
            del self.config_states[user_id]
    
    async def handle_set_callback_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wrapper for handle_set_callback that extracts data from callback_query"""
        data = update.callback_query.data
        await self.handle_set_callback(update, context, data)
    
    async def handle_view_callback_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wrapper for handle_view_callback that extracts data from callback_query"""
        data = update.callback_query.data
        await self.handle_view_callback(update, context, data)
    
    async def show_main_config_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main configuration menu"""
        query = update.callback_query
        chat_id = query.message.chat.id
        
        # Get current configurations
        clock_in_config = self.db.get_configuration(chat_id, 'clock_in')
        clock_out_config = self.db.get_configuration(chat_id, 'clock_out')
        
        keyboard = [
            [InlineKeyboardButton("🟢 Konfigurasi Clock In", callback_data="config_clock_in")],
            [InlineKeyboardButton("🔴 Konfigurasi Clock Out", callback_data="config_clock_out")],
            [InlineKeyboardButton("📊 Lihat Konfigurasi", callback_data="view_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "⚙️ **Menu Konfigurasi**\n\n"
        message += "Pilih jenis konfigurasi yang ingin diatur:"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN) 