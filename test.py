from multiprocessing import JoinableQueue, Process

from account.trade import TickersTrade
from broker.pretend import PretendExecutor
from data.exporter import DataExporter
from strategy.base import Controller
from strategy.neutral_network import NeutralNetwork


if __name__ == '__main__':
    ticker_list = ['1', '2', '3']
    broker = PretendExecutor()
    account = TickersTrade(['FAKE'], PretendExecutor())
    exporter = DataExporter(broker=broker, tickers=ticker_list)
    model = NeutralNetwork()
    input_queue = JoinableQueue()
    output_queue = JoinableQueue()
    controller = Controller(exporter=exporter, model=model, in_queue=input_queue, out_queue=output_queue)

    process = Process(target=controller.entry)
    process.start()

    message = {
        'action': '',
        'datum': []
    }

