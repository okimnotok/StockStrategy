import time
from datetime import datetime
import json

from broker.base import BrokerExecutor
from common.constants import PATH_PREFIX
from data.datum import DataHandler


ONE_MINUTE = 1
THREE_MINUTE = 3
FIVE_MINUTES = 5
TEN_MINUTES = 10
FIFTEEN_MINUTES = 15
THIRTY_MINUTES = 30
ONE_HOUR = 60
SIZE = [ONE_MINUTE, THREE_MINUTE, FIVE_MINUTES, TEN_MINUTES, FIFTEEN_MINUTES, THIRTY_MINUTES, ONE_HOUR]


class DataExporter:
    def __init__(self, tickers: list[str], broker: BrokerExecutor):
        print('Initializing DataExporter')
        self.tickers = tickers
        self.broker = broker
        self.raw_data = {ticker: [] for ticker in self.tickers}
        self.history_data = {ticker: [] for ticker in self.tickers}
        self.handler = [DataHandler(size) for size in SIZE]
        self.path = ''
        print('Done!!!')

    def reload(self):
        print('Reloading DataExporter')
        self.raw_data = {ticker: [] for ticker in self.tickers}
        self.history_data = {ticker: [] for ticker in self.tickers}
        print('Done!!!')

    def get_data(self):
        for ticker in self.tickers:
            self.raw_data[ticker].append(self.broker.retrieve_current_price(ticker))

    def _get_history_data(self):
        self.history_data = {ticker: [] for ticker in self.tickers}
        for ticker in self.tickers:
            while True:
                try:
                    items = self.broker.retrieve_history_price(ticker)
                    break
                except Exception:
                    time.sleep(30)
            for item in items:
                self.history_data[ticker].append(item)

    def _serialize_data(self, data, index):
        row = []
        for handler in self.handler:
            row.extend(handler.retrieve_current_data(data[:index]))
        return row

    def retrieve_row_data(self, ticker, index):
        return self._serialize_data(self.raw_data[ticker], index)

    def retrieve_history_data(self, ticker, index):
        return self._serialize_data(self.history_data[ticker], index)

    def _update_path(self):
        self.path = f'{PATH_PREFIX}/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}'
        import os
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _save_raw_data(self):
        print(f'saving raw data to {self.path}/raw_data.txt')
        for ticker in self.tickers:
            self.raw_data[ticker] = [datum.__dict__ for datum in self.raw_data[ticker]]
        with open(f'{self.path}/raw_data.txt', 'w') as f:
            f.write(json.dumps(self.raw_data))
        print('Done!!!')

    def _save_training_data(self):
        print('saving training data')
        self._get_history_data()
        training_data = []
        for index in range(len(self.history_data[self.tickers[0]])):
            row = []
            for ticker in self.tickers:
                row.extend(self.retrieve_history_data(ticker, index+1))
            training_data.append(row)

        with open(f'{self.path}/train.txt', 'w') as f:
            f.write(json.dumps(training_data))
        buy_result = []
        sell_result = []
        # 如果当前价格比未来一段时间都低，这个点是买入的好时间
        # 如果这个价格比未来一段时间都高，这个点是卖出的好时间
        raw_data = [datum[0] for datum in training_data]
        for index in range(len(raw_data)):
            # 是不是买在最低点。在未来最高峰前，和最低点的差距。
            local_max = max(raw_data[index:])
            local_max_index = raw_data.index(local_max)
            local_min = min(raw_data[:local_max_index + 1])
            if local_max == local_min:
                buy_result.append(0)
            else:
                buy_result.append(int((local_max - raw_data[index]) / (local_max - local_min) * 100))

            # 是不是卖在最高点，在未来的高峰和当前的高峰比较。和之前的最点点
            local_min = min(raw_data[:index + 1])
            local_min_index = raw_data.index(local_min)
            local_max = max(raw_data[local_min_index:])
            if local_max == local_min:
                sell_result.append(0)
            else:
                sell_result.append(int((raw_data[index] - local_min) / (local_max - local_min) * 100))

        with open(f'{self.path}/buy_result.txt', 'w') as f:
            f.write(json.dumps(buy_result))

        with open(f'{self.path}/sell_result.txt', 'w') as f:
            f.write(json.dumps(sell_result))
        print('Done!!!')

    def save_data(self):
        self._update_path()
        self._save_raw_data()
        self._save_training_data()


if __name__ == '__main__':
    from broker.xueqiu import XueQiuExecutor
    ticker = ['SOXL', 'QQQ', 'SQQQ', 'AAPL', 'NVDA', 'AMD', 'INTC', 'SPY', 'AMZN', 'GOOGL', 'TSLA', 'META']
    broker = XueQiuExecutor()
    exporter = DataExporter(ticker, broker)
    for i in range(10):
        exporter.get_data()
    print(exporter.retrieve_row_data('SOXL', 1))
    print(exporter.retrieve_row_data('SOXL', len(exporter.raw_data)))
    exporter.save_data()
