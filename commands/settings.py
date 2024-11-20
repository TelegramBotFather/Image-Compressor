from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards
from database.user_db import get_user_settings
from utils.decorators import rate_limit
import logging

logger = logging.getLogger(__name__)

@rate_limit
async def settings_command(client: Client, message: Message) -> None:
    """Handle the /settings command."""
    try:
        user_id = message.from_user.id
        settings = await get_user_settings(user_id)

        settings_text = (
            "⚙️ <b>Bot Settings</b>\n\n"
            "Configure your preferences:\n\n"
            "🔑 <b>API Settings</b>\n"
            f"├ Custom API: {'✅ Enabled' if settings.get('custom_api_key') else '❌ Disabled'}\n"
            f"└ Default Format: {settings.get('default_format', 'JPEG').upper()}\n\n"
            "🔔 <b>Notifications</b>\n"
            f"└ Status: {'✅ Enabled' if settings.get('notifications_enabled') else '❌ Disabled'}"
        )

        await message.reply_text(
            settings_text,
            reply_markup=Keyboards.settings_menu(bool(settings.get('custom_api_key'))),
            parse_mode="html"
        )

    except Exception as e:
        logger.error(f"Error in settings command: {str(e)}")
        await message.reply_text("❌ An error occurred. Please try again.")