from NetTrade.Notes.RealNotes import RealNotes
from NetTrade.Strategy.NetstrategyA import NetstrategyA

def note():
    r = RealNotes("sz162411", NetstrategyA, range_percent=0.03, growth_rate=0.2)
    # r.buy(0.50, 1000)
    # r.buy(0.485, 1201)
    # r.buy(0.47, 1441)
    # r.sell(0.485, 3066)
    # r.calc_next_val()
    r.pr_status()
    r.calc_curr_val(0.30)

def history():
    pass

if __name__ == "__main__":
    note()

