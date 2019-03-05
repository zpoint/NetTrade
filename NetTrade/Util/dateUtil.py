import time

def timestamp2datetime(value):
    """
    timestamp2datetime(1471234567) -> "2016-1-1 12:12:12"
    """
    struct_time = time.localtime(value)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', struct_time)
    return dt

def datetime2timestamp(dt):
    """
    datetime2timestamp("2016-1-1 12:12:12") -> 1471234567
    """
    struct_time = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(struct_time))
