from datetime import datetime
from multiprocessing import JoinableQueue, Process
import pytz
import threading
import time

from data.exporter import DataExporter
from strategy.neutral_network import BaseNetwork

market_status = False


class BaseController:
    def __init__(self, exporter: DataExporter, model: BaseNetwork, in_queue: JoinableQueue, out_queue: JoinableQueue):
        self.exporter = exporter
        self.model = model
        self.in_queue = in_queue
        self.out_queue = out_queue

    def close_market(self):
        pass

    def open_market(self):
        pass

    def do_buy(self, data):
        return True

    def do_sell(self, data):
        return True

    def retrieve_data(self, ticker):
        return []

    def entry(self):
        while True:
            if not self.in_queue.empty():
                message = self.in_queue.get_nowait()
                action = message.get('action')
                if action == 'close_market':
                    self.close_market()
                elif action == 'open_market':
                    t = threading.Thread(target=self.open_market, daemon=True)
                    t.start()
                elif action == 'retrieve_data':
                    row = []
                    for ticker in self.exporter.tickers:
                        row.extend(self.retrieve_data(ticker))
                    self.out_queue.put(row)
                elif action == 'do_buy':
                    datum = message.get('datum')
                    self.out_queue.put(self.do_buy(datum))
                elif action == 'do_sell':
                    datum = message.get('datum')
                    self.out_queue.put(self.do_sell(datum))


class Controller(BaseController):
    def __init__(self, exporter: DataExporter, model: BaseNetwork, in_queue: JoinableQueue, out_queue: JoinableQueue):
        print('Initializing Controller')
        super().__init__(exporter, model, in_queue, out_queue)
        print('Done!!!')

    def close_market(self):
        global market_status
        market_status = False
        from broker.pretend import PretendExecutor
        self.exporter.save_data()
        self.model.all_train()
        self.model.save()

    def open_market(self):
        self.model.reload()
        self.exporter.reload()
        global market_status
        market_status = True
        while market_status:
            start_time = time.time()
            self.exporter.get_data()
            end_time = time.time()
            time.sleep(30 - end_time + start_time)

    def retrieve_data(self, ticker):
        return self.exporter.retrieve_row_data(ticker, len(self.exporter.raw_data[ticker]))

    def do_buy(self, datum):
        return self.model.buy(datum)

    def do_sell(self, datum):
        return self.model.sell(datum)


if __name__ == '__main__':
    from broker.xueqiu import XueQiuExecutor
    from data.exporter import DataExporter
    from strategy.neutral_network import NeutralNetwork
    ticker_list = ['SOXL', 'QQQ', 'SQQQ', 'AAPL', 'NVDA', 'AMD', 'INTC', 'SPY', 'AMZN', 'GOOGL', 'TSLA', 'META']
    broker = XueQiuExecutor()
    exporter = DataExporter(broker=broker, tickers=ticker_list)
    model = NeutralNetwork()
    input_queue = JoinableQueue()
    output_queue = JoinableQueue()
    controller = Controller(exporter=exporter, model=model, in_queue=input_queue, out_queue=output_queue)

    process = Process(target=controller.entry)
    process.start()

    action_list = ['open_market', 'retrieve_data', 'retrieve_data', 'do_buy', 'retrieve_data', 'do_sell', 'close_market']
    message = {
        'action': '',
        'datum': []
    }
    for action in action_list:
        print(action)
        message['action'] = action
        input_queue.put(message)
        if action in ['retrieve_data', 'do_buy', 'do_sell']:
            while output_queue.empty():
                continue
            datum = output_queue.get()
            print(len(datum))
            message['datum'] = datum
        time.sleep(2)
