import pymongo
import os
import logging


class AmmMongoClientFactory:
    def __init__(self):
        self.client = None

    def get_mongo_client(self):
        if self.client is not None:
            return self.client
        else:
            # update the default values of environment variables
            host = os.environ.get("MONGODB_HOST", "localhost")
            port = os.environ.get("MONGODB_PORT", "27017")
            user = os.environ.get("MONGODB_ACCOUNT", "readWriteAnyDb")
            password = os.environ.get("MONGODB_PASS", "readWriteAnyDbpass")
            db = os.environ.get("MONGODB_DBNAME_LP_STORE", "ursa_space")
            auth_db = os.environ.get("MONGODB_DBNAME_LP_STORE", "ursa_space")

            # build connection string and create client
            connection_string = (
                f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource={auth_db}"
            )
            logging.info(connection_string)
            self.client = pymongo.MongoClient(connection_string)
            self.client.db_name = db
        return self.client
