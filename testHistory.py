from NetTrade.HistoryNotes.HistoryNotes import HistoryNotes
from NetTrade.Strategy.NetstrategyA import NetstrategyA

if __name__ == "__main__":
    HistoryNotes(NetstrategyA, "jsl", "sz162411", 0.6, 2000, 2017, 2019, range_percent=0.03, growth_rate=0.3)
