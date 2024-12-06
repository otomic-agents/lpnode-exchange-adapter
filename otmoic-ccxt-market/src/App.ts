import { Koatty, Bootstrap, Logger } from "koatty";
import * as path from 'path';
import logger from './utils/Log';
@Bootstrap(() => {
  process.env.UV_THREADPOOL_SIZE = '128';
})
export class App extends Koatty {
  public init() {
    this.rootPath = path.dirname(__dirname);
  }
  public listen() {
    console.log("rewrite listen")
  }
}
