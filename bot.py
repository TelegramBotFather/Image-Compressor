import os
import asyncio
import logging
from pyrogram import Client, filters, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import tinify
from utils import clean_temp_files, cleanup_old_data
from utils.decorators import rate_limit
from api_management.api_handler import APIHandler
from api_management import APISettings
from commands import (
    start_command,
    admin_dashboard,
    usage_stats,
    broadcast_command,
    ban_user,
    unban_user,
    banned_users_list,
    support_command
)
from config import (
    ERROR_MESSAGES,
    RATE_LIMIT_SECONDS,
    LOG_CHANNEL_ID,
    BOT_VERSION
)
from database.mongodb import mongodb, db
from handlers.file_handler import FileHandler
from handlers.button_handlers import ButtonHandler
from handlers.url_handler import URLHandler
from datetime import datetime
from log_handlers.channel_logger import ChannelLogger
from components.keyboards import Keyboards
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.enums import ParseMode

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

if not os.path.exists('temp'):
    os.makedirs('temp')

async def start_bot():
    """Initialize bot and verify configurations."""
    try:
        # Initialize MongoDB indexes
        await mongodb.init_indexes()
        
        # Start the bot
        await app.start()
        
        # Register handlers
        app.add_handler(MessageHandler(start_command, filters.command("start")))
        app.add_handler(MessageHandler(broadcast_command, filters.command("broadcast")))
        app.add_handler(MessageHandler(ban_user, filters.command("ban")))
        app.add_handler(MessageHandler(unban_user, filters.command("unban")))
        app.add_handler(MessageHandler(banned_users_list, filters.command("banned_users")))
        app.add_handler(MessageHandler(admin_dashboard, filters.command("admin")))
        app.add_handler(MessageHandler(usage_stats, filters.command("stats")))
        app.add_handler(MessageHandler(file_handler.handle, filters.photo | filters.document))
        app.add_handler(CallbackQueryHandler(button_handler.handle))
        app.add_handler(MessageHandler(url_handler.handle, filters.regex(r'https?://[^\s]+')))
        app.add_handler(MessageHandler(support_command, filters.command("support")))

        # Initialize scheduler
        scheduler = AsyncIOScheduler()
        scheduler.add_job(cleanup_old_data, 'interval', hours=1)
        # Add temp files cleanup job
        scheduler.add_job(clean_temp_files, 'interval', hours=2, args=[["temp"]])
        
        # Start scheduler
        scheduler.start()
        
        # Send startup message
        await app.send_message(
            LOG_CHANNEL_ID,
            f"🟢 Bot Started\nVersion: {BOT_VERSION}\n"
            f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode=ParseMode.HTML
        )
        
        logger.info("Bot started successfully!")
        
        # Keep the bot running
        await idle()
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise
    finally:
        await app.stop()

if __name__ == "__main__":
    try:
        app = Client(
            "image_compressor_bot",
            api_id=os.getenv("API_ID"),
            api_hash=os.getenv("API_HASH"),
            bot_token=os.getenv("BOT_TOKEN")
        )
        
        # Initialize handlers and components
        api_settings = APISettings(app)
        file_handler = FileHandler(app)
        button_handler = ButtonHandler(app, api_settings)
        url_handler = URLHandler(app)
        
        # Run the bot properly
        asyncio.run(start_bot())
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")