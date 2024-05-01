from datetime import timedelta, date, datetime, timezone

from keras.models import Sequential
from keras.layers import Dense, LSTM
import numpy as np
import pandas as pd

from common.constants import PATH_PREFIX


def serialize(row):
    return row


def initialize_model():
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(264, 1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


class BaseNetwork:
    def __init__(self):
        pass

    def reload(self):
        pass

    def train(self):
        pass

    def all_train(self):
        pass

    def save(self):
        pass

    def buy(self, datum) -> bool:
        pass

    def sell(self, datum) -> bool:
        pass


class NeutralNetwork(BaseNetwork):
    def __init__(self):
        super().__init__()

    def reload(self):
        print('Reloading NeutralNetwork')
        self.buy_model = initialize_model()
        self.sell_model = initialize_model()
        self.buy_model.load_weights(f'{PATH_PREFIX}/buy_model.h5')
        self.sell_model.load_weights(f'{PATH_PREFIX}/sell_model.h5')
        print('Done!!!')

    def _load_all_data(self):
        time_str = "2024-04-07T00:00:00.359+08:00"
        dt = datetime.fromisoformat(time_str)
        now = datetime.now(timezone.utc)
        delta = now - dt
        self._load_data_with_day(delta.days)

    def _load_data(self):
        self._load_data_with_day(7)

    def _load_data_with_day(self, day):
        train_data = []
        buy_result = []
        sell_result = []
        for i in range(day):
            today = date.today()
            data_date = today - timedelta(days=i)
            if data_date.weekday() <= 4:
                path = f'{PATH_PREFIX}/{data_date.year}/{data_date.month}/{data_date.day}'
                current_train_data, current_buy_data, current_sell_data = None, None, None
                try:
                    with open(f'{path}/train.txt') as f:
                        data = f.read()
                        current_train_data = pd.read_json(data)
                    with open(f'{path}/buy_result.txt') as f:
                        data = f.read()
                        buy_result.append(pd.read_json(data))
                    with open(f'{path}/sell_result.txt') as f:
                        data = f.read()
                        sell_result.append(pd.read_json(data))
                    train_data.append(current_train_data)
                    buy_result.append(current_buy_data)
                    sell_result.append(current_sell_data)
                except:
                    continue
        self.train_data = pd.concat(train_data).apply(serialize, axis=0)
        print(self.train_data.shape)
        buy_result = pd.concat(buy_result)
        self.buy_result = (buy_result - np.min(buy_result)) / (np.max(buy_result) - np.min(buy_result))
        print(self.buy_result.shape)
        sell_result = pd.concat(sell_result)
        self.sell_result = (sell_result - np.min(sell_result)) / (np.max(sell_result) - np.min(sell_result))
        print(self.sell_result.shape)

    def all_train(self):
        self._load_all_data()
        self.base_train()

    def train(self):
        self._load_data()
        self.base_train()

    def base_train(self):
        train_x = np.reshape(self.train_data.values,
                             (self.train_data.values.shape[0], self.train_data.values.shape[1], 1))
        sell_x = self.sell_result.values.reshape(-1, 1, 1)
        buy_x = self.buy_result.values.reshape(-1, 1, 1)
        self.buy_model.fit(train_x, buy_x, epochs=2, batch_size=1, verbose=2)
        self.buy_model.fit(train_x, sell_x, epochs=2, batch_size=1, verbose=2)

    def save(self):
        self.buy_model.save(f'{PATH_PREFIX}/buy_model.h5')
        self.sell_model.save(f'{PATH_PREFIX}/sell_model.h5')

    def buy(self, datum) -> bool:
        x = np.array(datum).reshape((-1, 264, 1))
        return self.buy_model.predict(x) > 0.6

    def sell(self, datum) -> bool:
        x = np.array(datum).reshape((-1, 264, 1))
        return self.sell_model.predict(x) > 0.6


if __name__ == '__main__':
    model = NeutralNetwork()
    model.reload()
    model.all_train()
    model.save()
    x = np.array(
        [30.79, 32.310973, 34.58, 34.58, 32.310973, 34.58, 30.2, 32.310973, 34.58, 30.2, 32.310973, 34.58, 30.2,
         32.310973,
         34.58, 30.2, 32.310973, 34.58, 30.2, 32.310973, 34.58, 30.2, 414.65, 417.300677, 422.75, 422.75, 417.300677,
         422.75, 413.07, 417.300677, 422.75, 413.07, 417.300677, 422.75, 413.07, 417.300677, 422.75, 413.07, 417.300677,
         422.75, 413.07, 417.300677, 422.75, 413.07, 12.84, 12.606803, 12.99, 12.99, 12.606803, 12.99, 12.16, 12.606803,
         12.99, 12.16, 12.606803, 12.99, 12.16, 12.606803, 12.99, 12.16, 12.606803, 12.99, 12.16, 12.606803, 12.99,
         12.16,
         165.0, 165.137151, 166.4, 166.4, 165.137151, 166.4, 164.075, 165.137151, 166.4, 164.075, 165.137151, 166.4,
         164.075, 165.137151, 166.4, 164.075, 165.137151, 166.4, 164.075, 165.137151, 166.4, 164.075, 762.0, 796.388727,
         843.24, 843.24, 796.388727, 843.24, 756.06, 796.388727, 843.24, 756.06, 796.388727, 843.24, 756.06, 796.388727,
         843.24, 756.06, 796.388727, 843.24, 756.06, 796.388727, 843.24, 756.06, 146.64, 149.177533, 154.25, 154.25,
         149.177533, 154.25, 145.29, 149.177533, 154.25, 145.29, 149.177533, 154.25, 145.29, 149.177533, 154.25, 145.29,
         149.177533, 154.25, 145.29, 149.177533, 154.25, 145.29, 34.2, 34.463572, 35.13, 35.13, 34.463572, 35.13, 34.18,
         34.463572, 35.13, 34.18, 34.463572, 35.13, 34.18, 34.463572, 35.13, 34.18, 34.463572, 35.13, 34.18, 34.463572,
         35.13, 34.18, 495.16, 496.882474, 500.455, 500.455, 496.882474, 500.455, 493.86, 496.882474, 500.455, 493.86,
         496.882474, 500.455, 493.86, 496.882474, 500.455, 493.86, 496.882474, 500.455, 493.86, 496.882474, 500.455,
         493.86,
         174.63, 175.569936, 179.0, 179.0, 175.569936, 179.0, 173.44, 175.569936, 179.0, 173.44, 175.569936, 179.0,
         173.44,
         175.569936, 179.0, 173.44, 175.569936, 179.0, 173.44, 175.569936, 179.0, 173.44, 154.09, 154.199857, 156.36,
         156.36, 154.199857, 156.36, 152.3, 154.199857, 156.36, 152.3, 154.199857, 156.36, 152.3, 154.199857, 156.36,
         152.3,
         154.199857, 156.36, 152.3, 154.199857, 156.36, 152.3, 147.05, 148.727189, 150.94, 150.94, 148.727189, 150.94,
         146.22, 148.727189, 150.94, 146.22, 148.727189, 150.94, 146.22, 148.727189, 150.94, 146.22, 148.727189, 150.94,
         146.22, 148.727189, 150.94, 146.22, 481.07, 485.35619599999995, 502.8, 502.8, 485.35619599999995, 502.8,
         475.73,
         485.35619599999995, 502.8, 475.73, 485.35619599999995, 502.8, 475.73, 485.35619599999995, 502.8, 475.73,
         485.35619599999995, 502.8, 475.73, 485.35619599999995, 502.8, 475.73])
    x = x.reshape((-1, 264, 1))
    y = model.buy(x)
    print(y)
