class Datum:
    def __init__(self, current, volume, high, low, avg):
        self.current = current or 0
        self.volume = volume or 1
        self.high = high or current
        self.low = low or current
        self.avg = avg or current

    @staticmethod
    def average(data: list['Datum']):
        if not data:
            return 0
        return sum([datum.volume * datum.avg for datum in data]) / sum([datum.volume for datum in data])

    @staticmethod
    def maximum(data: list['Datum']):
        if not data:
            return 0
        return max([datum.high for datum in data])

    @staticmethod
    def minimum(data: list['Datum']):
        if not data:
            return 0
        return min([datum.low for datum in data])


class DataHandler:
    def __init__(self, size):
        self.size = size

    def retrieve_current_data(self, original_prices: list[Datum]):
        result = [original_prices[-1].current] if self.size == 1 and original_prices else []
        if len(original_prices) < self.size:
            return result + [Datum.average(original_prices), Datum.maximum(original_prices), Datum.minimum(original_prices)]
        else:
            return result + [Datum.average(original_prices[-self.size:]), Datum.maximum(original_prices[-self.size:]), Datum.maximum(original_prices[-self.size:])]
