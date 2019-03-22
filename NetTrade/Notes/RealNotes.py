import time
from ..ExcelDataUtil.xlsxDataGetter import XlsxDataGetter
from ..ExcelDataUtil.xlsxDataWriter import XlsxDataWriter
from ..Util.dateUtil import timestamp2datetime
from ..Variables.Status import Status

class RealNotes(object):
    def __init__(self, code, strategy, **kwargs):
        self.file_name = code + ".xlsx"
        self.code = code
        self.strategy = strategy
        self.operation_history = None
        self.kwargs = kwargs

    def pr_status(self):
        if self.operation_history is None:
            self.init_strategy()
        self.strategy.print_status()

    def calc_next_val(self):
        if self.operation_history is None:
            self.init_strategy()
        tup_buy, tup_sell = self.strategy.calc_next_buy_sell_val()
        buy_value, buy_shares, buy_money = tup_buy
        print("\n\n下次买入价格: %-8s\t买入份额: %-8s\t买入金额: %-8s" % (buy_value, buy_shares, buy_money))
        if tup_sell:
            sell_value, sell_shares, sell_money = tup_sell
            print("下次卖出价格: %-8s\t卖出份额: %-8s\t卖出金额: %-8s\n\n" % (sell_value, sell_shares, sell_money))
        else:
            print("份额已卖完，无下次卖出价格\n")

    def buy(self, value, shares, ts=None):
        operation_history = XlsxDataGetter.get_data(self.file_name, raise_if_not_exist=False)
        # "value", "shares", "money", "date_str", "status", "timestamp"]
        if shares % 100 != 0:
            raise ValueError("请输入100的整数倍份额")
        money = shares * value
        if ts is None:
            ts = int(time.time())
        operation_history.append((value, shares, money, timestamp2datetime(ts), Status.BUY, ts))
        XlsxDataWriter.write_data(self.file_name, operation_history)

    def sell(self, value, shares, ts=None):
        operation_history = XlsxDataGetter.get_data(self.file_name)
        if ts is None:
            ts = int(time.time())
        operation_history.append((value, shares, value * shares, timestamp2datetime(ts), Status.SELL, ts))
        XlsxDataWriter.write_data(self.file_name, operation_history)

    def init_strategy(self):
        self.operation_history = XlsxDataGetter.get_data(self.file_name)
        self.strategy = self.strategy(self.operation_history, **self.kwargs)

    def calc_curr_val(self, value):
        if self.operation_history is None:
            self.init_strategy()
        tup_buy, tup_sell = self.strategy.calc_curr_buy_sell_val(value)
        if tup_buy is not None:
            buy_value, buy_shares, buy_money = tup_buy
            print("\n当前净值跌幅过大，需要加大买入, 价格: %-8s\t买入份额: %-8s\t买入金额: %-8s" % (buy_value, buy_shares, buy_money))
        elif tup_sell is not None:
            sell_value, sell_shares, sell_money = tup_sell
            print("当前净值涨幅过大: 需要加大卖出，价格: %-8s\t卖出份额: %-8s\t卖出金额: %-8s\n" % (sell_value, sell_shares, sell_money))
        else:
            print("\n当前净值波动在合理范围内\n")
