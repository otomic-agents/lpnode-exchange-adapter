interface IAmmConfigData {
  chainDataConfig: {
    chainId: number;
    config: {
      maxSwapNativeTokenValue: string;
      minSwapNativeTokenValue: string;
      minChargeUsdt: string;
    };
  }[];
  bridgeBaseConfig: {
    defaultFee: string;
    enabledHedge: boolean;
    minChargeUsdt: string;
  };
  bridgeConfig: any[]; // 根据具体内容可能需要更详细的类型定义
  orderBookType: string;
  exchangeName: string;
  hedgeConfig: {
    hedgeAccount: string;
    hedgeType: string;
    accountList: {
      enablePrivateStream: boolean;
      apiType: string;
      accountId: string;
      exchangeName: string;
      spotAccount: {
        apiKey: string;
        apiSecret: string;
      };
      usdtFutureAccount: {
        apiKey: string;
        apiSecret: string;
      };
      coinFutureAccount: {
        apiKey: string;
        apiSecret: string;
      };
    }[];
  };
}
export {
  IAmmConfigData
}