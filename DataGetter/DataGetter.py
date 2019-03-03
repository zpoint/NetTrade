import abc


class DataGetter(object):
    @abc.abstractmethod
    def get_data(self, stock_code, date):
        pass
