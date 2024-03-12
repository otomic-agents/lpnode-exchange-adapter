#!/usr/bin/env python3
import os
import asyncio
from database.bus_redis_client import RedisBusClient
import json
import logging
import ccxt.pro as ccxt
from anyio import create_task_group, run
from market.market_main import Market
from account.account_main import AccountMain
from httpd import HttpServer
from database.amm_mongo_client_fectory import AmmMongoClientFactory
import psutil

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:T+%(relativeCreated)d  %(levelname)s [%(pathname)s:%(lineno)d in '
                           'function %(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', )


class Application:
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.redis_bus_client = RedisBusClient().get_redis_client()
        self.exchange = None
        self.amm_mongo_client = None
        self.market = None
        self.account = None

    async def init(self):
        self.exchange = await self.create_exchange()
        self.amm_mongo_client = AmmMongoClientFactory().get_mongo_client()
        self.market = Market(
            self.exchange, self.redis_bus_client, self.amm_mongo_client)
        self.account = AccountMain(self.exchange)

    async def start_tasks(self):
        async with create_task_group() as tg:
            tg.start_soon(self.market.main)
            tg.start_soon(self.account.main)
            tg.start_soon(self.print_cpu_usage)
            tg.start_soon(self.run_httpd)

    async def run_httpd(self):
        await asyncio.sleep(5)
        port = os.environ.get('SERVICE_PORT', '18080')
        await HttpServer(self.market, self.account).run('0.0.0.0', port)

    async def create_exchange(self):
        exchange_config = load_exchange_config(self.exchange_name)
        exchange_class = getattr(ccxt, self.exchange_name)
        exchange = exchange_class({
            "type": exchange_config.get('type', 'spot'),
        })
        exchange.setSandboxMode(True)  # enable sandbox mode
        exchange.apiKey = exchange_config.get('apiKey')
        logging.info(f'exchange.apiKey: {exchange.apiKey}')
        exchange.secret = exchange_config.get('secret')
        logging.info(f'exchange.secret: {exchange.secret}')
        return exchange

    @staticmethod
    async def print_cpu_usage():
        while True:
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            print(f"CPU占用率: {cpu_percent}%")
            print(f"内存占用: {memory_mb:.2f} MB")
            await asyncio.sleep(10)

    async def run(self):
        try:
            await self.init()
            await self.start_tasks()
            print('All tasks finished!')
        except Exception as e:
            logging.error(f'An error occurred: {e}')
            print('主程序退出..')


def load_exchange_config(exchange_name):
    with open('exchange_config.json', 'r') as file:
        config = json.load(file)
        return config.get(exchange_name, {})


if __name__ == "__main__":
    app = Application('binance')
    run(app.run)
