# Exchange Arbitrage Bot between Binance and The Ocean

A Python implementation of a bot that places trades based on arbitrage opportunities between Binance and The Ocean. 
This program is meant to accompany [Lesson 3: Introduction to Arbitration Strategies](https://medium.com/the-ocean-trade/algorithmic-trading-101-lesson-3-introduction-to-arbitrage-strategies-76e546b99691).

Sample Scenario Functionality:
For a given token pair, if the lowest ask in exchange A is smaller than the highest bid in exchange B, the bot will buy from exchange A and sell to exchange B.

## Installation
To install the bot and its dependencies, navigate to the `ExchangeArbitrageBot` directory (note the capitalizations). Then, enter the following command:
 ```
 pip install .
 ```

Note: Please read the disclaimer, associated read me files and explanation of methods before running the bot.

To run the Arbitrage Bot, navigate to the `exchangearbitragebot` directory and enter the following command:
```
 python exchange_arbitrage.py
```

## Requirements
- Web3 Provider (such as Parity) is needed
- Required environment variables
 - OCEAN_API_KEY
 - OCEAN_API_SECRET
 - ETHEREUM_ADDRESS 
 - BINANCE_API_KEY
 - BINANCE_API_SECRET

## Explanation of Methods and Definitions (mini Wiki)
 - [Explanation of exchange_arbitrage.py](../master/exchangearbitragebot/exchange_arbitrage_README.md)
 - [Explanation of theocean.py](../master/exchangearbitragebot/exchanges/theocean_README.md)

## DISCLAIMER
#### USE THE PROGRAM AT YOUR OWN RISK. YOU ARE RESPONSIBLE FOR YOUR OWN MONEY. 
#### IN NO EVENT SHALL THE AUTHORS OR THEIR AFFILIATES BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE PROGRAM OR THE USE OR OTHER DEALINGS IN THE PROGRAM.

