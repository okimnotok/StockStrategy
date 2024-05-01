class BrokerExecutor:
    def buy_with_market(self, ticker, quantity):
        raise NotImplemented

    def buy_with_limit(self, ticker, quantity, price):
        raise NotImplemented

    def sell_with_market(self, ticker, quantity):
        raise NotImplemented

    def sell_with_limit(self, ticker, quantity, price):
        raise NotImplemented

    def sell_with_stop_loss(self, ticker, quantity, price):
        raise NotImplemented

    def cancel_stock_order(self, order_id):
        raise NotImplemented

    def is_order_finished(self, order_id):
        raise NotImplemented

    def get_order_status(self, order_id):
        raise NotImplemented

    def get_order_info(self, order_id):
        raise NotImplemented

    def retrieve_current_price(self, ticker):
        raise NotImplemented

    def retrieve_history_price(self, ticker):
        raise NotImplemented
