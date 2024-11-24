from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards
from utils.decorators import admin_only, rate_limit
from database.mongodb import db
import asyncio
import logging

logger = logging.getLogger(__name__)

@admin_only
@rate_limit
async def broadcast_command(client: Client, message: Message) -> None:
    """Handle the /broadcast command."""
    try:
        if not message.reply_to_message:
            await message.reply_text("⚠️ Please reply to the message you want to broadcast.")
            return

        status_msg = await message.reply_text("📊 Calculating users...")
        users = await db.users.find({"banned": {"$ne": True}}).to_list(None)
        
        if not users:
            await status_msg.edit_text("❌ No users found to broadcast to.")
            return

        success = 0
        failed = 0
        total = len(users)

        await status_msg.edit_text(f"📤 Broadcasting to {total} users...")

        for user in users:
            try:
                await message.reply_to_message.copy(user["user_id"])
                success += 1
            except Exception as e:
                logger.error(f"Broadcast failed for user {user['user_id']}: {str(e)}")
                failed += 1

            if (success + failed) % 5 == 0:
                await status_msg.edit_text(
                    f"📤 Broadcasting...\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"📊 Progress: {((success + failed) / total) * 100:.1f}%"
                )

        await status_msg.edit_text(
            f"📤 Broadcast completed!\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}\n"
            f"👥 Total Users: {total}"
        )

    except Exception as e:
        logger.error(f"Error in broadcast: {str(e)}")
        await message.reply_text("❌ An error occurred during broadcast.")