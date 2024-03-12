from aiohttp import web


class HttpServer:
    def __init__(self, market, account):
        self.market = market
        self.account = account
        self.app = web.Application()
        self.add_routes()

    def add_routes(self):
        self.app.add_routes(
            [
                web.get('/api/spotOrderbook', self.handle_spot_orderbook),
                web.get('/api/spotBalances', self.handle_spot_balances)
            ])
        # self.app.add_get('/api/spotOrderbook', self.handle_spot_orderbook)

    async def handle_spot_orderbook(self, request):
        orderbook = await self.market.get_spot_orderbook()
        return web.json_response(orderbook)

    async def handle_spot_balances(self, request):
        balances = await self.account.get_spot_balances()
        return web.json_response(balances)

    async def run(self, host='127.0.0.1', port=10086):
        print(f"Starting server on {host}:{port}...")
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()
        except KeyboardInterrupt:
            await site.stop()
            await runner.cleanup()
