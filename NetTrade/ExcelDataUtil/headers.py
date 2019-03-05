class Headers(object):
    fields_en2cn_map = {
        "value": "净值",
        "shares": "份额",
        "money": "金额",
        "date_str": "日期",
        "status": "状态",
        "timestamp": "时间戳"
    }
    fields_cn2en_map = {v: k for k, v in fields_en2cn_map.items()}
    fields_en_order = ["value", "shares", "money", "date_str", "status", "timestamp"]
    fields_cn_order = list()
    for i in fields_en_order:
        fields_cn_order.append(fields_en2cn_map[i])

    @staticmethod
    def filter_en2cn(item):
        new_item = {k: v for k, v in zip(Headers.fields_cn_order, item)}
        return new_item

    @staticmethod
    def filter_cn2en(item):
        for float_keys in ("value", "shares", "money", "timestamp"):
            item[Headers.fields_en2cn_map[float_keys]] = round(float(item[Headers.fields_en2cn_map[float_keys]]), 3)
        r = tuple(item[k] for k in Headers.fields_cn_order)
        return r
