import logging
import json


class DataLoader:
    def __init__(self, amm_mongo_client) -> None:
        self.amm_mongo_client = amm_mongo_client
        self.hedgeConfig = None
        self.ammConfig = None

    def getHedgeConfig(self):
        return self.hedgeConfig

    def load_amm_cnofig(self):

        db = self.amm_mongo_client[self.amm_mongo_client.db_name]
        collection = db["configResources"]
        documents = collection.find({})
        configs: list = []
        index = 0
        for document in documents:
            configs.append(document["templateResult"])
            print(f"add  ammconfig {print}")
            index = index+1

        if len(configs) > 1:
            logging.error("There should only be one.")
        amm_config = json.loads(configs[0])
        print(json.dumps(amm_config, indent=4))
        self.hedgeConfig = amm_config['hedgeConfig']
        self.ammConfig = amm_config
        logging.info("load_amm_cnofig sucessed")
        return self.ammConfig

    def getAccountConfigByHedgeConfig(self, hedge_config):
        hedge_account = hedge_config["hedgeAccount"]
        hedge_account_list = hedge_config['accountList']
        logging.info(f"cur hedge account is:{hedge_account}")
        for account in hedge_account_list:
            if account["accountId"] == hedge_account:
                return account
        return None
