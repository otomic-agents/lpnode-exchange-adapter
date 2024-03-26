import redis
import os
import anyio
from anyio import create_task_group
import asyncio
import logging


class RedisBusClient:
    def __init__(self):
        self.redis_client = None
        self.redis_pub_sub = None

    async def ping(self):
        while True:
            try:
                if self.redis_client is not None:
                    logging.info("send redis ping ")
                    response = self.redis_client.ping()
                    logging.info("response redis pong")
                if self.redis_pub_sub is not None:
                    logging.info("send pub_sub_redis ping ")
                    response = self.redis_pub_sub.ping()
                    logging.info("response pub_sub_redis pong")
            except:
                logging.error("redis ping error")
            finally:
                await anyio.sleep(10)

    async def get_redis_client(self):
        if self.redis_client is not None:
            return self.redis_client
        else:
            host = os.environ.get(
                "REDIS_HOST", "127.0.0.1"
            )
            port = os.environ.get("REDIS_PORT", "6379")
            db = os.environ.get("REDIS_DB", "0")
            password = os.environ.get("REDIS_PASSWORD", None)
            port = int(port)
            db = int(db)
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                socket_connect_timeout=10,
                retry_on_timeout=True,
            )
            asyncio.get_running_loop().create_task(self.ping())
            logging.info("create redis_client")
        return self.redis_client

    async def get_pub_sub(self, channel):
        if self.redis_pub_sub is not None:
            return self.redis_pub_sub
        else:
            print("current redis client", self.redis_client)
            self.redis_pub_sub = self.redis_client.pubsub()
            self.redis_pub_sub.subscribe(channel)
        return self.redis_pub_sub
