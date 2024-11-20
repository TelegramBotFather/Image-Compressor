from typing import Optional, Dict, Any
from pyrogram import Client
from pyrogram.types import Message
from .api_handler import APIHandler
from components.keyboards import get_settings_buttons
from log_handlers.channel_logger import ChannelLogger
import logging

logger = logging.getLogger(__name__)

class APISettings:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()
        self.channel_logger = ChannelLogger(client)
        self._waiting_for_api = set()

    async def show_api_settings(self, message: Message) -> None:
        """Show API settings menu."""
        try:
            user_id = message.from_user.id
            has_custom_api = bool(await self.api_handler.get_api_key(user_id))
            
            text = (
                "⚙️ <b>API Settings</b>\n\n"
                "Here you can manage your TinyPNG API key and view usage statistics.\n\n"
                f"Current Status: {'✅ Using Custom API' if has_custom_api else '📎 Using Bot API'}\n"
            )
            
            await message.reply_text(
                text,
                reply_markup=get_settings_buttons(has_custom_api),
                parse_mode="html"
            )
        except Exception as e:
            logger.error(f"Error showing API settings: {str(e)}")