import asyncio
from anyio import create_task_group
import logging
from bson.son import SON
import time
import datetime
import pytz
import json
import anyio
import sys


def format_timestamp_difference(current_timestamp, orderbook_timestamp):
    """
    update package
    Given two timestamps in milliseconds, calculate and return the time difference
    in the format "* mins ago", "* hours ago", or "* days ago".

    Args:
        current_timestamp (int): Current timestamp in milliseconds.
        orderbook_timestamp (int): Orderbook timestamp in milliseconds.

    Returns:
        str: The time difference represented as "* mins ago", "* hours ago",
              or "* days ago", depending on the duration.
    """
    time_diff_ms = current_timestamp - orderbook_timestamp
    time_diff_secs = time_diff_ms / 1000

    # Calculate time differences in minutes, hours, and days
    time_diff_mins = time_diff_secs / 60
    time_diff_hours = time_diff_mins / 60
    time_diff_days = time_diff_hours / 24

    # Round the values to the nearest integer
    rounded_mins = round(time_diff_mins)
    rounded_hours = round(time_diff_hours)
    rounded_days = round(time_diff_days)

    # Choose the appropriate time unit based on the duration
    if rounded_days >= 1:
        return f"{rounded_days} days ago"
    elif rounded_hours >= 1:
        return f"{rounded_hours} hours ago"
    elif rounded_mins >= 1:
        return f"{rounded_mins} mins ago"
    else:
        return "just now"


