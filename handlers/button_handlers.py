from pyrogram import Client
from pyrogram.types import CallbackQuery
from pyrogram.enums import ParseMode
from components.messages import Messages
from components.keyboards import Keyboards
from api_management.api_handler import APIHandler
from database.user_db import get_user_settings, update_user_settings
from config import ERROR_MESSAGES
import logging

logger = logging.getLogger(__name__)

class ButtonHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()

    async def _handle_settings(self, callback_query: CallbackQuery) -> None:
        """Handle settings menu callbacks."""
        try:
            user_id = callback_query.from_user.id
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
            
            await callback_query.message.edit_text(
                settings_text,
                reply_markup=Keyboards.settings_menu(bool(settings.get('custom_api_key'))),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Error in settings handler: {str(e)}")
            raise

    async def handle(self, client: Client, callback_query: CallbackQuery) -> None:
        """Handle all callback queries."""
        try:
            data = callback_query.data
            message = callback_query.message
            user_id = callback_query.from_user.id

            if data == "start":
                await message.edit_text(
                    Messages.WELCOME,
                    reply_markup=Keyboards.main_menu(),
                    parse_mode=ParseMode.HTML
                )
                
            elif data == "help":
                await message.edit_text(
                    Messages.HELP,
                    reply_markup=Keyboards.help_menu(),
                    parse_mode=ParseMode.HTML
                )
                
            elif data.startswith("settings"):
                await self._handle_settings(callback_query)
                
            elif data.startswith("format"):
                await self._handle_format_selection(callback_query)
                
            elif data.startswith("api_key"):
                await self._handle_api_key(callback_query)
                
            await callback_query.answer()
            
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            await callback_query.answer(
                ERROR_MESSAGES["general_error"],
                show_alert=True
            )

    async def _handle_format_selection(self, callback_query: CallbackQuery) -> None:
        """Handle format selection callbacks."""
        try:
            format_choice = callback_query.data.split("_")[1]
            user_id = callback_query.from_user.id
            
            await update_user_settings(user_id, {'default_format': format_choice})
            
            await callback_query.message.edit_text(
                f"Selected format: {format_choice.upper()}\n"
                "Now send me an image to convert.",
                reply_markup=Keyboards.main_menu()
            )
        except Exception as e:
            logger.error(f"Error in format selection: {str(e)}")
            raise

    async def _handle_api_key(self, callback_query: CallbackQuery) -> None:
        """Handle API key related callbacks."""
        try:
            user_id = callback_query.from_user.id
            settings = await get_user_settings(user_id)
            has_api_key = bool(settings.get('custom_api_key'))
            
            await callback_query.message.edit_text(
                Messages.API_KEY_SETTINGS,
                reply_markup=Keyboards.api_key_settings(has_api_key)
            )
        except Exception as e:
            logger.error(f"Error in API key handler: {str(e)}")
            raise