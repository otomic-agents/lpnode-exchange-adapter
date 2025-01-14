import { Service, Autowired, Logger } from 'koatty';
import { App } from '../App';
import MongoDto from '../dto/MongoDto';
import { RedisDto } from '../dto/RedisDto';
import { OrderBook } from 'ccxt/js/src/base/types';
import { Exchange, } from 'ccxt';
import { TokenService } from './TokenService';
import { RedisStoreService } from './RedisStoreService';
import { AmmConfigService } from './AmmConfigService';
import { SystemMessageProcessService } from './SystemMessageProcessService';
import * as _ from "lodash";
import logger from '../utils/Log';
const ccxtpro = require('ccxt').pro
console.log('ccxt version', ccxtpro.version)
console.log('exchanges:', ccxtpro.exchanges)
@Service()
export class InitService {
  private marketSymbolList: Map<string, boolean> = new Map();

  @Autowired()
  protected mongoDto: MongoDto

  @Autowired()
  protected redisDto: RedisDto


  @Autowired()
  protected systemMessageProcessService: SystemMessageProcessService;

  private cexExchange: Exchange = null;

  @Autowired()
  private redisStoreService: RedisStoreService
  @Autowired()
  private tokenService: TokenService;

  @Autowired()
  private ammConfig: AmmConfigService
  app: App;
  public constructor() {
    Logger.info("project started...")
    setTimeout(() => {
      this.start()
    }, 1000 * 3)
  }
  private async start() {
    await this.systemMessageProcessService.startListen()
    await this.createExchange()
    const chainListTokens = await this.tokenService.loadChainListTokens()
    chainListTokens.forEach((symbol) => {
      this.marketSymbolList.set(symbol, true)
    })
    const bridgeListToken = await this.tokenService.loadBridgeTokens()
    bridgeListToken.forEach((symbol) => {
      this.marketSymbolList.set(symbol, true)
    })
    console.log(this.marketSymbolList)
    const keyArray = Array.from(this.marketSymbolList.keys());
    await this.redisStoreService.saveSymbols(keyArray);
    this.marketSymbolList.forEach((value, key) => {
      logger.markAsNewRoot();
      this.subscribe(key).then(() => {
        const logMessage = () => Logger.info(`${key} sub end...🟥`);
        logMessage();
        setInterval(logMessage, 1000 * 60 * 5);
      });
    });
  }
  private async subscribe(symbol: string): Promise<string> {
    for (; ;) {
      try {
        let lastWatchTime = Date.now();
        let lastReportTime = Date.now();
        Logger.info(`Watch ${symbol} Orderbook`)
        await this.cexExchange.watchOrderBook(symbol, 5);
        for (; ;) {
          try {
            const currentTime = Date.now();
            if (currentTime - lastWatchTime >= 60000) {
              logger.info("refresh")
              Logger.info(`Refresh watch ${symbol} Orderbook`)
              await this.cexExchange.watchOrderBook(symbol, 5);
              lastWatchTime = currentTime;
            }

            const orderbook: OrderBook = this.cexExchange.orderbooks[symbol].limit();
            if (currentTime - lastReportTime >= 30000) {
              Logger.info(_.get(orderbook, "symbol"), "bid Price", `$${_.get(orderbook, "bids.0.0")}`, "Time", _.get(orderbook, "datetime"), `diff - 【${currentTime - orderbook.timestamp}ms】`)
              lastReportTime = currentTime;
            }
            this.redisStoreService.save(this.cexExchange.name, symbol, JSON.stringify(orderbook));
            await new Promise(resolve => setTimeout(resolve, 800));
          } catch (e) {
            Logger.error(`🔴 Inner loop error for ${symbol}: ${e}`);
            throw e;
          }
        }
      } catch (e) {
        if (e.toString().includes("does not have market symbol")) {
          Logger.info(`${symbol} Exit`);
          Logger.error(e);
          break;
        }
        Logger.error(`🔴 Outer loop error for ${symbol}: ${e}`);
        Logger.info("⏳ Continue after 5 seconds.");
        await new Promise(resolve => setTimeout(resolve, 1000 * 5));
      }
    }
    return "end"
  }

  private async createExchange() {
    Logger.info("Load amm Config...")
    const config = await this.ammConfig.readAmmConfigFromDb();
    let exchangeName = config.exchangeName;
    const hedgeAccountId = config.hedgeConfig.hedgeAccount;
    Logger.info(`config hedge account id:${hedgeAccountId}`);
    const hedgeAccountAccountList = _.get(config, "hedgeConfig.accountList", []);
    for (const accountItem of hedgeAccountAccountList) {
      Logger.info(`${hedgeAccountId} ===? ${accountItem.accountId}`)
      if (accountItem.accountId === hedgeAccountId) {
        Logger.info("Use the exchange name set in the hedge settings.")
        exchangeName = accountItem.exchangeName;
      }
    }

    Logger.info("Create CexExchange", exchangeName)
    const exchange: Exchange = new ccxtpro[exchangeName]({ newUpdates: false });
    const runEnv = _.get(process, "env.RUN_ENV", "prod");
    const supportsSandbox = typeof exchange.setSandboxMode === 'function';
    if (supportsSandbox && runEnv === "dev") {
      Logger.info(`🏖️  Exchange ${exchangeName} - Sandbox Support: ✅`);
      Logger.info(`🔧 Environment: ${runEnv.toUpperCase()}`);
      exchange.setSandboxMode(true);
      Logger.info(`✨ Successfully enabled sandbox mode for ${exchangeName}`);
    } else {
      if (!supportsSandbox) {
        Logger.warn(`⚠️  ${exchangeName} does not support sandbox mode`);
      }
      Logger.info(`🚀 Running ${exchangeName} in production mode`);
      Logger.info(`🌍 Environment: ${runEnv.toUpperCase()}`);
    }
    this.cexExchange = exchange
  }
}
