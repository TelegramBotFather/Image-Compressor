from pyrogram import Client
from pyrogram.types import CallbackQuery
from pyrogram.enums import ParseMode
from database.mongodb import db
from components.keyboards import Keyboards
from components.messages import Messages
from commands.stats import usage_stats
from database.user_db import get_user_settings, update_user_settings
from api_management.api_handler import APIHandler
from commands.support import support_command
from api_management import APISettings
from database.api_db import get_user_api_stats
import logging

logger = logging.getLogger(__name__)
class ButtonHandler:
    def __init__(self, client: Client, api_settings: APISettings):
        self.client = client
        self.api_settings = api_settings
        self._handlers = {
            "start": self._handle_start,
            "stats": self._handle_stats,
            "support": self._handle_support,
            "retry": self._handle_retry,
            # Admin handlers
            "admin_back": self._handle_admin_back,
            "admin_api_settings": self._handle_admin_api_settings,
            "admin_bot_settings": self._handle_admin_bot_settings,
        }

    async def handle(self, client: Client, callback_query: CallbackQuery) -> None:
        try:
            data = callback_query.data
            
            # Special handling for API settings
            if data in ["settings_api", "api_key_toggle"]:
                await self.api_settings.handle_callback(callback_query)
                return
                
            handler = self._handlers.get(data)
            if handler:
                await handler(callback_query)
                await callback_query.answer()
            else:
                logger.warning(f"Unknown callback data: {data}")
                await callback_query.answer("⚠️ Invalid button", show_alert=True)
                
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            await callback_query.answer("❌ An error occurred", show_alert=True)

    async def _handle_stats(self, callback_query: CallbackQuery) -> None:
        """Handle stats button."""
        try:
            user_id = callback_query.from_user.id
            stats = await get_user_api_stats(user_id)
            
            await callback_query.message.edit_text(
                Messages.get_stats(stats),
                reply_markup=Keyboards.stats_menu(),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in stats handler: {str(e)}")
            raise

    async def _handle_start(self, callback_query: CallbackQuery) -> None:
        """Handle start button (return to main menu)."""
        try:
            await callback_query.message.edit_text(
                dashboard_text,
                reply_markup=Keyboards.admin_menu(),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in start handler: {str(e)}")
            raise

    async def _handle_retry(self, callback_query: CallbackQuery) -> None:
        """Handle retry button."""
        try:
            # Simply delete the error message to let user try again
            await callback_query.message.delete()
        except Exception as e:
            logger.error(f"Error in retry handler: {str(e)}")
            raise

    async def _handle_support(self, callback_query: CallbackQuery) -> None:
        """Handle support button."""
        try:
            support_command(callback_query)
        except Exception as e:
            logger.error(f"Error in support handler: {str(e)}")
            raise

    async def _handle_admin_back(self, callback_query: CallbackQuery) -> None:
        """Handle admin back button."""
        try:
            await callback_query.message.edit_text(
                dashboard_text,
                reply_markup=Keyboards.admin_menu(),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in admin back handler: {str(e)}")
            raise


    async def _handle_admin_bot_settings(self, callback_query: CallbackQuery) -> None:
        """Handle admin bot settings button."""
        try:
            # Implement admin bot settings handler logic here
            pass
        except Exception as e:
            logger.error(f"Error in admin bot settings handler: {str(e)}")
            raise

