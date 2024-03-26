## Program Functionality
This program is designed to provide order book data and order execution capabilities for Amm applications. It utilizes CCXT to interface with the Cex exchange, thereby facilitating the seamless expansion of Amm functionality to include operations on the Cex exchange. The otmoic-exchange-adapter program encapsulates features such as order book (ws) integration, order management, and balance synchronization.

Note: When enabling the hedging feature for an amm within the otmoic program, you must configure the apiKey and apiSecret for the corresponding exchange account. Additionally, ensure that the account has sufficient balance and that IP authorization has been properly established.

## Main Functions
* Automatically loads tokens configured in the Amm program and retrieves their respective order book data.
* Automatically refreshes the order book list upon changes in tokens.
* Automatically authenticates and authorizes the hedging account specified in the Amm program's configuration.
* Synchronously updates balance information for the hedging account.
* Implements the creation of orders.