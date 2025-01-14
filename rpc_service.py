import logging
import json

class RpcService:
    def __init__(self, exchange, hedge_account_id):
        self.exchange = exchange
        self.hedge_account_id = hedge_account_id
        
        logging.info(f"🚀 ==========================================")
        logging.info(f"🔑 Starting service with Account ID: {self.hedge_account_id} (Type: {type(self.hedge_account_id).__name__})")
        logging.info(f"🚀 ==========================================")


    async def isHedgingEnabled(self) -> bool:
       return bool(self.hedge_account_id and self.hedge_account_id.strip())

       
    async def fetchBalance(self):
        try:
            exchange_result = await self.exchange.fetch_balance()
            return {
                "accountId": self.hedge_account_id,
                "exchangeResult": exchange_result
            }
        except Exception as e:
            logging.error(f"❌ Error fetching balance for account {self.hedge_account_id}: {str(e)}")
            raise