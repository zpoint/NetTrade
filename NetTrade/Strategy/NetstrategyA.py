import time
import math
from ..Variables.Status import Status

class NetstrategyA(object):
    def __init__(self, operate_history, price_per_net, range_percent=0.03, growth_rate=0.2, init_val=None):
        """
        :param operate_history: [(value1, money1, shares, timestamp, date_str， status), (value2, money2, shares, timestamp, date_str, status) ... ]
        :param price_per_net: 初始每网价格
        :param range_percent: 幅度, e.g 0.03
        :param growth_rate: 每网增加幅度 0.2
        :param init_val: initial value (第一次买入净值)
        """
        self.operate_history = operate_history
        self.buy_history_including_sold, self.sell_history, self.buy_history, \
        self.curr_buy_money, self.sum_shares, self.curr_shares_worth, \
        self.total_base_money, self.total_current_money = self.split_history()
        if init_val is None:
            self.init_val = self.operate_history[0][0]
        else:
            self.init_val = init_val
        self.price_per_net = price_per_net
        self.range_percent = range_percent
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

        next_grow_shares = 0
        need_sell_history_index_including = self.bin_search(next_grow_value)
        for each in self.buy_history[need_sell_history_index_including:]:
            next_grow_shares += each[2]
        next_grow_money = next_grow_shares * next_grow_value
        return (next_fall_value, next_fall_money, next_fall_shares), (next_grow_value, next_grow_money, next_grow_shares)

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

    def split_history(self, curr_val=None):
        """
        :param curr_val: 当前净值，不提供则按照最后次交易计算
        """
        buy_history_including_sold = list()
        sell_history = list()
        buy_history = list()
        curr_buy_money = 0 # 当前投入的钱数 (还未卖出的钱数的和)
        sum_shares = 0 # 当前持有份额
        curr_shares_worth = 0 # 投入部分当前市值(净值为 curr_val)
        total_base_money = 0 # 总的使用过的钱数(当前投入的本金 + 卖出的本金)
        total_current_money = 0 # 总的当前的钱数(投入部分当前市值 + 卖出部分获得的金额)
        # 总收益率 = total_current_money / total_base_money
        for each in self.operate_history:
            if each["status"] == Status.BUY:
                buy_history_including_sold.append(each)
                buy_history.append(each)
                total_base_money += each[1]
            elif each["status"] == Status.SELL:
                sell_history.append(each)
                total_current_money += each[1]
                max_index = len(buy_history)-1
                for i in range(max_index, -1, -1):
                    max_index = i
                    if buy_history[max_index][0] > each[0]:
                        break
                buy_history = buy_history[:max_index+1]
            else:
                raise ValueError("Unknown status: %s" % (str(each), ))

        for i in buy_history:
            curr_buy_money += i[1]
            sum_shares += i[2]
        curr_val = curr_val if curr_val else self.operate_history[-1][0]
        curr_shares_worth = sum_shares * curr_val
        total_current_money += curr_buy_money
        return buy_history_including_sold, sell_history, buy_history, curr_buy_money, \
               sum_shares, curr_shares_worth, total_base_money, total_current_money

    def print_status(self):
        print("操作历史:")
        if not self.operate_history:
            print("无任何操作记录")
        else:
            print("%-10s\t%-10s\t%-10s\t%-10s\t%-10s" % ("净值", "金额", "份额", "日期", "操作"))
        for each in self.operate_history:
            print("%-10s\t%-10s\t%-10s\t%-10s\t%-10s" % (str(each[0]), str(each[1]), str(each[2]), str(each[4]), Status.CN_MAP[str(each[5])]))

        print("当前投入的钱数 (还未卖出的钱数的和): ", self.curr_buy_money)
        print("当前持有份额: ", self.sum_shares)
        print("投入部分当前市值: ", self.curr_shares_worth)
        print("总的使用过的钱数(当前投入的本金 + 卖出的本金): ", self.total_base_money)
        print("总的当前的钱数(投入部分当前市值 + 卖出部分获得的金额): ", self.total_current_money)
        rate = self.total_current_money / self.total_base_money
        print("当前总收益率: %.2f" % (rate * 100))
        ts_begin = int(self.operate_history[0][3])
        ts_now = int(time.time())
        days_interval = (ts_now - ts_begin) / (24 * 3600)
        years_interval = days_interval / 365
        if years_interval < 1:
            average_year_rate = rate / years_interval
        else:
            average_year_rate = math.pow(rate, 1 / years_interval)
        print("第一份到最后份时长: %.2f 天, 平均年化: %.2f" % (rate * 100, average_year_rate * 100))
