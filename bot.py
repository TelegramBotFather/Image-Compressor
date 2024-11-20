import os
import asyncio
import logging
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import tinify
from utils import clean_temp_files, cleanup_old_data
from utils.decorators import rate_limit
from commands import (
    start_command,
    admin_dashboard,
    usage_stats,
    convert_command,
    broadcast_command,
    ban_user,
    unban_user,
    banned_users_list,
    settings_command,
    support_command
)
from config import (
    ERROR_MESSAGES,
    RATE_LIMIT_SECONDS,
    LOG_CHANNEL_ID,
    BOT_VERSION
)
from database.mongodb import db
from handlers.file_handler import FileHandler
from handlers.button_handlers import ButtonHandler
from datetime import datetime
from log_handlers.channel_logger import ChannelLogger
from components.keyboards import Keyboards
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate environment variables
required_vars = [
    "API_ID", 
    "API_HASH", 
    "BOT_TOKEN", 
    "TINIFY_API_KEY", 
    "MONGO_URI", 
    "ADMIN_ID",
    "LOG_CHANNEL_ID"
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize bot
app = Client(
    "image_compressor_bot",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Initialize handlers
file_handler = FileHandler(app)
button_handler = ButtonHandler(app)

# Initialize TinyPNG
tinify.key = os.getenv("TINIFY_API_KEY")

# Initialize scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(cleanup_old_data, 'interval', hours=1)

async def start_bot():
    """Initialize bot and verify configurations."""
    try:
        # Initialize MongoDB indexes
        await db.init_indexes()
        
        # Start the bot
        await app.start()
        
        # Verify log channel
        log_channel_id = os.getenv("LOG_CHANNEL_ID")
        if not log_channel_id.startswith("-100"):
            raise ValueError("LOG_CHANNEL_ID must start with -100")
            
        # Send startup message
        await app.send_message(
            int(log_channel_id),
            f"🟢 Bot Started\nVersion: {BOT_VERSION}\n"
            f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Start scheduler
        scheduler.start()
        
        logger.info("Bot started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise e

# Register command handlers
app.add_handler(MessageHandler(start_command, filters.command("start")))
app.add_handler(MessageHandler(support_command, filters.command("help")))
app.add_handler(MessageHandler(settings_command, filters.command("settings")))
app.add_handler(MessageHandler(convert_command, filters.command("convert")))
app.add_handler(MessageHandler(broadcast_command, filters.command("broadcast")))
app.add_handler(MessageHandler(ban_user, filters.command("ban")))
app.add_handler(MessageHandler(unban_user, filters.command("unban")))
app.add_handler(MessageHandler(banned_users_list, filters.command("banned_users")))
app.add_handler(MessageHandler(admin_dashboard, filters.command("admin")))
app.add_handler(MessageHandler(usage_stats, filters.command("stats")))

# Register message handlers
app.add_handler(MessageHandler(file_handler.handle, filters.photo | filters.document))
app.add_handler(CallbackQueryHandler(button_handler.handle))

if __name__ == "__main__":
    try:
        app.run(start_bot)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")