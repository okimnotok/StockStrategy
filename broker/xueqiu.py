import requests
import time

from broker.base import BrokerExecutor
from data.datum import Datum


class XueQiuExecutor(BrokerExecutor):
    def __init__(self):
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/64.0.3282.167 Safari/537.36",
            "Connection": "keep-alive"
        }
        self._initialize_headers()

    def _initialize_headers(self):
        url = 'https://xueqiu.com/hq/screener'
        response = requests.get(url, headers=self.headers, verify=True)
        cookie_list = response.cookies.get_dict()
        cookie = ""
        for k, v in cookie_list.items():
            cookie += ';' + k + "=" + v
        self.headers['cookie'] = cookie

    def _get(self, url):
        try:
            return requests.get(url, headers=self.headers)
        except:
            self._initialize_headers()
            return requests.get(url, headers=self.headers)

    @staticmethod
    def to_datum(item):
        return Datum(current=item.get('current'), volume=item.get('volume'), high=item.get('high'), low=item.get('low'), avg=item.get('avg_price'))

    def retrieve_current_price(self, ticker) -> Datum:
        url = f'https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol={ticker}&_={int(time.time())}'
        response = self._get(url)
        data = response.json().get('data')[0]
        return XueQiuExecutor.to_datum(data)

    def retrieve_history_price(self, ticker) -> list[Datum]:
        url = f'https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol={ticker}&period=1d'
        response = self._get(url)
        return [XueQiuExecutor.to_datum(item) for item in response.json().get('data').get('items')]

    def buy_with_limit(self, ticker, quantity, price):
        pass

    def sell_with_limit(self, ticker, quantity, price):
        pass


if __name__ == '__main__':
    executor = XueQiuExecutor()
    print(executor.retrieve_current_price('SOXL'))
    print(len(executor.retrieve_history_price('SOXL')))
