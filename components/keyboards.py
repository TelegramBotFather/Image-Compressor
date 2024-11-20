from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from config import CONVERSION_FORMATS

class Keyboards:
    """Class to manage all keyboard markups for the bot."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("📊 Stats", callback_data="stats")
            ],
            [
                InlineKeyboardButton("🔄 Convert", callback_data="convert"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ])

    @staticmethod
    def settings_menu(has_api_key: bool = False) -> InlineKeyboardMarkup:
        """Settings menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(
                    "🔑 API Key", 
                    callback_data="settings_api"
                )
            ],
            [
                InlineKeyboardButton(
                    "📋 Default Format", 
                    callback_data="settings_format"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔔 Notifications", 
                    callback_data="settings_notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Back to Menu", 
                    callback_data="start"
                )
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def format_selection_settings() -> InlineKeyboardMarkup:
        """Format selection keyboard for settings."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("WEBP", callback_data="set_format_webp"),
                InlineKeyboardButton("JPEG", callback_data="set_format_jpeg"),
                InlineKeyboardButton("PNG", callback_data="set_format_png")
            ],
            [
                InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")
            ]
        ])

    @staticmethod
    def api_key_settings(has_api_key: bool) -> InlineKeyboardMarkup:
        """API key settings keyboard."""
        buttons = [
            [
                InlineKeyboardButton(
                    "🗑 Remove API Key" if has_api_key else "➕ Add API Key",
                    callback_data="api_key_toggle"
                )
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="start")
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
        """Generic confirmation keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ No", callback_data="cancel")
            ]
        ])

    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Help menu keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📱 Contact Support",
                    url="https://t.me/YourSupportUsername"
                )
            ],
            [
                InlineKeyboardButton(
                    "📖 Commands List",
                    callback_data="help_commands"
                )
            ],
            [
                InlineKeyboardButton("🏠 Back to Menu", callback_data="start")
            ]
        ])

    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        """Admin panel keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="start")
            ]
        ])

    @staticmethod
    def format_selection() -> InlineKeyboardMarkup:
        """Format selection keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("JPEG", callback_data="format_jpeg"),
                InlineKeyboardButton("PNG", callback_data="format_png")
            ],
            [
                InlineKeyboardButton("WEBP", callback_data="format_webp")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings")
            ]
        ])

    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Admin menu keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="start")
            ]
        ])
