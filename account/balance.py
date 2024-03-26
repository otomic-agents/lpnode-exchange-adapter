import logging
import json


class Balance:
    def __init__(self, exchange):
        self.spot_balanace = {}
        self.exchange = exchange

    @property
    def balance(self):
        return self._balance

    async def get_spot_balances(self):
        return self.spot_balanace

    async def update(self):
        skip_key_list = ["info", "free", "used", "total", "timestamp", "datetime"]
        try:
            logging.info("fetchBalance")
            balance_info = await self.exchange.fetchBalance()
            # print(json.dumps(balance_info))
            i = 0
            for key, value in balance_info.items():
                if key in skip_key_list:
                    # logging.info(f"skip key:{skip_key_list}")
                    continue
                i = i + 1
                self.spot_balanace[key] = value
            logging.info(f"Updated balance,assets count:{i}")
        except Exception as e:
            logging.error(f"Error updating balance:{e}")
