from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from database.api_db import get_user_api_stats
from components.messages import Messages
from utils.decorators import rate_limit
import logging

logger = logging.getLogger(__name__)

@rate_limit
async def usage_stats(client: Client, message: Message) -> None:
    """Handle the /stats command."""
    try:
        user_id = message.from_user.id
        stats = await get_user_api_stats(user_id)
        
        await message.reply_text(
            Messages.get_stats(stats),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in stats command: {str(e)}")
        await message.reply_text("❌ An error occurred. Please try again.")