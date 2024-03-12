import redis
import os


class RedisBusClient:
    def __init__(self):
        self.redis_client = None

    def get_redis_client(self):
        if self.redis_client is not None:
            return self.redis_client
        else:
            host = os.environ.get(
                'OBRIDGE_LPNODE_DB_REDIS_MASTER_SERVICE_HOST', '127.0.0.1')
            port = os.environ.get('REDIS_PORT', '6379')
            db = os.environ.get('REDIS_DB', '0')
            password = os.environ.get('REDIS_PASSWORD', None)
            port = int(port)
            db = int(db)
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, password=password)
        return self.redis_client
