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
    """Handle the /broadcast command (admin only)."""
    try:
        if not message.reply_to_message:
            await message.reply_text("⚠️ Please reply to the message you want to broadcast.")
            return

        users_cursor = db.users.find({"banned": {"$ne": True}})
        users = await users_cursor.to_list(length=None)
        total_users = len(users)

        if total_users == 0:
            await message.reply_text("❌ No users found to broadcast to.")
            return

        status_msg = await message.reply_text(
            f"📤 Broadcasting initiated...\n\n👥 Total Users: {total_users}\n✅ Successful: 0\n❌ Failed: 0\n📊 Progress: 0%"
        )

        success, failed = 0, 0
        batch_size = 25  # Adjust based on rate limits
        tasks = []

        async def send_message(user):
            nonlocal success, failed
            try:
                await client.copy_message(
                    chat_id=user["user_id"],
                    from_chat_id=message.chat.id,
                    message_id=message.reply_to_message.message_id
                )
                success += 1
            except Exception as e:
                failed += 1
                logger.error(f"Failed to send message to {user['user_id']}: {str(e)}")

        for idx, user in enumerate(users, start=1):
            tasks.append(asyncio.create_task(send_message(user)))

            if len(tasks) >= batch_size or idx == total_users:
                await asyncio.gather(*tasks)
                tasks = []
                progress = (idx / total_users) * 100
                await status_msg.edit_text(
                    f"📤 Broadcasting...\n\n✅ Successful: {success}\n❌ Failed: {failed}\n📊 Progress: {progress:.1f}%"
                )
                await asyncio.sleep(2)  # Prevent rate limiting

        await status_msg.edit_text(
            f"📤 Broadcast completed!\n\n✅ Successful: {success}\n❌ Failed: {failed}\n👥 Total Users: {total_users}"
        )

    except Exception as e:
        logger.error(f"Error in broadcast command: {str(e)}")
        await message.reply_text("❌ An error occurred during broadcast.")