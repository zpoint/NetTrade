
def calculate(mon_per_year, rate, target):
    init_year = 0
    init_mon = 0
    while init_mon < target:
        init_mon += mon_per_year
        init_mon *= 1 + rate
        init_year += 1
        print("year: %d, mon: %f" % (init_year, init_mon))


calculate(20, 0.2, 1000)
