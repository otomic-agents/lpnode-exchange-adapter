import logging


class Balance:
    def __init__(self, exchange):
        self.spot_balanace = {}
        self.exchange = exchange

    @property
    def balance(self):
        return self._balance

    async def update(self):
        try:
            balance_info = await self.exchange.fetchBalance()
            logging.info("Updating balance")
            info = balance_info.get("info")
            balances = info.get("balances")
            for balance in balances:
                self.spot_balanace[balance["asset"]] = balance
            logging.info(f"Updated balance,assets count:{len(balances)}")
        except:
            logging.error("Error updating balance")
