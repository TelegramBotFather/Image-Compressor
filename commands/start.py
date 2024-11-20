from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards
from database.user_db import save_user
from log_handlers.channel_logger import ChannelLogger
from components.messages import Messages
from utils.decorators import rate_limit
import logging

logger = logging.getLogger(__name__)

@rate_limit
async def start_command(client: Client, message: Message) -> None:
    """Handle the /start command."""
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name

        # Save user to database
        await save_user(user_id, username, first_name)

        # Log new user
        channel_logger = ChannelLogger(client)
        await channel_logger.log_new_user(user_id, username)

        # Send welcome message
        await message.reply_text(
            Messages.WELCOME,
            reply_markup=Keyboards.main_menu(),
            parse_mode="html"
        )

    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await message.reply_text("❌ An error occurred. Please try again.")