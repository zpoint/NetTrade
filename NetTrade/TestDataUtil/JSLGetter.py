import requests
from datetime import datetime
from .DataGetter import DataGetter

class JSLGetter(DataGetter):
    def get_data(self, stock_code, date):
        """
        :param stock_code: e.g sz162411
        :param date: e.g 2018
        :return: [(datetime1, value1), (datetime2, value2)]
        """
        r = requests.get("http://data.gtimg.cn/flashdata/hushen/daily/%s/%s.js" % (date[:2], stock_code))
        ret_data = list()
        for line in r.text.split("\n")[1:-1]:
            line_lst = line.split(" ")
            date_obj = datetime.strptime(line_lst[0], "%y%m%d")
            val = float(line_lst[-2])
            ret_data.append((date_obj, val))
