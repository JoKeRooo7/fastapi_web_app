import json
import asyncio
import subprocess
from redis.asyncio import Redis
from settings import settings
from typing import Optional
from datetime import datetime, timedelta


class RedisNotRunningError(Exception):
    pass


class RedisService:
    def __init__(self, stop_time=10):
        self._process: Optional[subprocess.Popen] = None
        self._redis = None
        self.stop_time = stop_time

    def start(self) -> None:
        self._process = subprocess.Popen(
            ['redis-server',
                '--bind', settings.REDIS_HOST, 
                '--port', str(settings.REDIS_PORT),
                '--dir', settings.REDIS_PATH, 
                '--dbfilename', 'redis_dumb.rdb'],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
        # stdout, stderr = self._process.communicate()
        # print("Redis stdout:", stdout.decode())
        # print("Redis stderr:", stderr.decode())      

    async def get_client(self) -> None:
        if self._redis is None:
            self._redis = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
        await self._wait_for_redis()
        return self._redis

    async def stop(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None

        if self._process:
            self._process.terminate()
        await asyncio.get_event_loop().run_in_executor(None, self._process.wait)            
        self._process = None

    async def increment_rating_count(self, client_id: str) -> int:
        key = f"ratings:{client_id}:{datetime.today().date()}"
        count = await self._redis.incr(key)
        await self._redis.expire(key, timedelta(hours=settings.TIME_TO_REMOVE_LIMIT))
        return count

    async def get_rating_count(self, client_id: str) -> int:
        key = f"ratings:{client_id}:{datetime.today().date()}"
        count = await self._redis.get(key)
        return int(count) if count else 0
    
    async def clear_all_rating_counts(self) -> None:
        cursor = '0'
        pattern = 'ratings:*'
        while cursor != 0:
            cursor, keys = await self._redis.scan(cursor=cursor, match=pattern)
            if keys:
                await self._redis.delete(*keys)

    async def get_cached_data(self, key: str):
        cached_data = await self._redis.get(key)
        return json.loads(cached_data) if cached_data else None


    async def set_cached_data(self, key: str, data):
        await self._redis.set(key, 
            json.dumps(data), 
            ex=settings.TIME_TO_REMOVE_LIST_CASH)


    async def _is_running(self) -> None:
        if self._redis is None:
            raise RedisNotRunningError("Redis client is not initialized.")
        
        try:
           await self._redis.ping()
        except Exception as e:
            raise RedisNotRunningError("Redis is not running.")
        
    async def _wait_for_redis(self) -> None:
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < self.stop_time:
            try:
                await self._is_running() 
                return
            except RedisNotRunningError:
                await asyncio.sleep(1)  # Ждем 1 секунду перед следующей проверкой

        raise RedisNotRunningError(f"Redis did not start in time ({self.stop_time}sec).")
    