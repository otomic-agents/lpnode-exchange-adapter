import { MongoClient, ServerApiVersion } from "mongodb";
import { Config, Component, Logger } from "koatty";

@Component()
export default class MongoDto {
  @Config("MongoStore", "db")
  public conf: {
    host: string,
    user: string,
    password: string,
    port: string,
    db: string
  };

  private readonly mongoClient: MongoClient;
  private hasDisconnected: boolean = false;

  constructor() {
    this.mongoClient = this.createClient();
    this.connect();
  }

  private createClient(): MongoClient {
    const uri = `mongodb://${this.conf.user}:${this.conf.password}@${this.conf.host}:${this.conf.port}/${this.conf.db}?authSource=${this.conf.db}`;
    Logger.info(uri);

    return new MongoClient(uri, {
      serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
      },
      retryWrites: true,
      retryReads: true,
      connectTimeoutMS: 30000,
      socketTimeoutMS: 45000,
      maxPoolSize: 10,
      minPoolSize: 0,
      maxIdleTimeMS: 120000,
      waitQueueTimeoutMS: 10000,
    });
  }

  private async connect() {
    try {
      this.mongoClient.on('serverHeartbeatFailed', (event) => {
        if (!this.hasDisconnected) {
          Logger.warn('MongoDB connection lost, attempting to reconnect...', event);
          this.hasDisconnected = true;
        }
      });

      this.mongoClient.on('serverHeartbeatSucceeded', () => {
        if (this.hasDisconnected) {
          Logger.info('MongoDB reconnection successful');
          this.hasDisconnected = false;
        }
      });

      await this.mongoClient.connect();
      Logger.info("Connected successfully to MongoDB");
      const healthResult = await this.healthCheck();
      if (!healthResult) {
        Logger.error("❌ MongoDB health check failed after successful connection. The program will exit.");
        console.log('⚠️ Initialization failed: MongoDB connection is unstable. The program will exit.');
        await new Promise(resolve => setTimeout(resolve, 10000));
        process.exit(1);
      }
    } catch (e) {
      Logger.error("Failed to connect to MongoDB during initialization. The program will exit.", e);
      console.log('⚠️ Initialization failed: Could not connect to MongoDB. The program will exit.');
      await new Promise(resolve => setTimeout(resolve, 10000));
      process.exit(1);
    }
  }
  async healthCheck(): Promise<boolean> {
    try {
      const result = await this.mongoClient.db().command({ ping: 1 });

      if (result?.ok === 1) {
        Logger.log('✅ MongoDB health check passed - Connection is healthy');
        return true;
      } else {
        Logger.warn('⚠️ MongoDB health check returned unexpected status:', result);
        return false;
      }
    } catch (error) {
      Logger.error('❌ MongoDB health check failed:', {
        error: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString(),
      });
      return false;
    }
  }

  public getClient(): MongoClient {
    return this.mongoClient;
  }
}
