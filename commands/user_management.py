from pyrogram import Client
from pyrogram.types import Message
from utils.decorators import admin_only
from database.mongodb import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@admin_only
async def ban_user(client: Client, message: Message) -> None:
    """Ban a user from using the bot."""
    try:
        # Extract user ID and reason
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "⚠️ Usage:\n"
                "/ban user_id [reason]\n\n"
                "Example: /ban 123456789 Spam"
            )
            return

        user_id = int(parts[1])
        reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"

        # Check if user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            await message.reply_text("❌ User not found in database.")
            return

        # Check if already banned
        if user.get("banned", False):
            await message.reply_text(
                f"⚠️ User {user_id} is already banned.\n"
                f"Reason: {user.get('ban_reason', 'No reason provided')}"
            )
            return

        # Ban user
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "banned": True,
                    "ban_reason": reason,
                    "banned_at": datetime.now(),
                    "banned_by": message.from_user.id
                }
            }
        )

        # Log ban
        logger.info(f"User {user_id} banned by {message.from_user.id}. Reason: {reason}")

        await message.reply_text(
            f"✅ User {user_id} has been banned\n"
            f"Reason: {reason}"
        )

    except ValueError:
        await message.reply_text("❌ Invalid user ID format.")
    except Exception as e:
        logger.error(f"Error in ban_user: {str(e)}")
        await message.reply_text("❌ An error occurred while banning user.")

@admin_only
async def unban_user(client: Client, message: Message) -> None:
    """Unban a user."""
    try:
        # Extract user ID
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text(
                "⚠️ Usage:\n"
                "/unban user_id\n\n"
                "Example: /unban 123456789"
            )
            return

        user_id = int(parts[1])

        # Check if user exists and is banned
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            await message.reply_text("❌ User not found in database.")
            return

        if not user.get("banned", False):
            await message.reply_text("⚠️ This user is not banned.")
            return

        # Unban user
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"banned": False},
                "$unset": {
                    "ban_reason": "",
                    "banned_at": "",
                    "banned_by": ""
                }
            }
        )

        # Log unban
        logger.info(f"User {user_id} unbanned by {message.from_user.id}")

        await message.reply_text(
            f"✅ User {user_id} has been unbanned\n"
            f"They can now use the bot again."
        )

    except ValueError:
        await message.reply_text("❌ Invalid user ID format.")
    except Exception as e:
        logger.error(f"Error in unban_user: {str(e)}")
        await message.reply_text("❌ An error occurred while unbanning user.")

@admin_only
async def banned_users_list(client: Client, message: Message) -> None:
    """Get list of banned users."""
    try:
        # Get all banned users
        banned_users = await db.users.find(
            {"banned": True}
        ).to_list(None)

        if not banned_users:
            await message.reply_text("✅ No banned users found.")
            return

        # Format banned users list
        text = "🚫 <b>Banned Users</b>\n\n"
        for user in banned_users:
            text += (
                f"👤 User ID: <code>{user['user_id']}</code>\n"
                f"📅 Banned At: {user['banned_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📝 Reason: {user.get('ban_reason', 'No reason provided')}\n"
                f"👮‍♂️ Banned By: <code>{user.get('banned_by', 'Unknown')}</code>\n\n"
            )

        await message.reply_text(
            text,
            parse_mode="html"
        )

    except Exception as e:
        logger.error(f"Error in banned_users_list: {str(e)}")
        await message.reply_text("❌ An error occurred while fetching banned users list.")