import logging
import json
import time

class DataLoader:
    def __init__(self, amm_mongo_client) -> None:
        self.amm_mongo_client = amm_mongo_client
        self.hedgeConfig = None
        self.ammConfig = None

    def getHedgeConfig(self):
        return self.hedgeConfig
    def get_amm_config(self):
        return self.ammConfig

    def load_amm_cnofig(self):
        logging.info("load_amm_cnofig")
        
        def read_config_from_db():
            db = self.amm_mongo_client[self.amm_mongo_client.db_name]
            collection = db["configResources"]
            documents = collection.find({})
            index = 0
            for document in documents:
                print(index,document)
                configs.append(document["templateResult"])
                print(f"add  ammconfig {print}")
                index = index+1
            return configs
        


        while True:
            configs: list = []
            read_config_from_db()
            if len(configs) > 1:
                logging.error("There should only be one.")
                print(configs)
                time.sleep(5)
                continue
            if len(configs) == 0:
                logging.error("There should only be one. 0")
                time.sleep(5)
                continue
            amm_config_json_str = configs[0]
            if amm_config_json_str=="":
                logging.info("Wait for the AMM configuration to be ready.")
                time.sleep(5)
                continue
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
