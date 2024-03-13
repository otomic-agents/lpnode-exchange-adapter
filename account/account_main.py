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

    async def get_spot_balances(self):
        """
        获取现货账户余额
        :return:
        """
        return await self.balance.get_spot_balances()

    async def sync_balance(self):
        """
        同步余额方法，调用 Balance 类的相关方法进行同步操作
        """
        while True:
            await self.balance.update()
            logging.info("10 seconds later, balance will be updated.")
            await asyncio.sleep(10)

    async def main(self):
        try:
            async with create_task_group() as tg:
                tg.start_soon(self.sync_balance)
        except Exception as e:
            logging.error(f"account_main task group error:{e}")
            await anyio.sleep(20)
        logging.info("AccountMain run compelete")
