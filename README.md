# Trading Bot with Python and Bybit API

### Project Structure
The project consists of three main folders:

- Backtestings: Contains scripts for backtesting trading strategies.
- Csv: Contains historical price data in CSV format.
- Bots: Contains the trading bot scripts.


In this README file, we will be focusing on the matic.py file located in the Bots folder, which contains the code for a trading bot that trades the MATIC/USDT pair on the Bybit exchange.

#### matic.py 

This is a Python-based trading bot that utilizes the Bybit API to implement a long position strategy for the MATIC/USDT cryptocurrency pair. The bot takes advantage of technical analysis indicators, such as RSI and Stochastic RSI, to make decisions on when to enter and exit the market.

### Requirements
To use this trading bot, you will need the following:

- Python 3.7 or higher
- Bybit API keys
- Python libraries: pandas, numpy, smtplib, email.mime, dotenv, ta
- A Gmail account to send email notifications


### The bot will automatically send email notifications for the following events:

- When a limit order is placed
- When a limit order is activated
- When a position is closed due to reaching the stop-loss or take-profit price
- When a position is closed due to RSI exceeding the exit threshold


### Explanation of the Strategy

The strategy_long function is a trading strategy that implements a long position for the SYMBOL specified in the configuration. The function takes two parameters, qty and open_position (which is optional and defaults to False).

The function starts by calling the get5minutedata function to fetch 5-minute candlestick data for the specified SYMBOL. The apply_technicals function is then called to apply technical indicators (such as RSI, Stochastic Oscillator, and Moving Averages) to the fetched data. The Signals class is then instantiated with the processed data to generate buy/sell signals based on the applied technicals.

If a Buy signal is detected, the function sends an email notification and sets a buyprice_limit price based on the current close price, multiplied by the LIMIT_ORDER constant. The function then sets a take profit (tp) and stop loss (sl) price based on the buyprice_limit multiplied by the REWARD and RISK constants, respectively.

Next, the function sets an expiration time for the order and waits until the expiration time is reached. If the current price falls below the buyprice_limit before the order expiration, the function sends an email notification and sets the open_position parameter to True. If the order expires without being filled, the function sends a notification and sets the open_position parameter to False.

If the open_position parameter is True, the function enters a loop that checks the current price of the SYMBOL every 10 seconds. The current profit, RSI, and other relevant information are then printed to the console. If the price falls below the stop loss price, the position is closed and a notification email is sent. Similarly, if the price reaches the take profit price or the RSI exceeds the RSI_EXIT constant, the position is closed, and a notification email is sent.

The function is called within a while loop to continuously check for new buy/sell signals and execute the trading strategy.

### Disclaimer
Please note that this trading bot is for educational and informational purposes only. It is not intended to be used as a substitute for professional financial advice. Trading cryptocurrencies involves risk and you should consult with a financial advisor before making any investment decisions.