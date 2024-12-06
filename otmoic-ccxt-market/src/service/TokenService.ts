import { Service, Autowired, Logger, Component } from 'koatty';
import { TokenDocument } from '../proto/MarketTypes';
import MongoDto from '../dto/MongoDto';
@Service()
export class TokenService {
  @Autowired()
  protected mongoDto: MongoDto
  async loadChainListTokens(): Promise<string[]> {
    const db = this.mongoDto.getClient().db(this.mongoDto.conf.db);
    const collection = db.collection("chainList");
    const documents = await collection.find({}, { projection: { tokenName: 1 } }).toArray();
    Logger.info("find all chainlist token");

    const tokenList: string[] = documents.map(document => `${document.tokenName}/USDT`);
    return tokenList;
  }
  async loadBridgeTokens(): Promise<string[]> {
    const db = this.mongoDto.getClient().db(this.mongoDto.conf.db);
    const collection = db.collection("tokens");
    const pipeline = [
      {
        $match: {
          coinType: { $in: ["coin", "stable_coin"] }
        }
      },
      {
        $group: {
          _id: "$marketName",
          tokenAddress: { $addToSet: "$marketName" },
          tokenAddressStr: { $first: "$address" },
          marketName: { $first: "$marketName" }
        }
      }
    ];

    const tokenSet = new Set<string>();

    try {
      const cursor = collection.aggregate<TokenDocument>(pipeline);
      Logger.info(`load_bridge_tokens ${JSON.stringify(pipeline)}`);

      await cursor.forEach((doc) => {
        const marketNameUsdt = `${doc._id}/USDT`;
        if (marketNameUsdt !== "USDT/USDT") {
          tokenSet.add(marketNameUsdt);
        }
      });
    } catch (error) {
      Logger.error(`Error loading bridge tokens: ${error}`);
      throw error;
    }

    return Array.from(tokenSet);
  }

}