from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from components.keyboards import Keyboards
from components.messages import Messages
import logging

logger = logging.getLogger(__name__)

async def support_command(client: Client, message: Message) -> None:
    try:
        await message.reply_text(
            Messages.SUPPORT,
            reply_markup=Keyboards.main_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in support command: {str(e)}")
        await message.reply_text("❌ An error occurred. Please try again.")