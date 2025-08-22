import redis.asyncio as redis
import logging

logging.basicConfig(level=logging.INFO)

redis_client: redis.Redis | None=None

def get_redis_client() -> redis.Redis:

    if not redis_client:
        logging.info('Redis_client не инициализирован')

        raise RuntimeError('Redis client is not initializied')
    
    return redis_client