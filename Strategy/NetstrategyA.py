from ..Variables.Status import Status

class NetstrategyA(object):
    def __init__(self, operate_history, init_val, price_per_net, range_percent, sell_strategy="all", growth_rate=0.2):
        """
        :param operate_history: [(value1, money1, shares, timestamp, date_str， status), (value2, money2, shares, timestamp, date_str, status) ... ]
        :param init_val: initial value (第一次买入净值)
        :param price_per_net: 初始每网价格
        :param range_percent: 幅度, e.g 0.03
        :param sell_strategy: 卖出策略, all or average
        :param growth_rate: 每网增加幅度 0.2
        """
        self.operate_history = operate_history
        self.buy_history, self.sell_history, self.sum_value, self.sum_money, self.sum_shares, self.curr_money = self.split_history()
        self.init_val = init_val
        self.price_per_net = price_per_net
        self.range_percent = range_percent
        self.sell_strategy = sell_strategy
        self.growth_rate = growth_rate

    def calc_next_buy_sell_val(self):
        """
        :return: ((buy_value, buy_money, buy_shares), (sell_value, sell_money, sell_shares))
        """
        if not self.buy_history:
            return (self.init_val, self.price_per_net), None

        latest_buy_value, latest_buy_money, latest_shares, latest_buy_ts, latest_buy_date, status = self.buy_history[-1]
        next_fall_value = latest_buy_value * (1 - self.range_percent)
        next_fall_money = next_fall_value * (1 + self.growth_rate)
        next_fall_shares = int(next_fall_money / next_fall_value + 1) # 取整数份额
        next_fall_money = next_fall_value * next_fall_shares

        next_grow_value = latest_buy_value * (1 + self.range_percent)
        if self.sell_strategy == "all":
            next_grow_shares = 0
            need_sell_history_index_including = self.bin_search(next_grow_value)
            for each in self.buy_history[need_sell_history_index_including:]:
                next_grow_shares += each[2]
            next_grow_money = next_grow_shares * next_grow_value
        else:
            sum_shares = ()

    def bin_search(self, value, begin=None, end=None):
        if begin is None:
            begin = 0
        if end is None:
            end = len(self.buy_history) - 1

        if begin == end: # terminate
            if value >= self.buy_history[begin][0]:
                return begin
            return end + 1 if end != len(self.buy_history) - 1 else None

        middle = int((begin + end) / 2)
        if value == self.buy_history[middle][0]:
            # best match
            return middle
        elif value < self.buy_history[middle][0]:
            return self.bin_search(value, middle+1, end)
        elif value > self.buy_history[middle][0]:
            return self.bin_search(value, begin, middle)

    def split_history(self):
        buy_history = list()
        sell_history = list()
        for each in self.operate_history:
            if each["status"] == Status.BUY:
                buy_history.append(each)
            elif each["status"] == Status.SELL:
                sell_history.append(each)
            else:
                raise ValueError("Unknown status")
