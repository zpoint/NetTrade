from idataapi_transform import ProcessFactory, WriterConfig
from .headers import Headers

class XlsxDataWriter(object):
    @staticmethod
    def write_data(file_name, items):
        with ProcessFactory.create_writer(WriterConfig.WXLSXConfig(file_name, headers=Headers.fields_cn_order, filter_=Headers.filter_en2cn)) as writer:
            writer.write(items)
