from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any
import logging
from config import MONGO_URI
import asyncio

logger = logging.getLogger(__name__)

class MongoDB:
    """
    MongoDB client for the Image Compressor Bot.
    Manages connections and provides access to collections.
    """

    def __init__(self):
        try:
            self.client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client.image_compressor
            
            # Collections
            self.users = self.db.users
            self.api_keys = self.db.api_keys
            self.usage_stats = self.db.usage_stats
            self.settings = self.db.settings
            self.logs = self.db.logs
            self.user_logs = self.db.user_logs
            self.api_stats = self.db.api_stats
            
            # Verify connection
            asyncio.get_event_loop().run_until_complete(self.client.server_info())
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    async def init_indexes(self):
        """Initialize database indexes."""
        try:
            await self.users.create_index("user_id", unique=True, background=True)
            await self.api_keys.create_index("user_id", unique=True, background=True)
            await self.usage_stats.create_index([("user_id", 1), ("date", 1)], background=True)
            await self.logs.create_index("timestamp", background=True)
            await self.user_logs.create_index([("user_id", 1), ("timestamp", 1)], background=True)
            await self.api_stats.create_index([("user_id", 1), ("date", 1)], background=True)
            logger.info("All indexes created successfully.")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise

# Initialize MongoDB instance
mongodb = MongoDB()
db = mongodb.db