
import IoRedis from "ioredis";
import { Config, Component, Logger } from "koatty";
@Component()
export class RedisDto {
  @Config("RedisStore", "db")
  conf: {
    host: string,
    password: string,
    port: string
  };
  public redisIns: IoRedis;
  constructor() {
    this.initRedis().catch((e) => {
      Logger.debug(e)
    })
  }
  public async getNewIns(): Promise<IoRedis> {
    Logger.debug("connect redis server", this.conf.host, this.conf.port)
    const redisClient = new IoRedis({
      host: this.conf.host,
      password: this.conf.password,
      port: parseInt(this.conf.port),
      retryStrategy: () => {
        return 3000
      }
    })
    return redisClient
  }
  private async initRedis() {
    Logger.debug("connect redis server", this.conf.host, this.conf.port)
    this.redisIns = new IoRedis({
      host: this.conf.host,
      password: this.conf.password,
      port: parseInt(this.conf.port),
      retryStrategy: () => {
        return 3000
      }
    })
  }
}