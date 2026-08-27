from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
from backend.utils.logger import logger
_client = None
_db = None

async def connect_mongodb():
    global _client, _db
    try:
        _client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        _db = _client[settings.mongodb_db]
        await _client.admin.command('ping')
        await _db.whitelisted_domains.create_index('domain', unique=True)
        await _db.admins.create_index('user_id', unique=True)
        logger.info('MongoDB connected')
        return _db
    except Exception as error:
        logger.warning(f'MongoDB unavailable: {error}')
        _client = _db = None
        return None

def get_mongodb():
    return _db

async def close_mongodb():
    global _client, _db
    if _client:
        _client.close()
    _client = _db = None
