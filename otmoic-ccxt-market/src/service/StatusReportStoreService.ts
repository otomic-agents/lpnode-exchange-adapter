import { Service, Autowired, Logger, Component } from 'koatty';
import { RedisDto } from '../dto/RedisDto';
import * as _ from "lodash"
@Service()
export class StatusReportStoreService {
  @Autowired()
  protected redisDto: RedisDto
  public async save(value: string) {
    const key = _.get(process, "env.STATUS_KEY", "")
    await this.redisDto.redisIns.set(key, value);
  }
}