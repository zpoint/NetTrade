import time
from NetTrade.Strategy.NetstrategyA import NetstrategyA
from NetTrade.ExcelDataUtil.xlsxDataGetter import XlsxDataGetter
from NetTrade.ExcelDataUtil.xlsxDataWriter import XlsxDataWriter
from NetTrade.Util.dateUtil import timestamp2datetime
from NetTrade.Variables.Status import Status

class RealNotes(object):
    def __init__(self, code="sz162411"):
        self.file_name = code + ".xlsx"
        self.code = code
        self.operation_history = self.strategy = None

    def pr_status(self):
        if self.strategy is None:
            self.init_strategy()
        self.strategy.print_status()

    def buy(self, value, money):
        operation_history = XlsxDataGetter.get_data(self.file_name, raise_if_not_exist=False)
        # "value", "shares", "money", "date_str", "status", "timestamp"]
        shares = int(money / value + 1) # 整数份额
        money = shares * value
        ts = int(time.time())
        operation_history.append((value, shares, money, timestamp2datetime(ts), Status.BUY, ts))
        XlsxDataWriter.write_data(self.file_name, operation_history)

    def sell(self, value, shares):
        operation_history = XlsxDataGetter.get_data(self.file_name)
        ts = int(time.time())
        operation_history.append((value, shares, value * shares, timestamp2datetime(ts), Status.SELL, ts))
        XlsxDataWriter.write_data(self.file_name, operation_history)

    def init_strategy(self):
        self.operation_history = XlsxDataGetter.get_data(self.file_name)
        self.strategy = NetstrategyA(self.operation_history, 1000)

if __name__ == "__main__":
    r = RealNotes()
    # r.buy(0.40, 1000)
    r.pr_status()

