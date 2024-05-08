import asyncio
from anyio import create_task_group
from account.balance import Balance
from account.order import Order
import logging
import anyio


class AccountMain:
    def __init__(self, exchange) -> None:
        self.exchange = exchange
        self.balance = Balance(exchange)
        self.order = Order(exchange)
        pass

    def set_exchange(self, exchange):
        self.exchange = exchange

    async def get_spot_balances(self):
        """
        get spot account balance
        :return:
        """
        return await self.balance.get_spot_balances()

    async def sync_balance(self):
        """
        synchronize balance method, call relevant methods of the Balance class for synchronization
        """
        try:
            while True:
                if self.exchange.apiKey == None or self.exchange.apiKey == "":
                    logging.warning("No account has been initialized.")
                    await anyio.sleep(10)
                    continue
                await self.balance.update()
                # logging.info("10 seconds later, balance will be updated.")
                await asyncio.sleep(10)
        except Exception as e:
            raise e

    async def main(self):
        try:
            async with create_task_group() as tg:
                tg.start_soon(self.sync_balance)
        except Exception as e:
            logging.error(f"account_main task group error:{e}")
            await anyio.sleep(20)
        logging.info("AccountMain run compelete")
