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
        self._waiting_for_api = set()

    async def handle(self, client: Client, callback_query: CallbackQuery) -> None:
        """Handle callback queries from inline buttons."""
        try:
            data = callback_query.data
            
            # Map callback data to handler methods
            handlers = {
                "stats": self._handle_stats,
                "start": self._handle_start,
                "settings_api": self._handle_api_key,
                "api_key_toggle": self._handle_api_key_toggle,
                "support": self._handle_support,
                "retry": self._handle_retry
            }
            
            # Get the appropriate handler
            handler = handlers.get(data)
            if handler:
                await handler(callback_query)
                # Answer callback query to remove loading state
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

    async def _handle_settings(self, callback_query: CallbackQuery) -> None:
        """Handle settings button."""
        try:
            user_id = callback_query.from_user.id
            settings = await get_user_settings(user_id)
            
            await callback_query.message.edit_text(
                "⚙️ <b>Settings</b>\n\n"
                f"API Key: {'✅' if settings.get('custom_api_key') else '❌'}",
                reply_markup=Keyboards.settings_menu(bool(settings.get('custom_api_key'))),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in settings handler: {str(e)}")
            raise

    async def _handle_help(self, callback_query: CallbackQuery) -> None:
        """Handle help button."""
        try:
            await callback_query.message.edit_text(
                Messages.HELP,
                reply_markup=Keyboards.main_menu(),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in help handler: {str(e)}")
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

    async def _handle_admin_api_settings(self, callback_query: CallbackQuery) -> None:
        """Handle admin API settings button."""
        try:
            support_text = (
                "🎯 <b>Need Help?</b>\n\n"
                "Choose from the options below:\n\n"
                "📱 <b>Quick Support</b>\n"
                "• Use buttons below to get help\n"
                "• Contact support team directly\n\n"
                "⚡️ <b>Response Time</b>\n"
                "• Usually within 24 hours\n"
                "• Priority support for API users"
            )
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📞 Support Group", url="https://t.me/supportgroup"),
                    InlineKeyboardButton("📢 Update Channel", url="https://t.me/Matiz_Tech")
                ],
                [
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/MatinBhai")
                ],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="start")]
            ])
            
            await callback_query.message.edit_text(
                support_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in support handler: {str(e)}")
            raise

    async def _handle_retry(self, callback_query: CallbackQuery) -> None:
        """Handle retry button."""
        try:
            # Simply delete the error message to let user try again
            await callback_query.message.delete()
        except Exception as e:
            logger.error(f"Error in retry handler: {str(e)}")
            raise

    async def _handle_api_key(self, callback_query: CallbackQuery) -> None:
        """Handle API key settings button."""
        try:
            user_id = callback_query.from_user.id
            settings = await get_user_settings(user_id)
            
            await callback_query.message.edit_text(
                "🔑 <b>API Key Settings</b>\n\n"
                "With a custom API key:\n"
                "• Higher daily limits\n"
                "• Priority processing\n"
                "• Usage statistics\n\n"
                "Get your API key from tinypng.com",
                reply_markup=Keyboards.api_key_settings(bool(settings.get('custom_api_key'))),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in API key handler: {str(e)}")
            raise

    async def _handle_api_key_toggle(self, callback_query: CallbackQuery) -> None:
        """Handle API key toggle button."""
        try:
            user_id = callback_query.from_user.id
            settings = await get_user_settings(user_id)
            has_api_key = bool(settings.get('custom_api_key'))

            if has_api_key:
                # Remove API key
                await update_user_settings(user_id, {'custom_api_key': None})
                await callback_query.message.edit_text(
                    "🔑 API key removed successfully!",
                    reply_markup=Keyboards.api_key_settings(False),
                    parse_mode=ParseMode.HTML
                )
            else:
                # Start API key input process
                self._waiting_for_api.add(user_id)
                await callback_query.message.edit_text(
                    "📝 Please send your TinyPNG API key.\n\n"
                    "You can get it from: https://tinypng.com/developers",
                    reply_markup=Keyboards.cancel_button(),
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"Error in API key toggle handler: {str(e)}")
            raise

