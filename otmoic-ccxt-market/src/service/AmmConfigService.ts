import { Service, Autowired, Logger, Component } from 'koatty';
import { TokenDocument } from '../proto/MarketTypes';
import { IAmmConfigData } from '../proto/AmmConfigData';
import MongoDto from '../dto/MongoDto';
@Service()
export class AmmConfigService {
  @Autowired()
  protected mongoDto: MongoDto
  public async readAmmConfigFromDb(): Promise<IAmmConfigData> {
    const configs: string[] = []
    for (; ;) {
      const result = await this.mongoDto.getClient().db(this.mongoDto.conf.db).collection("configResources").find({}).toArray();
      if (result.length !== 1) {
        Logger.info(`There should only be one , number:${result.length}`)
        await new Promise(resolve => setTimeout(resolve, 5000));
        continue;
      }
      for (let i = 0; i < result.length; i++) {
        configs.push(result[i].templateResult)
      }
      const ammConfigStr = configs[0];
      if (ammConfigStr === "") {
        Logger.info(`Wait for the AMM configuration to be ready`)
        await new Promise(resolve => setTimeout(resolve, 5000));
        continue;
      }
      const ammConfig: IAmmConfigData = JSON.parse(ammConfigStr)
      return ammConfig;
    }
  }
}
