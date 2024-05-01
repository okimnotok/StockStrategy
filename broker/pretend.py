from random import uniform, randint

from broker.base import BrokerExecutor
from data.datum import Datum


class PretendExecutor(BrokerExecutor):
    def __str__(self):
        super().__init__()

    def to_datum(self, lower, higher):
        rand_list = sorted([uniform(lower, higher), uniform(lower, higher), uniform(lower, higher), uniform(lower, higher)])
        return Datum(
            current=rand_list[1],
            volume=randint(100000, 400000),
            high=rand_list[3],
            low=rand_list[0],
            avg=rand_list[2]
        )

    def retrieve_current_price(self, ticker):
        return self.to_datum(30, 40)

    def retrieve_history_price(self, ticker):
        return [self.to_datum(30, 40) for i in range(20)]

    def buy_with_limit(self, ticker, quantity, price):
        return True

    def sell_with_limit(self, ticker, quantity, price):
        return True
