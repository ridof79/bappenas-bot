#!/usr/bin/env python3
"""
Test script to send message to group manually
"""

import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from src.config.settings import Settings

async def test_send_message():
    """Test sending message to group"""
    print("🧪 Testing Manual Message Send...")
    
    bot = Bot(token=Settings.BOT_TOKEN)
    
    # You need to replace this with your actual group chat ID
    # You can get this by sending /start in the group and checking the logs
    group_chat_id = -1001234567890  # Replace with actual group ID
    
    try:
        message = (
            f"🧪 **Test Message** - Manual Send\n\n"
            f"Ini adalah test untuk memastikan bot bisa kirim pesan ke grup.\n\n"
            f"Jika Anda melihat pesan ini, berarti bot berfungsi normal."
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Test Button", callback_data="test_button")],
            [InlineKeyboardButton("📊 Cek Status", callback_data="refresh_attendance")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=group_chat_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        print("✅ Test message sent successfully!")
        
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
    
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_send_message()) 