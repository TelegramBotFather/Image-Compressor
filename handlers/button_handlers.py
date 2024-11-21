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

    async def handle(self, callback_query: CallbackQuery) -> None:
        """Handle callback queries from inline buttons."""
        try:
            data = callback_query.data
            user_id = callback_query.from_user.id

            if data == "start":
                await callback_query.message.edit_text(
                    Messages.WELCOME,
                    reply_markup=Keyboards.main_menu(),
                    parse_mode=ParseMode.HTML
                )

            # ... rest of the handler logic ...

            # Answer the callback query to remove the loading state
            await callback_query.answer()

        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            await callback_query.answer("❌ An error occurred", show_alert=True)

    async def _update_settings_message(self, callback_query: CallbackQuery, settings: dict) -> None:
        """Update settings message with current status."""
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

    async def _handle_format_selection(self, callback_query: CallbackQuery) -> None:
        """Handle format selection callbacks."""
        try:
            format_choice = callback_query.data.split("_")[1]  # format_jpeg -> jpeg
            user_id = callback_query.from_user.id
            
            await update_user_settings(user_id, {'default_format': format_choice})
            settings = await get_user_settings(user_id)
            
            await self._update_settings_message(callback_query, settings)
            await callback_query.answer(f"Format set to {format_choice.upper()}")
            
        except Exception as e:
            logger.error(f"Error in format selection: {str(e)}")
            await callback_query.answer("❌ Error setting format", show_alert=True)

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

    async def _handle_admin_buttons(self, callback_query: CallbackQuery) -> None:
        """Handle admin panel button callbacks."""
        try:
            data = callback_query.data
            user_id = callback_query.from_user.id

            # Verify admin status
            if user_id not in ADMIN_IDS:
                await callback_query.answer("⚠️ Unauthorized access", show_alert=True)
                return

            if data == "admin_stats":
                # Show detailed statistics
                from commands.admin_stats import detailed_stats
                await detailed_stats(self.client, callback_query.message)
                
            elif data == "admin_users":
                # Show user management options
                await callback_query.message.edit_text(
                    "👥 <b>User Management</b>\n\n"
                    "Select an action below:",
                    reply_markup=Keyboards.user_management_menu(),
                    parse_mode=ParseMode.HTML
                )
                
            elif data == "admin_broadcast":
                # Show broadcast message input prompt
                await callback_query.message.edit_text(
                    "📣 <b>Broadcast Message</b>\n\n"
                    "Please send the message you want to broadcast to all users.\n"
                    "Use /cancel to cancel the broadcast.",
                    parse_mode=ParseMode.HTML
                )
                
            elif data == "admin_settings":
                # Show admin settings
                await callback_query.message.edit_text(
                    "⚙️ <b>Admin Settings</b>\n\n"
                    "Configure bot settings below:",
                    reply_markup=Keyboards.admin_settings_menu(),
                    parse_mode=ParseMode.HTML
                )
                
            elif data == "admin_back":
                # Return to main admin menu
                await callback_query.message.edit_text(
                    "🔧 <b>Admin Dashboard</b>\n\nSelect an option below:",
                    reply_markup=Keyboards.admin_menu(),
                    parse_mode=ParseMode.HTML
                )

            await callback_query.answer()

        except Exception as e:
            logger.error(f"Error in admin button handler: {str(e)}")
            await callback_query.answer("❌ An error occurred", show_alert=True)