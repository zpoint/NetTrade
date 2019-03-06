import time
import math
import logging
from ..Variables.Status import Status


class NetstrategyA(object):
    def __init__(self, operate_history, range_percent=0.03, growth_rate=0.2):
        """
        :param operate_history: [(value1, shares, money1, date_str， status, timestamp), (value2, shares, money2, date_str, status, timestamp) ... ]
        :param range_percent: 幅度, e.g 0.03
        :param growth_rate: 每网增加幅度 0.2
        """
        self.operate_history = operate_history
        self.buy_history_including_sold, self.sell_history, self.buy_history, \
        self.curr_buy_money, self.sum_shares, self.curr_shares_worth, \
        self.total_base_money, self.total_current_money, self.curr_val = self.split_history()
        self.init_val = self.operate_history[0][0]
        self.range_percent = range_percent
        self.growth_rate = growth_rate

    def re_static(self):
        self.buy_history_including_sold, self.sell_history, self.buy_history, \
        self.curr_buy_money, self.sum_shares, self.curr_shares_worth, \
        self.total_base_money, self.total_current_money, self.curr_val = self.split_history()
        self.init_val = self.operate_history[0][0]

    def calc_next_buy_sell_val(self):
        """
        :return: ((buy_value, buy_shares, buy_money), (sell_value, sell_shares, sell_money))
        """
        if not self.buy_history:
            if self.operate_history:
                buy_tup = (self.operate_history[0][0], self.operate_history[0][1], self.operate_history[0][2])
            else:
                buy_tup = None
            return buy_tup, None

        latest_buy_value, latest_buy_money = self.buy_history[-1][0], self.buy_history[-1][2]

        next_fall_value = round(latest_buy_value * (1 - self.range_percent), 3)
        next_fall_money = latest_buy_money * (1 + self.growth_rate)
        next_fall_shares = int(math.ceil(next_fall_money / next_fall_value / 100) * 100) # 取100的整数份额
        next_fall_money = next_fall_value * next_fall_shares

        next_grow_value = latest_buy_value * (1 + self.range_percent)
        r = math.modf(next_grow_value * 1000)
        if r[0]:
            next_grow_value = (r[1] + 1) / 1000
        else:
            next_grow_value = r[1] / 1000
        next_grow_shares = 0
        need_sell_history_index_including = self.bin_search(next_grow_value)
        for each in self.buy_history[need_sell_history_index_including:]:
            next_grow_shares += each[1]
        next_grow_money = next_grow_shares * next_grow_value

        return (round(next_fall_value, 4), round(next_fall_shares, 4), round(next_fall_money, 4)), \
               (round(next_grow_value, 4), round(next_grow_shares, 4), round(next_grow_money, 4))

    def calc_curr_buy_sell_val(self, curr_val):
        tup1, tup2 = self.calc_next_buy_sell_val()
        next_buy_value, next_buy_shares, next_buy_money = tup1
        if tup2:
            next_sell_value, next_sell_shares, next_sell_money = tup2
        else:
            next_sell_value, next_sell_shares, next_sell_money = None, None, None

        if next_sell_value is not None and curr_val > next_sell_value:
            # there are some shares need to be sold, but currently hold
            need_sell_history_index_including = self.bin_search(curr_val)
            next_grow_shares = 0
            for each in self.buy_history[need_sell_history_index_including:]:
                next_grow_shares += each[1]
            next_grow_money = next_grow_shares * curr_val
            return None, (curr_val, next_grow_shares, round(next_grow_money, 4))
        elif curr_val < next_buy_value:
            # need to buy more, price is lower than curr_val
            operation = self.buy_history[-1] if self.buy_history else self.operate_history[0]
            x = math.log(curr_val / operation[0], 1-self.range_percent)
            next_fall_money = operation[2] * math.pow(1 + self.growth_rate, x)
            next_fall_shares = int(math.ceil(next_fall_money / curr_val / 100) * 100) # 取100的整数份额
            next_fall_money = curr_val * next_fall_shares
            return (curr_val, next_fall_shares, round(next_fall_money, 4)), None
        return None, None

    def bin_search(self, value, begin=None, end=None):
        if begin is None:
            begin = 0
        if end is None:
            end = len(self.buy_history) - 1

        if begin == end: # terminate
            if value > self.buy_history[begin][0]:
                return begin
            return end + 1 if end != len(self.buy_history) - 1 else None

        middle = int((begin + end) / 2)
        if value == self.buy_history[middle][0]:
            # best match, 不能卖出相同净值的买入份额
            return self.bin_search(value, middle, middle)
        elif value < self.buy_history[middle][0]:
            return self.bin_search(value, middle+1, end)
        elif value > self.buy_history[middle][0]:
            return self.bin_search(value, begin, middle)

    def split_history(self):
        buy_history_including_sold = list()
        sell_history = list()
        buy_history = list()
        curr_buy_money = 0 # 当前投入的钱数 (还未卖出的钱数的和)
        sum_shares = 0 # 当前持有份额
        curr_shares_worth = 0 # 投入部分当前市值(净值为 curr_val)
        total_current_money = 0 # 总的当前的钱数(投入部分当前市值 + 卖出部分获得的金额)
        already_sold_money = 0 # 总的卖出获得的金额

        curr_used_money = 0  # 当前占用本金
        curr_not_used_money = 0  # 当前卖出未占用本金
        # 总收益率 = total_current_money / total_base_money
        for each in self.operate_history:
            if each[4] == Status.BUY:
                new_curr_not_used_money = curr_not_used_money
                curr_used_money += each[2]
                new_curr_not_used_money -= each[2]
                if new_curr_not_used_money < 0:
                    new_curr_not_used_money = 0
                    already_sold_money -= curr_not_used_money
                else:
                    already_sold_money -= each[2]
                curr_not_used_money = new_curr_not_used_money

                buy_history_including_sold.append(each)
                buy_history.append(each)
            elif each[4] == Status.SELL:
                sell_history.append(each)
                max_index = len(buy_history)-1
                if len(buy_history) == 1:
                    need_sell_history = buy_history
                    max_index = -1
                else:
                    for i in range(max_index, -1, -1):
                        max_index = i
                        if buy_history[max_index][0] >= each[0]:
                            break
                    need_sell_history = buy_history[max_index + 1:]
                sold_rest_money = sum(i[2] for i in need_sell_history)
                curr_used_money -= sold_rest_money
                curr_not_used_money += sold_rest_money
                already_sold_money += each[0] * sum(i[1] for i in need_sell_history)
                buy_history = buy_history[:max_index+1]
            else:
                raise ValueError("Unknown status: %s" % (str(each), ))

        for i in buy_history:
            curr_buy_money += i[2]
            sum_shares += i[1]
        curr_val = self.operate_history[-1][0]
        curr_shares_worth = sum_shares * curr_val
        total_current_money = round(curr_shares_worth + already_sold_money, 2)
        return buy_history_including_sold, sell_history, buy_history, curr_buy_money, \
               sum_shares, curr_shares_worth, round(curr_used_money + curr_not_used_money, 3), total_current_money, curr_val

    def print_status(self):
        print("操作历史:")
        if not self.operate_history:
            print("无任何操作记录")
        else:
            buy_history = list()
            curr_used_money = 0 # 当前占用本金
            curr_not_used_money = 0 # 当前卖出未占用本金
            already_sold_money = 0
            print("%-10s\t%-10s\t%-10s\t%-10s\t%-20s\t%-15s\t%-10s" % ("净值", "份额", "金额", "操作", "日期", "当前动用过本金", "当前收益率"))
            for each in self.operate_history:
                total_current_money = 0  # 总的当前的钱数(投入部分当前市值 + 卖出部分获得的金额)
                if each[4] == Status.BUY:
                    new_curr_not_used_money = curr_not_used_money
                    curr_used_money += each[2]
                    new_curr_not_used_money -= each[2]
                    if new_curr_not_used_money < 0:
                        new_curr_not_used_money = 0
                        already_sold_money -= curr_not_used_money
                    else:
                        already_sold_money -= each[2]
                    curr_not_used_money = new_curr_not_used_money
                    buy_history.append(each)
                else:
                    if len(buy_history) == 1:
                        need_sell_history = buy_history
                        max_index = -1
                    else:
                        max_index = len(buy_history) - 1
                        for i in range(max_index, -1, -1):
                            max_index = i
                            if buy_history[max_index][0] >= each[0]:
                                break
                        need_sell_history = buy_history[max_index + 1:]

                    sold_rest_money = sum(i[2] for i in need_sell_history)
                    curr_used_money -= sold_rest_money
                    curr_not_used_money += sold_rest_money
                    buy_history = buy_history[:max_index + 1]
                    already_sold_money += each[0] * sum(i[1] for i in need_sell_history)
                sum_shares = sum(i[1] for i in buy_history)
                total_current_money += sum_shares * each[0] + already_sold_money
                total_used_base_money = curr_used_money + curr_not_used_money
                rate = (total_current_money - total_used_base_money) / total_used_base_money
                print("%-10s\t%-10s\t%-10s\t%-10s\t%-20s\t%-20s\t%-10s" %
                      (str(each[0]), str(each[1]), str(each[2]), Status.CN_MAP[str(each[4])], each[3],
                       round(total_used_base_money, 3), "%.2f%%" % (rate * 100, )))

        print("\n%s" % ("当前投入的钱数 (还未卖出的钱数的和):                  ", ), round(self.curr_buy_money, 3))
        print("%s" % ("当前持有份额:                                      ", ), self.sum_shares)
        print("%s" % ("投入部分当前市值:                                   ", ), round(self.curr_shares_worth, 3))
        print("%s" % ("总的使用过的本金(当前投入的本金 + 卖出的本金):         ", ), self.total_base_money)
        print("%s" % ("总的当前的资产(投入部分当前市值 + 卖出部分获得的金额):  ", ), self.total_current_money)
        rate = (self.total_current_money - self.total_base_money) / self.total_base_money
        print("%s" % ("当前总收益:                                         %.2f  " % (self.total_current_money - self.total_base_money, )))
        print("%s" % ("当前收益率:                                         %.2f%% " % (rate * 100)), )
        ts_begin = int(self.operate_history[0][5])
        ts_now = int(self.operate_history[-1][5])
        days_interval = (ts_now - ts_begin) / (24 * 3600)
        years_interval = days_interval / 365
        if years_interval < 1:
            average_year_rate = (365 * rate / days_interval) if days_interval else 0
        else:
            if rate < 0:
                sign = -1
            else:
                sign = 1
            average_year_rate = sign * math.pow(abs(rate), 1 / years_interval)
        print("\n%s" % ("第一份到最后份时长: %.2f 天, 平均年化: %.2f%%            " % (days_interval, average_year_rate * 100)), )
