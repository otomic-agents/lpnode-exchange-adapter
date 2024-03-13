#!/usr/bin/env python3
import os
import sys
import asyncio
from database.bus_redis_client import RedisBusClient
import json
import logging
import ccxt.pro as ccxt
import anyio
from anyio import create_task_group, run
from market.market_main import Market
from market.market_public import MarketPublic
from account.account_main import AccountMain
from httpd import HttpServer
from database.amm_mongo_client_fectory import AmmMongoClientFactory
import psutil
from datetime import datetime
from data_loader.data_loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:T+%(relativeCreated)d  %(levelname)s [%(pathname)s:%(lineno)d in "
    "function %(funcName)s] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)


class Application:
    def __init__(self):
        self.exchange_name = None
        self.exchange = None
        self.amm_mongo_client = None
        self.market = None
        self.account = None
        self.market_public = None

    async def init(self):
        try:
            self.amm_mongo_client = AmmMongoClientFactory().get_mongo_client()
            self.data_loader = DataLoader(self.amm_mongo_client)
            self.data_loader.load_amm_cnofig()
            # init exchange and load account config
            self.exchange = await self.create_exchange()

            self.redis_bus_client = RedisBusClient().get_redis_client()
            self.market = Market(
                self.exchange, self.redis_bus_client, self.amm_mongo_client
            )
            self.market_public = MarketPublic(self.exchange)
            self.account = AccountMain(self.exchange)
        except Exception as e:
            print("init error", e)

    async def report_status(self):
        while True:
            try:
                status_key = os.environ.get("STATUS_KEY")
                if status_key == None:
                    await anyio.sleep(20)
                    continue
                logging.info(f"set status info to redis key:{status_key}")
                orderbook_data_ret = await self.market.get_spot_orderbook()
                orderbook_data = orderbook_data_ret.get("data")
                now = datetime.now()
                formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
                orderbook_data["last_update_time"] = formatted_now
                self.redis_bus_client.set(
                    status_key, json.dumps(orderbook_data))
            except Exception as e:
                logging.info(f"error to set status:{e}")
            finally:
                await anyio.sleep(10)

    async def start_tasks(self):
        try:
            async with create_task_group() as tg:
                tg.start_soon(self.market.main)
                tg.start_soon(self.account.main)
                tg.start_soon(self.print_cpu_usage)
                tg.start_soon(self.report_status)
                tg.start_soon(self.run_httpd)
        except Exception as e:
            for e_item in e.exceptions:
                print(e_item)
            print("start_task_error", e)

    async def run_httpd(self):
        logging.info('The HTTP service will start in 2 seconds.')
        await asyncio.sleep(2)
        port = os.environ.get("SERVICE_PORT", "18080")
        await HttpServer(self.market, self.account, self.market_public).run(
            "0.0.0.0", port
        )

    async def create_exchange(self):
        print(self.data_loader.getHedgeConfig())
        hedge_config = self.data_loader.getHedgeConfig()
        hedge_account = self.data_loader.getAccountConfigByHedgeConfig(
            hedge_config)
        if hedge_account == None:
            logging.error("not found hedgeconfig account")
            sys.exit()
        # sys.exit()
        hedge_account_api_key = hedge_account["spotAccount"]["apiKey"]
        hedge_account_api_secret = hedge_account["spotAccount"]["apiSecret"]
        hedgeExchange = hedge_account["exchangeName"]
        logging.info(f"exchange name :{hedgeExchange}")
        self.exchange_name = hedgeExchange
        exchange_config = load_exchange_config(self.exchange_name)

        exchange_class = getattr(ccxt, self.exchange_name)
        has_sandbox = exchange_config.get("hasSandbox", False)
        exchange = exchange_class(
            {
                "type": exchange_config.get("type", "spot"),
            }
        )
        logging.info(f"cur exchange:{self.exchange_name}")
        if has_sandbox:
            logging.info("set type as sandbox")
            exchange.setSandboxMode(True)  # enable sandbox mode
        exchange.apiKey = hedge_account_api_key
        logging.info(f"exchange.apiKey: {exchange.apiKey}")
        exchange.secret = hedge_account_api_secret
        logging.info(f"exchange.secret: {exchange.secret}")
        exchange.exchange_config = exchange_config
        return exchange

    @staticmethod
    async def print_cpu_usage():
        while True:
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            print(f"cpu: {cpu_percent}%")
            print(f"memory: {memory_mb:.2f} MB")
            await asyncio.sleep(10)

    async def run(self):
        try:
            await self.init()
            await self.start_tasks()
            print("All tasks finished!")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print("主程序退出..")


def load_exchange_config(exchange_name):
    with open("exchange_config.json", "r") as file:
        config = json.load(file)
        return config.get(exchange_name, {})


if __name__ == "__main__":
    app = Application()
    run(app.run)
