from datetime import datetime
from multiprocessing import JoinableQueue, Process
import pytz
import time

from account.trade import TickersTrade
from broker.xueqiu import XueQiuExecutor
from data.exporter import DataExporter
from strategy.base import Controller
from strategy.neutral_network import NeutralNetwork


def base_send(message: dict, input_queue: JoinableQueue):
    input_queue.put(message)


def open_market(message: dict, input_queue: JoinableQueue):
    message['action'] = 'open_market'
    base_send(message, input_queue)


def close_market(message: dict, input_queue: JoinableQueue):
    message['action'] = 'close_market'
    base_send(message, input_queue)


def base_retrieve(message: dict, input_queue: JoinableQueue, output_queue: JoinableQueue):
    base_send(message, input_queue)
    while output_queue.empty():
        continue
    return output_queue.get()


def retrieve_data(message: dict, input_queue: JoinableQueue, output_queue: JoinableQueue):
    message['action'] = 'retrieve_data'
    return base_retrieve(message, input_queue, output_queue)


def do_buy(message: dict, datum: list, input_queue: JoinableQueue, output_queue: JoinableQueue):
    message['action'] = 'do_buy'
    message['datum'] = datum
    return base_retrieve(message, input_queue, output_queue)


def do_sell(message: dict, datum: list, input_queue: JoinableQueue, output_queue: JoinableQueue):
    message['action'] = 'do_sell'
    message['datum'] = datum
    return base_retrieve(message, input_queue, output_queue)


if __name__ == '__main__':
    ticker_list = ['SOXL', 'QQQ', 'SQQQ', 'AAPL', 'NVDA', 'AMD', 'INTC', 'SPY', 'AMZN', 'GOOGL', 'TSLA', 'META']
    broker = XueQiuExecutor()
    account = TickersTrade(['SOXL'], XueQiuExecutor())
    exporter = DataExporter(broker=broker, tickers=ticker_list)
    model = NeutralNetwork()
    input_queue = JoinableQueue()
    output_queue = JoinableQueue()
    controller = Controller(exporter=exporter, model=model, in_queue=input_queue, out_queue=output_queue)

    process = Process(target=controller.entry)
    process.start()

    new_york_tz = pytz.timezone('America/New_York')
    message = {
        'action': '',
        'datum': []
    }
    is_buying = True
    market_status = False

    while True:
        current_time = datetime.now(new_york_tz)
        print(current_time)
        if current_time.weekday() < 5:
            if 4 <= current_time.hour <= 20:
                if market_status:
                    datum = retrieve_data(message, input_queue, output_queue)
                    print(datum)
                    if is_buying:
                        buy = do_buy(message, datum, input_queue, output_queue)
                        if buy:
                            print('buy')
                            account.buy('SOXL', datum[0])
                            is_buying = False

                    else:
                        sell = do_sell(message, datum, input_queue, output_queue)
                        if sell:
                            print('sell')
                            account.sell('SOXL', datum[0])
                            is_buying = True
                else:
                    account.reload()
                    market_status = True
                    open_market(message, input_queue)
            else:
                if market_status:
                    market_status = False
                    close_market(message, input_queue)
                    account.save()
                else:
                    time.sleep(900)
            time.sleep(30)
        else:
            time.sleep(3600)
