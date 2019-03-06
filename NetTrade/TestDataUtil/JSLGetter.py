import requests
import logging
from datetime import datetime
from idataapi_transform import ProcessFactory # for log
from .DataGetter import DataGetter

class JSLGetter(DataGetter):
    def get_data(self, stock_code, date):
        """
        :param stock_code: e.g sz162411
        :param date: e.g 2018
        :return: [(datetime1, value1), (datetime2, value2)]
        """
        url = "http://data.gtimg.cn/flashdata/hushen/daily/%s/%s.js" % (str(date)[2:], stock_code)
        logging.info("requesting %s" % (url, ))
        r = requests.get(url)
        if '<head><title>404' in r.text:
            raise ValueError("无法从以下 url 获取到历史数据，请确保参数均填写正确: %s" % (url, ))
        ret_data = list()
        for line in r.text.split("\n")[1:-1]:
            line_lst = line.split(" ")
            date_obj = datetime.strptime(line_lst[0], "%y%m%d")
            val = float(line_lst[-2])
            ret_data.append((date_obj, val))
        return ret_data
