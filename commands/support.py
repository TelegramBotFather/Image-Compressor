from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)

async def support_command(client: Client, message: Message) -> None:
    try:
        support_text = (
            "💬 <b>Support</b>\n\n"
            "Need help? Have suggestions?\n"
            "Contact us through the following channels:"
        )

        await message.reply_text(
            support_text,
            reply_markup=Keyboards.main_menu(),
            parse_mode="html"
        )

    except Exception as e:
        logger.error(f"Error in support command: {str(e)}")
        await message.reply_text("❌ An error occurred. Please try again.")