import pymongo
import os


class AmmMongoClientFactory:
    def __init__(self):
        self.client = None

    def get_mongo_client(self):
        if self.client is not None:
            return self.client
        else:
            # 更新环境变量的默认值
            host = os.environ.get('LP_NODE_DATA_MONGO_URL', 'localhost')
            port = os.environ.get('MONGODB_PORT', '27017')
            user = os.environ.get('MONGODB_ACCOUNT', 'readWriteAnyDb')
            password = os.environ.get('MONGODBPASS', 'readWriteAnyDbpass')
            db = os.environ.get('MONGODB_DBNAME_LP_STORE', 'ursa_space')
            auth_db = os.environ.get('MONGODB_DBNAME_LP_STORE', 'ursa_space')

            # 构建连接字符串并创建客户端
            connection_string = f'mongodb://{user}:{password}@{
                host}:{port}/{db}?authSource={auth_db}'
            self.client = pymongo.MongoClient(connection_string)
            self.client.db_name = db
        return self.client
