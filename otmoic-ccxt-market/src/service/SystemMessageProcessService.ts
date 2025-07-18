import { Service, Autowired, Logger, Component } from 'koatty';
import { RedisDto } from '../dto/RedisDto';

@Service()
export class SystemMessageProcessService {
  @Autowired()
  protected redisDto: RedisDto
  public async startListen() {
    let subClient 
    try {
      subClient = await this.redisDto.getNewIns();
      await new Promise(resolve => setTimeout(resolve, 3000));
    } catch (e) {
      process.exit(1);
    }
    
    subClient.subscribe("LP_SYSTEM_Notice");
    subClient.on("message", (channel: string, message: string) => {
      const msg = JSON.parse(message);
      Logger.info(`📬 Received message: ${JSON.stringify(msg)}`);

      switch (msg.type) {
        case "configResourceUpdate":
          Logger.info("🔄 Preparing to exit due to config resource update...");
          setTimeout(() => {
            Logger.info("🚪 Exiting due to config resource update.");
            process.exit();
          }, 3000);
          break;
        case "tokenCreate":
          Logger.info("🆕 Preparing to exit due to token creation...");
          setTimeout(() => {
            Logger.info("🚪 Exiting due to token creation.");
            process.exit();
          }, 3000);
          break;
        case "tokenDelete":
          Logger.info("🗑️ Preparing to exit due to token deletion...");
          setTimeout(() => {
            Logger.info("🚪 Exiting due to token deletion.");
            process.exit();
          }, 3000);
          break;
        default:
          Logger.info(`❓ Unhandled message type: ${msg.type}`);
      }
    });
  }
}