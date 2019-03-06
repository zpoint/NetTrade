from NetTrade.Notes.RealNotes import RealNotes
from NetTrade.Strategy.NetstrategyA import NetstrategyA

def note():
    r = RealNotes("sz162411", NetstrategyA, range_percent=0.03, growth_rate=0.3)
    # r.buy(0.505, 4000)
    r.calc_next_val()
    r.pr_status()


if __name__ == "__main__":
    note()
