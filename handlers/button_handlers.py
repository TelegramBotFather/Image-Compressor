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

    async def handle(self, client: Client, callback_query: CallbackQuery) -> None:
        """Handle all callback queries."""
        try:
            data = callback_query.data
            
            if data == "help":
                await callback_query.message.edit_text(
                    Messages.HELP,
                    reply_markup=Keyboards.help_menu(),
                    parse_mode=ParseMode.HTML
                )
                
            elif data == "start":
                await callback_query.message.edit_text(
                    Messages.WELCOME,
                    reply_markup=Keyboards.main_menu(),
                    parse_mode=ParseMode.HTML
                )
                
            elif data == "convert":
                await convert_command(self.client, callback_query.message)
                await callback_query.answer()
            
            elif data == "stats":
                await usage_stats(self.client, callback_query.message)
                await callback_query.answer()
                
            elif data.startswith("settings"):
                if data == "settings_notifications":
                    # Toggle notifications instead of showing same message
                    user_id = callback_query.from_user.id
                    settings = await get_user_settings(user_id)
                    new_status = not settings.get('notifications_enabled', True)
                    
                    await db.settings.update_one(
                        {"user_id": user_id},
                        {"$set": {"notifications_enabled": new_status}},
                        upsert=True
                    )
                    
                    # Update message with new status
                    settings['notifications_enabled'] = new_status
                    await self._update_settings_message(callback_query, settings)
                    
                elif data == "settings_format":
                    # Show format selection keyboard instead of same message
                    keyboard = Keyboards.format_selection_settings()
                    await callback_query.message.edit_text(
                        "Select your default format:",
                        reply_markup=keyboard
                    )
                else:
                    await self._handle_settings(callback_query)
                    
            elif data.startswith("set_format_"):
                format_choice = data.split("_")[2]  # Extract format from set_format_jpeg
                user_id = callback_query.from_user.id
                
                # Update user's default format
                await update_user_settings(user_id, {'default_format': format_choice})
                
                # Show confirmation and return to settings
                await callback_query.message.edit_text(
                    f"✅ Default format set to {format_choice.upper()}\n"
                    "Your images will be converted to this format by default.",
                    reply_markup=Keyboards.settings_menu(
                        bool((await get_user_settings(user_id)).get('custom_api_key'))
                    ),
                    parse_mode=ParseMode.HTML
                )
            
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