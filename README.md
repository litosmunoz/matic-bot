# Trading Bot with Python and Bybit API

### Project Structure
The project consists of three main folders:

- Backtestings: Contains scripts for backtesting trading strategies.
- Csv: Contains historical price data in CSV format.
- Bots: Contains the trading bot scripts.


In this README file, we will be focusing on the matic.py file located in the Bots folder, which contains the code for a trading bot that trades the MATIC/USDT pair on the Bybit exchange.

### matic.py 

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


### Disclaimer
Please note that this trading bot is for educational and informational purposes only. It is not intended to be used as a substitute for professional financial advice. Trading cryptocurrencies involves risk and you should consult with a financial advisor before making any investment decisions.