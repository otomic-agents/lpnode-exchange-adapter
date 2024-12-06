import { Service, Autowired, Logger, Component } from 'koatty';
import { RedisDto } from '../dto/RedisDto';
@Service()
export class RedisStoreService {
  @Autowired()
  protected redisDto: RedisDto
  public async save(exchangeName: string, symbol: string, orderbookString: string) {
    const key = `${exchangeName.toUpperCase()}_${symbol}`
    await this.redisDto.redisIns.setex(symbol, 60, orderbookString)
  }
  public async saveSymbols(symbols: string[]) {
    const key = `LP_MARKET_SYMBOLS`;
    await this.redisDto.redisIns.set(key, JSON.stringify(symbols));
  }
}