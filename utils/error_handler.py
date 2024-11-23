from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import logging

logger = logging.getLogger(__name__)

async def handle_error(message: Message, error: Exception, error_message: str = None) -> None:
    """Centralized error handler with user-friendly messages."""
    try:
        error_text = "❌ Error: " + (error_message or str(error))
        
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
        
        logger.error(f"Error: {str(error)}", exc_info=True)
        
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}", exc_info=True)