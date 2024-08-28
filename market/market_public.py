import asyncio
import logging

class MarketPublic:
    def __init__(self, exchange):
        self.exchange = exchange

    async def fetchMarkets(self):
        try:
            market = self.exchange.markets
            # logging.info(markets)
            filtered_market = {key: value for key, value in market.items() if value["quote"] in ["USDT", "USDC"]}
            # usdt_usdc_markets = [market for market in markets if market['quote'] == 'USDT' or market['quote'] == 'USDC']
            filtered_values = [value for value in filtered_market.values()]
            return filtered_values
        except Exception as e:
            print(e)
        

    def set_exchange(self, exchange):
        self.exchange = exchange

    async def hasMarkets(self, request):
        query_params = request.query
        market = query_params.get("market", None)
        if market is None:
            return False
        markets = await self.exchange.fetchMarkets()
        for symbol in markets:
            print(f'find ..{symbol.get("base")}')
            if symbol.get("base") == market:
                return True
        return False
