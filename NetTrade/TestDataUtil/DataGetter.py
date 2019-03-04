import abc

class DataGetter(object):
    @abc.abstractmethod
    def get_data(self, stock_code, date):
        """
        :param stock_code: e.g sz162411
        :param date: e.g 2018
        :return: [(datetime1, value1), (datetime2, value2)]
        """
        pass
