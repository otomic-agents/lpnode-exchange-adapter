from aiohttp import web
import logging
from rpc_service import RpcService

class HttpServer:
    def __init__(self, market, account, market_public,exchange,hedge_account_id):
        self.exchange = exchange;
        self.market = market
        self.account = account
        self.market_public = market_public
        self.app = web.Application()
        self.rpc_service = RpcService(exchange,hedge_account_id)
        self.add_routes()
        
        

    def add_routes(self):
        self.app.add_routes(
            [
                web.get("/api/public/fetchMarkets", self.handle_fetch_markets),
                web.get("/api/public/hasMarket", self.handle_has_market),
                web.get("/api/spotOrderbook", self.handle_spot_orderbook),
                web.get("/api/spotBalances", self.handle_spot_balances),
                web.post('/api/order/createMarketOrder',
                         self.handle_order_create_market_order),
                web.post("/api/order/simulationCreateMarketOrder",
                         self.handle_order_simulation_create_market_order),
                web.post("/jsonrpc", self.handle_jsonrpc),
            ]
        )
        
        # self.app.add_get('/api/spotOrderbook', self.handle_spot_orderbook)
    async def handle_jsonrpc(self, request):
        try:
            request_data = await request.json()
            
            if 'jsonrpc' not in request_data or request_data['jsonrpc'] != '2.0':
                raise Exception('Invalid JSON-RPC request')
            
            method_name = request_data.get('method')
            params = request_data.get('params', {})
            request_id = request_data.get('id')

            if not hasattr(self.rpc_service, method_name):
                raise Exception(f'Method {method_name} not found')

            
            method = getattr(self.rpc_service, method_name)
            result = await method(**params)
            
            response = {
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            }
        except Exception as e:
            response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': str(e)
                },
                'id': request_data.get('id')
            }
        return web.json_response(response)
    async def handle_order_simulation_create_market_order(self, request):
        response = {"code": 0}
        try:
            response["result"] = await self.account.order.simulationCreateMarketOrder(request)
        except Exception as e:
            logging.error(e)
            response["code"] = 1
            response["result"] = None
            response["error"] = str(e)
        finally:
            return web.json_response(response)

    async def handle_order_create_market_order(self, request):
        response = {"code": 0}
        try:
            response["result"] = await self.account.order.createMarketOrder(request)
        except Exception as e:
            response["code"] = 1
            response["result"] = None
            response["error"] = str(e)
        finally:
            return web.json_response(response)

    async def handle_fetch_markets(self, request):
        response = {"code": 0}
        try:
            response["markets"] = await self.market_public.fetchMarkets()
        except Exception as e:
            response["code"] = 1
            response["markets"] = None
            response["error"] = str(e)
        finally:
            return web.json_response(response)

    async def handle_has_market(self, request):
        response = {"code": 0}
        try:
            response["markets"] = await self.market_public.hasMarkets(request)
        except Exception as e:
            response["code"] = 1
            response["markets"] = None
            response["error"] = str(e)
        finally:
            return web.json_response(response)

    async def handle_spot_orderbook(self, request):
        logging.info("handle_spot_orderbook")
        orderbook = await self.market.get_spot_orderbook()
        return web.json_response(orderbook)

    async def handle_spot_balances(self, request):
        response = {"code": 0}
        try:
            balances = await self.account.get_spot_balances()
            response["balances"] = balances
        except Exception as e:
            response["code"] = 1
            response["balances"] = None
            response["error"] = str(e)
        finally:
            return web.json_response(response)

    async def run(self, host="127.0.0.1", port=10086):
        logging.info(f"Starting server on {host}:{port}...")
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()
        except KeyboardInterrupt:
            await site.stop()
            await runner.cleanup()
