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
                    f"🔑 API Key ({'✅' if has_api_key else '❌'})", 
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
    def format_selection() -> InlineKeyboardMarkup:
        """Format selection keyboard."""
        buttons = []
        # Add format buttons in pairs
        for i in range(0, len(CONVERSION_FORMATS), 2):
            row = []
            row.append(InlineKeyboardButton(
                CONVERSION_FORMATS[i].upper(),
                callback_data=f"format_{CONVERSION_FORMATS[i]}"
            ))
            if i + 1 < len(CONVERSION_FORMATS):
                row.append(InlineKeyboardButton(
                    CONVERSION_FORMATS[i + 1].upper(),
                    callback_data=f"format_{CONVERSION_FORMATS[i + 1]}"
                ))
            buttons.append(row)
        
        # Add back button
        buttons.append([
            InlineKeyboardButton("🏠 Back to Menu", callback_data="start")
        ])
        return InlineKeyboardMarkup(buttons)

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