class Market:
    def __init__(
        self,
        exchange,
        bus_redis_client=None,
        amm_mongo_client=None,
        bus_sub_pub_redis_client=None,
    ):
        self.exchange = exchange
        self.bus_redis_client = bus_redis_client
        self.bus_sub_pub_redis_client = bus_sub_pub_redis_client
        self.amm_mongo_client = amm_mongo_client
        self.market_symbol_list = []
        self.subscribe_task_group = None
        self.orderbook = {}

    def set_exchange(self, exchange):
        self.exchange = exchange

    def pre_symbol_list(self):
        self.load_chain_list_tokens()
        self.load_bridge_tokens()

    def load_chain_list_tokens(self) -> None:
        db = self.amm_mongo_client[self.amm_mongo_client.db_name]
        collection = db["chainList"]
        documents = collection.find({}, {"tokenName": 1})
        logging.info("find all chanlist token")
        token_list = [
            f"{document['tokenName']}/USDT" for document in documents]
        for token in token_list:
            if token not in self.market_symbol_list:
                logging.info(f"load_chain_list_tokens {token}")
                self.market_symbol_list.append(token)

    def load_bridge_tokens(self) -> None:
        db = self.amm_mongo_client[self.amm_mongo_client.db_name]
        collection = db["tokens"]
        # build aggregated pipeline
        pipeline = [
            SON([("$match", {"coinType": {"$in": ["coin", "stable_coin"]}})]),
            SON(
                [
                    (
                        "$group",
                        {
                            "_id": "$marketName",
                            "tokenAddress": {"$addToSet": "$marketName"},
                            "tokenAddressStr": {"$first": "$address"},
                            "marketName": {"$first": "$marketName"},
                        },
                    )
                ]
            ),
        ]
        cursor = collection.aggregate(pipeline)
        logging.info(f"load_bridge_tokens {cursor}")

        for doc in cursor:
            market_name_usdt = f"{doc['_id']}/USDT"
            if market_name_usdt == "USDT/USDT":
                logging.info(f"skip {market_name_usdt}")
                continue
            if market_name_usdt not in self.market_symbol_list:
                logging.info(f"load_bridge_tokens {market_name_usdt}")
                self.market_symbol_list.append(market_name_usdt)

    async def get_spot_orderbook(self):
        return {"code": 0, "data": self.orderbook}

    async def market_subscribe_main(self):
        logging.info("market_subscribe_main")
        try:
            self.pre_symbol_list()
            print("restart group")
            try:
                async with create_task_group() as tg:
                    self.subscribe_task_group = tg
                    # iterate over all symbols and subscribe to each one individually
                    for symbol in self.market_symbol_list:
                        # start a task for each symbol
                        tg.start_soon(self.subscribe, symbol)
                print(f"{self.exchange.id} market_subscribe_main() finished")
                sys.exit(1)
            except Exception as e:
                print("market_subscribe_main() exception")
                print(e)
                sys.exit(1)
        except Exception as e:
            print("subscribe market has a error:", e)
            sys.exit(1)

    async def listen_message(self):
        # if subscription fails, continue retrying
        while True:
            try:
                logging.info(f"listen_message {self.exchange.id} start")
                while True:
                    message = self.bus_sub_pub_redis_client.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message != None:
                        logging.info(
                            f"listen_message {self.exchange.id} {message}")
                        if message["type"] == "message":
                            msg = json.loads(message["data"].decode("utf-8"))
                            print("msg", "🐟", msg)
                            if msg["type"] == "configResourceUpdate":
                                await anyio.sleep(3)
                                sys.exit()
                            if (
                                msg["type"] == "tokenCreate"
                                or msg["type"] == "tokenDelete"
                            ):
                                sys.exit()
                    await anyio.sleep(0.1)
            except Exception as e:
                logging.error(f"listen_message error:{e}")
            finally:
                logging.info(f"listen_message restart  10 secs")
                await anyio.sleep(10)

    async def subscribeSymbol(self, symbol: str):
        # orderbook = await self.exchange.watchOrderBook(
        #     symbol, self.exchange.exchange_config.get("orderbook")["limit"]
        # )
        loop_count = 0
        lastWatchTimestamp = int(time.time() * 1000)
        while True:
            await anyio.sleep(1)
            logging.info(
                f"exchange create time {self.exchange.exchange_create}")
            # logging.info(f"watch {symbol}")
            loop_count += 1
            if loop_count % 20 == 0 or loop_count == 1:  # 20 seconds watchOrderbook
                logging.info(
                    f"re-watch order book symbol:{symbol},loop_count:{loop_count}")
                await asyncio.wait_for(self.exchange.watchOrderBook(
                    symbol, self.exchange.exchange_config.get("orderbook")[
                        "limit"]
                ), 5.0)
                logging.info(
                    f"re-watch sucess symbol:{symbol},loop_count:{loop_count}")
            if loop_count % 10 == 0:
                logging.info(
                    {
                        "title": "summary",
                        "symbol": symbol,
                        "time": self.exchange.orderbooks[symbol]["datetime"],
                        "timestamp": self.exchange.orderbooks[symbol]["timestamp"],
                    }
                )
            currentTimestamp = int(time.time() * 1000)
            orderbookTimestamp = self.exchange.orderbooks[symbol]["timestamp"]
            if orderbookTimestamp != None:
                if loop_count % 10 == 0:
                    timediff = format_timestamp_difference(
                        currentTimestamp,
                        orderbookTimestamp,
                    )
                    logging.info(
                        f"checking {symbol} timestamp, orderbook age: {timediff}"
                    )
                if currentTimestamp - orderbookTimestamp > 1000 * 60 * 5:
                    logging.error(
                        "orderbook has not been updated for 5 minutes, exit the application")
                    raise ValueError(
                        f"{symbol} Timestamp difference exceeds 5 minutes"
                    )
            # logging.info(f"limit orderbook {symbol}")
            orderbook = self.exchange.orderbooks[symbol].limit()
            # logging.info(f"limit orderbook {symbol} sucess")
            self.updata_orderbook(orderbook)
            if loop_count >= 100:
                loop_count = 0

    async def subscribe(self, symbol: str):
        while True:
            task = None
            try:
                async with create_task_group() as tg:
                    logging.info(f"start {symbol} soon")
                    tg.start_soon(self.subscribeSymbol, symbol)
                logging.warn(f"subscribe exit  {symbol},  continue while loop")
                # continue while loop , if subscribeSymbol exit
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(f"subscribe() exception {symbol}")
                logging.info(
                    f"subscribeSymbol error: {e.message}, error list is:")
                logging.info(e.exceptions)
                logging.info("error list end")
                await asyncio.sleep(3)  # continue while loop

    def updata_orderbook(self, orderbook) -> None:
        symbol = orderbook["symbol"]
        timestamp_seconds = time.time()
        timestamp_milliseconds = int(timestamp_seconds * 1000)
        self.orderbook[symbol] = {
            "stdSymbol": orderbook["symbol"],
            "symbol": symbol.replace("/", ""),
            "lastUpdateId": orderbook["nonce"],
            "timestamp": orderbook["timestamp"],
            "incomingTimestamp": timestamp_milliseconds,
            "stream": "",
            "bids": orderbook["bids"][:5],
            "asks": orderbook["asks"][:5],
        }

    async def report_status(self):
        while True:
            logging.info('report eventloop')
            await asyncio.sleep(60)

    async def main(self):
        try:
            async with create_task_group() as tg:
                # main subscription program
                tg.start_soon(self.market_subscribe_main)
                tg.start_soon(self.listen_message)
                tg.start_soon(self.report_status)
        except Exception as e:
            for exc in e.exceptions:
                print("market_main.py main() error:")
                print(exc)
