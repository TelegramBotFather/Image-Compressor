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
        self.api_handler = APIHandler()

    async def handle(self, client: Client, callback_query: CallbackQuery) -> None:
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
            elif data == "settings":
                await self._handle_settings(callback_query)
            elif data == "convert":
                await convert_command(self.client, callback_query.message)
            elif data == "stats":
                await usage_stats(self.client, callback_query.message)
            elif data == "support":
                await support_command(self.client, callback_query.message)
            elif data == "help":
                await callback_query.message.edit_text(
                    Messages.HELP,
                    reply_markup=Keyboards.help_menu(),
                    parse_mode=ParseMode.HTML
                )
            elif data.startswith("format_"):
                await self._handle_format_selection(callback_query)
            elif data.startswith("settings_"):
                await self._handle_settings_submenu(callback_query)
            
            await callback_query.answer()
            
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            await callback_query.answer("❌ An error occurred", show_alert=True)

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
            format_choice = callback_query.data.split("_")[1]
            user_id = callback_query.from_user.id
            
            await update_user_settings(user_id, {'default_format': format_choice})
            
            await callback_query.message.edit_text(
                f"Format set to {format_choice.upper()}\nNow send me an image to compress!",
                parse_mode=ParseMode.HTML
            )
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

            if data == "admin_stats":
                await usage_stats(self.client, callback_query.message)
            elif data == "admin_users":
                # Show user list
                users = await db.users.find().to_list(length=100)
                user_text = "👥 **Registered Users**\n\n"
                for user in users:
                    user_text += f"• ID: {user['user_id']}\n"
                    user_text += f"• Username: @{user.get('username', 'None')}\n\n"
                await callback_query.message.edit_text(user_text)
            elif data == "admin_broadcast":
                await broadcast_command(self.client, callback_query.message)
            elif data == "admin_settings":
                await settings_command(self.client, callback_query.message)

            await callback_query.answer()

        except Exception as e:
            logger.error(f"Error in admin buttons: {str(e)}")
            await callback_query.answer("❌ Error occurred", show_alert=True)

    async def _handle_settings_submenu(self, callback_query: CallbackQuery) -> None:
        """Handle settings submenu callbacks."""
        try:
            data = callback_query.data
            user_id = callback_query.from_user.id
            
            if data == "settings_format":
                await callback_query.message.edit_text(
                    "🎨 Select Default Format",
                    reply_markup=Keyboards.format_selection_settings(),
                    parse_mode=ParseMode.HTML
                )
            elif data == "settings_notifications":
                settings = await get_user_settings(user_id)
                current_status = settings.get('notifications_enabled', False)
                await update_user_settings(user_id, {'notifications_enabled': not current_status})
                await self._handle_settings(callback_query)
            elif data == "settings_api":
                await self._handle_api_key(callback_query)
                
        except Exception as e:
            logger.error(f"Error in settings submenu: {str(e)}")
            await callback_query.answer("❌ Error in settings", show_alert=True)
