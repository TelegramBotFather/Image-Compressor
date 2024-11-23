from pyrogram import Client
from pyrogram.types import CallbackQuery
from pyrogram.enums import ParseMode
from database.mongodb import db
from components.keyboards import Keyboards
from components.messages import Messages
from commands.convert import convert_command
from commands.stats import usage_stats
from database.user_db import get_user_settings, update_user_settings
from api_management.api_handler import APIHandler
from commands.support import support_command
import logging

logger = logging.getLogger(__name__)

class ButtonHandler:
    def __init__(self, client: Client):
        self.client = client

    async def handle_callback(self, client: Client, callback_query: CallbackQuery) -> None:
        """Handle callback queries."""
        try:
            data = callback_query.data
            
            if data.startswith("settings_"):
                await self._handle_settings(callback_query)
            elif data.startswith("api_key_"):
                await self._handle_api_key(callback_query)
            
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            await callback_query.answer("❌ An error occurred", show_alert=True)

    async def _handle_settings(self, callback_query: CallbackQuery) -> None:
        """Handle settings menu callbacks."""
        try:
            action = callback_query.data.split("_")[1]
            
            if action == "api":
                await self._handle_api_key(callback_query)
            elif action == "stats":
                await self._show_stats(callback_query)
            elif action == "close":
                await callback_query.message.delete()
            
        except Exception as e:
            logger.error(f"Error in settings handler: {str(e)}")
            raise

    async def _handle_api_key(self, callback_query: CallbackQuery) -> None:
        """Handle API key related callbacks."""
        try:
            user_id = callback_query.from_user.id
            settings = await get_user_settings(user_id)
            has_api_key = bool(settings.get('custom_api_key'))
            
            api_settings_text = (
                "🔑 <b>API Key Settings</b>\n\n"
                f"Status: {'✅ Custom API Key Set' if has_api_key else '❌ No Custom API Key'}\n\n"
                "You can add your own TinyPNG API key for better rate limits."
            )
            
            await callback_query.message.edit_text(
                api_settings_text,
                reply_markup=Keyboards.api_key_settings(has_api_key),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in API key handler: {str(e)}")
            raise
