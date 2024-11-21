from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import logging

logger = logging.getLogger(__name__)

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