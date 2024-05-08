import asyncio


class MarketPublic:
    def __init__(self, exchange):
        self.exchange = exchange

    async def fetchMarkets(self):
        markets = await self.exchange.fetchMarkets()
        return markets

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
