from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import logging

logger = logging.getLogger(__name__)

async def support_command(client: Client, message: Message) -> None:
    try:
        support_text = (
            "🎯 <b>Need Help?</b>\n\n"
            "Choose from the options below:\n\n"
            "📱 <b>Quick Support</b>\n"
            "• Use buttons below to get help\n"
            "• Contact support team directly\n\n"
            "⚡️ <b>Response Time</b>\n"
            "• Usually within 24 hours\n"
            "• Priority support for API users"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📞 Support Group", url="https://t.me/YourSupportGroup"),
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/YourUsername")
            ],
            [
                InlineKeyboardButton("📢 Updates Channel", url="https://t.me/YourChannel")
            ],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="start")]
        ])
        
        await message.reply_text(
            support_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in support command: {str(e)}")
        await handle_error(message, e)

async def handle_error(message: Message, error: Exception, error_message: str = None) -> None:
    """Centralized error handler with user-friendly messages."""
    try:
        error_text = (
            "❌ <b>Error Occurred</b>\n\n"
            f"{error_message or 'An unexpected error occurred.'}\n\n"
            "🔄 <b>What to do?</b>\n"
            "• Try again in a few moments\n"
            "• Check file format & size\n"
            "• Contact support if persists"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Try Again", callback_data="retry"),
                InlineKeyboardButton("📞 Support", callback_data="support")
            ]
        ])
        
        await message.reply_text(
            error_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        # Log error
        logger.error(f"Error: {str(error)}", exc_info=True)
        
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")