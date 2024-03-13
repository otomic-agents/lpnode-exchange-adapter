import asyncio


class MarketPublic:
    def __init__(self, exchange):
        self.exchange = exchange

    async def fetchMarkets(self):
        markets = await self.exchange.fetchMarkets()
        return markets
