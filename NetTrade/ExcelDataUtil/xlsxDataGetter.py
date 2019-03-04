from idataapi_transform import ProcessFactory, GetterConfig
from .headers import Headers
from .xlsxDataWriter import XlsxDataWriter
import os

class XlsxDataGetter(object):
    @staticmethod
    def get_data(file_name, raise_if_not_exist=True):
        ret_list = list()

        if not os.path.exists(file_name):
            if raise_if_not_exist:
                raise ValueError("您还未进行过任何操作，请至少记录一次操作(买入/卖出)，再进行查看/计算")
            else:
                return ret_list

        getter = ProcessFactory.create_getter(GetterConfig.RXLSXConfig(file_name, filter_=Headers.filter_cn2en))
        for items in getter:
            ret_list.extend(items)
        return ret_list
