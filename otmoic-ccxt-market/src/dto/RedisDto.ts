
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
  private readonly HEALTH_CHECK_KEY = 'health:check';
  constructor() {
    Logger.debug("🚀 init Redis ")
    this.initRedis().then(async () => {
      Logger.debug("✅ connect complete");
      const health = await this.healthCheck();
      if (!health) {
        console.log('❌ Initialization failed: healthCheck result false. The program will exit.');
        await new Promise(resolve => setTimeout(resolve, 5000));
        process.exit(1);
      }
    }).catch(async (e) => {
      Logger.debug(e);
      console.log('💥 Initialization failed: Could not connect to Redis. The program will exit.');
      await new Promise(resolve => setTimeout(resolve, 3000));
      process.exit(1);
    });
  }

  async healthCheck(): Promise<boolean> {
    try {
      await this.redisIns.set(this.HEALTH_CHECK_KEY, 'OK');
      const result = await this.redisIns.get(this.HEALTH_CHECK_KEY);
      await this.redisIns.del(this.HEALTH_CHECK_KEY);
      
      if (result === 'OK') {
        Logger.log('✅ Redis health check passed - Connection is healthy');
        return true;
      } else {
        Logger.warn('⚠️ Redis health check returned unexpected value:', result);
        return false;
      }
    } catch (error) {
      Logger.error('❌ Redis health check failed:', {
        error: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });
      return false;
    }
  }
  public async getNewIns(): Promise<IoRedis> {
    return new Promise((resolve, reject) => {
      Logger.debug("connect redis server", this.conf.host, this.conf.port)
      const redisClient = new IoRedis({
        host: this.conf.host,
        password: this.conf.password,
        port: parseInt(this.conf.port),
        retryStrategy: () => {
          return 3000
        }
      })
      redisClient.on("connect", () => {
        resolve(redisClient)
      })
      redisClient.on("error", (error) => {
        Logger.debug("Redis connection error:", error);
        reject(error)
      });
    })

  }
  private async initRedis() {
    return new Promise((resolve, reject) => {
      Logger.debug("connect redis server", this.conf.host, this.conf.port)
      this.redisIns = new IoRedis({
        host: this.conf.host,
        password: this.conf.password,
        port: parseInt(this.conf.port),
        retryStrategy: () => {
          return 3000
        }
      })
      this.redisIns.on('reconnecting', () => {
        Logger.debug("reconnecting")
      })
      this.redisIns.on("error", (error) => {
        Logger.debug("Redis connection error:", error);
        reject(error)
        throw error;
      });
      this.redisIns.on("connect", () => {
        resolve(true)
      })
    })
  }
}