from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards
from database.user_db import get_user_settings
from utils.decorators import rate_limit
import logging
from pyrogram.enums import ParseMode
from utils.error_handler import handle_error

logger = logging.getLogger(__name__)

@rate_limit
async def settings_command(client: Client, message: Message) -> None:
    """Handle the /settings command."""
    try:
        user_id = message.from_user.id
        settings = await get_user_settings(user_id)

        settings_text = (
            "⚙️ <b>Settings</b>\n\n"
            f"API Key: {'✅' if settings.get('custom_api_key') else '❌'}"
        )

        await message.reply_text(
            settings_text,
            reply_markup=Keyboards.settings_menu(bool(settings.get('custom_api_key'))),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        await handle_error(message, e, "Error accessing settings")