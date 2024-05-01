import json

from math import floor

from common.constants import PATH_PREFIX
from broker.base import BrokerExecutor


class TickerTrade:
    def __init__(self, ticker: str, broker: BrokerExecutor):
        self.ticker = ticker
        self.remaining_money = 0
        self.ticker_number = 0
        self.prices = []
        self.portfolio = 0
        self.broker = broker

    def reload(self):
        with open(f'{PATH_PREFIX}/{self.ticker.lower()}_account_data.json', 'r') as f:
            data = json.loads(f.read())
        self.remaining_money = data.get('remaining_money')
        self.ticker_number = data.get('ticker_number')
        self.prices = data.get('prices')

    def save(self):
        datum = broker.retrieve_current_price(self.ticker)
        with open(f'{PATH_PREFIX}/{self.ticker.lower()}_account_data.json', 'w') as f:
            f.write(json.dumps({
                'remaining_money': self.remaining_money, 'ticker_number': self.ticker_number,
                'prices': self.prices[-1], 'portfolio': self.remaining_money + self.ticker_number * datum.current
            }))

    def buy(self, price):
        quantity = int(floor(self.remaining_money / price))
        self.broker.buy_with_limit(self.ticker, quantity, price)
        self.prices.append(('buy', price))
        self.ticker_number += quantity
        self.remaining_money -= price * quantity

    def sell(self, price):
        self.broker.sell_with_limit(self.ticker, self.ticker_number, price)
        self.prices.append(('sell', price))
        self.remaining_money += price * self.ticker_number
        self.ticker_number = 0

    def __str__(self):
        return f'{self.ticker}: {self.ticker_number}, {self.remaining_money}'


class TickersTrade:
    def __init__(self, tickers: list, broker: BrokerExecutor):
        self.tickers = {ticker: TickerTrade(ticker, broker) for ticker in tickers}

    def reload(self):
        for _, trade in self.tickers.items():
            trade.reload()

    def buy(self, ticker, price):
        self.tickers[ticker].buy(price)

    def sell(self, ticker, price):
        self.tickers[ticker].sell(price)

    def save(self):
        for _, trade in self.tickers.items():
            trade.save()


if __name__ == '__main__':
    from broker.xueqiu import XueQiuExecutor
    broker = XueQiuExecutor()
    tickers = ['SOXL', 'AAPL']
    tickers_trade = TickersTrade(tickers, broker)
    tickers_trade.reload()

    actions = [('buy', 'SOXL', 33.0), ('buy', 'AAPL', 120.3), ('sell', 'SOXL', 36.0), ('sell', 'AAPL', 130)]
    for action, ticker, price in actions:
        if action == 'buy':
            tickers_trade.buy(ticker, price)
            print(tickers_trade.tickers[ticker])
        elif action == 'sell':
            tickers_trade.sell(ticker, price)
            print(tickers_trade.tickers[ticker])
    for ticker in tickers:
        print(tickers_trade.tickers[ticker])
    tickers_trade.save()
