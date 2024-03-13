import json
import logging


class Order:
    def __init__(self, exchange):
        self.exchange = exchange

    def __str__(self):
        return f"Order ID: {self.order_id}, Product Info: {self.product_info}, Amount: {self.amount}"

    async def createMarketOrder(self, request):
        logging.info("simulationCreateMarketOrder")
        post_body = await request.json()
        logging.info("simulationCreateMarketOrder request parse sucess")
        # param_value = data.get('param_name')
        exchange = post_body.get("exchange")
        symbol = post_body.get("market")  # Trading pair
        side = post_body.get("side")
        timestamp = post_body.get("timestamp")
        lost_amount = post_body.get("lostAmount")
        quantity = post_body.get("quantity")
        order_id = post_body.get("clientOrderId")
        order_data = {
            "quantity": quantity,
            "symbol": symbol,
            "order_id": order_id,
            "side": side,
            "timestamp": timestamp,
            "exchange": exchange,
            "lost_amount": lost_amount
        }
        logging.info("simulationCreateMarketOrder sucess")
        print(json.dumps(order_data))
        if side == "BUY":
            ret = await self.createMarketBuyOrder(order_data)
            return ret
        elif side == "SELL":
            ret = await self.createMarketSellOrder(order_data)
            return ret
        else:
            logging.warn(
                'The order side must be provided in the createMarketOrder request.')
        return '{"test":"error"}'

    async def simulationCreateMarketOrder(self, request):
        logging.info("simulationCreateMarketOrder")
        post_body = await request.json()
        logging.info("simulationCreateMarketOrder request parse sucess")
        # param_value = data.get('param_name')
        exchange = post_body.get("exchange")
        symbol = post_body.get("market")  # Trading pair
        side = post_body.get("side")
        timestamp = post_body.get("timestamp")
        lost_amount = post_body.get("lostAmount")
        quantity = post_body.get("quantity")
        order_id = post_body.get("clientOrderId")
        order_data = {
            "quantity": quantity,
            "symbol": symbol,
            "order_id": order_id,
            "side": side,
            "timestamp": timestamp,
            "exchange": exchange,
            "lost_amount": lost_amount
        }
        logging.info("simulationCreateMarketOrder sucess")
        print(json.dumps(order_data))
        if side == "BUY":
            ret = await self.createMarketBuyOrder(order_data)
            return ret
        elif side == "SELL":
            ret = await self.createMarketSellOrder(order_data)
            return ret
        else:
            logging.warn(
                'The order side must be provided in the createMarketOrder request.')
        return '{"test":"error"}'

    async def createMarketBuyOrder(self, order_data):
        logging.info('createMarketBuyOrder')
        exe_result = await self.exchange.createMarketBuyOrder(
            order_data["symbol"], order_data["quantity"], {"clientOrderId": order_data["order_id"]})
        print(exe_result)
        logging.info(json.dumps({
            "title": "createMarketBuyOrder execute complated",
            "execute result": exe_result,
        }))
        return exe_result

    async def createMarketSellOrder(self, order_data):
        logging.info('createMarketSellOrder')
        exe_result = await self.exchange.createMarketSellOrder(
            order_data["symbol"], order_data["quantity"], {"clientOrderId": order_data["order_id"]})
        print(exe_result)
        logging.info(json.dumps({
            "title": "createMarketSellOrder execute complated",
            "execute result": exe_result,
        }))
        return exe_result
