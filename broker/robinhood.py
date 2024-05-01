import time

import robin_stocks.robinhood as r

from .base import BrokerExecutor

FINAL_STATE = ['cancelled', 'filled']


class RobinhoodExecutor(BrokerExecutor):
    def __init__(self):
        self.start_time = time.time()
        self._rh_client = r
        self._rh_client.login(EMAIL, PASSWORD)

    @property
    def rh_client(self):
        if time.time() - self.start_time >= 3600:
            self.start_time = time.time()
            self._rh_client.login(EMAIL, PASSWORD)
        return self._rh_client

    def buy_with_market(self, ticker, quantity):
        response = self.rh_client.order_buy_market(ticker, quantity)
        return response.get('id')

    def buy_with_limit(self, ticker, quantity, price):
        response = self.rh_client.order_buy_limit(ticker, quantity, price)
        return response.get('id')

    def sell_with_market(self, ticker, quantity):
        response = self.rh_client.order_sell_market(ticker, quantity)
        return response.get('id')

    def sell_with_limit(self, ticker, quantity, price):
        response = self.rh_client.order_sell_limit(ticker, quantity, price)
        return response.get('id')

    def sell_with_stop_loss(self, ticker, quantity, price):
        response = self.rh_client.order_sell_stop_loss(ticker, quantity, price)
        return response.get('id')

    def cancel_stock_order(self, order_id):
        self.rh_client.cancel_stock_order(order_id)

    def is_order_finished(self, order_id):
        return self.get_order_info(order_id) in FINAL_STATE

    def get_order_status(self, order_id):
        response = self.get_order_info(order_id)
        return response.get('state')

    def get_order_info(self, order_id):
        return self.rh_client.get_stock_order_info(order_id)

    def retrieve_current_price(self, ticker):
        return 46


robinhood_broker = RobinhoodExecutor()


if __name__ == '__main__':
    current_ticker = 'SOXL'
    current_quantity = 100
    rh = RobinhoodExecutor()
    rh.buy_with_market(current_ticker, current_quantity)
