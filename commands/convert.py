from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from components.keyboards import Keyboards
from components.messages import Messages
from config import ERROR_MESSAGES
from utils.helpers import get_image_info
from utils.decorators import rate_limit
import logging

logger = logging.getLogger(__name__)

@rate_limit
async def convert_command(client: Client, message: Message) -> None:
    """Handle the /convert command."""
    try:
        await message.reply_text(
            Messages.FORMAT_SELECTION,
            reply_markup=Keyboards.format_selection(),
            parse_mode="html"
        )
    except Exception as e:
        logger.error(f"Error in convert command: {str(e)}")
        await message.reply_text(ERROR_MESSAGES["general_error"])

async def handle_convert_callback(client: Client, callback_query: CallbackQuery) -> None:
    """Handle format selection callbacks."""
    try:
        format_choice = callback_query.data.split("_")[1]
        await callback_query.message.edit_text(
            f"Selected format: {format_choice.upper()}\n"
            "Now send me the image you want to convert."
        )
        
        # Store user's format choice in database
        user_id = callback_query.from_user.id
        await db.settings.update_one(
            {"user_id": user_id},
            {"$set": {"current_format": format_choice}},
            upsert=True
        )
        
    except Exception as e:
        logger.error(f"Error handling convert callback: {str(e)}")
        await callback_query.answer(ERROR_MESSAGES["general_error"], show_alert=True)