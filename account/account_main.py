import asyncio
from anyio import create_task_group
from account.balance import Balance
from account.order import Order
import logging


class AccountMain:
    def __init__(self, exchange) -> None:
        self.exchange = exchange
        self.balance = Balance(exchange)
        pass

    async def get_spot_balance(self):
        """
        获取现货账户余额
        :return:
        """
        return {"ETH": {"free": 100}}
        pass

    async def sync_balance(self):
        """
        同步余额方法，调用 Balance 类的相关方法进行同步操作
        """
        while True:
            await self.balance.update()
            await asyncio.sleep(10)

    async def main(self):
        async with create_task_group() as tg:
            tg.start_soon(self.sync_balance)
        logging.info("AccountMain run compelete")
