from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from config import CONVERSION_FORMATS

class Keyboards:
    """Class to manage all keyboard markups for the bot."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Improved main menu keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Convert Image", callback_data="convert")],
            [
                InlineKeyboardButton("📊 Statistics", callback_data="stats"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("❓ Help Center", callback_data="help"),
                InlineKeyboardButton("👤 Support", callback_data="support")
            ]
        ])

    @staticmethod
    def settings_menu(has_api_key: bool = False) -> InlineKeyboardMarkup:
        """Improved settings menu keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎨 Format Settings", callback_data="settings_format")],
            [InlineKeyboardButton("🔔 Notification Settings", callback_data="settings_notifications")],
            [InlineKeyboardButton("🔑 API Configuration", callback_data="settings_api")],
            [InlineKeyboardButton("↩️ Back to Menu", callback_data="start")]
        ])

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
    def admin_menu() -> InlineKeyboardMarkup:
        """Admin menu keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="start")
            ]
        ])

    @staticmethod
    def user_management_menu():
        """User management menu."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 Banned Users", callback_data="admin_banned_users"),
                InlineKeyboardButton("📊 User Stats", callback_data="admin_user_stats")
            ],
            [
                InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_back")
            ]
        ])

    @staticmethod
    def admin_settings_menu():
        """Admin settings menu."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔑 API Settings", callback_data="admin_api_settings"),
                InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_bot_settings")
            ],
            [
                InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_back")
            ]
        ])
