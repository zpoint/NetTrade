from datetime import datetime
from ..TestDataUtil.GetterFactory import GetterFactory
from ..Variables.Status import Status


class HistoryNotes(object):
    def __init__(self, strategy, source, code, begin_val, net_price, year_begin, year_end, **kwargs):
        """
        :param source: 数据来源
        :param code: 交易代码
        :param begin_val: 入网净值
        :param net_price: 初始价格
        :param year_begin: 开始的年份
        :param year_end: 结束的年份
        """
        getter = GetterFactory.create_getter(source)
        date_now = datetime.now()
        year_now = date_now.year
        if year_end > year_now:
            year_end = year_now
        result_data = list()
        for year in range(year_begin, year_end+1):
            ret_data = getter.get_data(code, year)
            result_data.extend(ret_data)

        self.strategy = strategy
        self.code = code
        self.begin_val = begin_val
        self.net_price = net_price
        self.kwargs = kwargs
        self.operation_history = list()
        self.curr_strategy = None
        self.next_buy_value, self.next_buy_shares, self.next_buy_money, self.next_sell_value, self.next_sell_shares, self.next_sell_money = None, None, None, None, None, None
        for date_time, value in result_data:
            if not self.next_buy_value:
                # first net
                if value <= begin_val:
                    self.buy(value, date_time, True)
            else:
                if value <= self.next_buy_value:
                    self.buy(value, date_time)
                else:
                    self.sell(value, date_time)

    def buy(self, value, date_time, first_time=False):
        if first_time:
            money = True
        else:
            # recalculate next buy
            pass

        self.operation_history.append((value, round(money / value, 3), money, date_time.strftime("%Y-%m-%d %H:%M:%S"), Status.BUY, int(date_time.timestamp())))
        if first_time:
            self.curr_strategy = self.strategy(self.operation_history, **self.kwargs) if self.kwargs else self.strategy(self.operation_history)


    def recalculate_next(self):
        next_buy_bup, next_sell_tup = self.curr_strategy.calc_next_buy_sell_val()
        self.next_buy_value, self.next_buy_shares, self.next_buy_money = next_buy_bup
        self.next_sell_value, self.next_sell_shares, self.next_sell_money = next_sell_tup
