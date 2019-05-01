import abc
from decimal import Decimal
from datetime import datetime, date, time


def str2hump(listx):
    listy = listx[0]
    for i in range(1, len(listx)):
        # listx[i] 直接copy 或 先加'_'再copy
        if listx[i].isupper() and not listx[i - 1].isupper():  # 加'_',当前为大写，前一个字母为小写
            listy += '_'
            listy += listx[i]
        elif listx[i].isupper() and listx[i - 1].isupper() and listx[i + 1].islower():
            # 加'_',当前为大写，前一个字母为小写
            listy += '_'
            listy += listx[i]
        else:
            listy += listx[i]
    return listy.lower()


def type_to_json(data):
    new_data = dict()
    for key, value in data.items():
        if isinstance(value, Decimal):
            new_data[key] = float(value)
        elif isinstance(value, datetime):
            new_data[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, date):
            new_data[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, time):
            new_data[key] = value.strftime("%H:%M:%S")
        else:
            new_data[key] = value
    return new_data


class AbcUrlCondition(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def parser(cls, args: dict) -> (dict, dict, dict):
        raise NotImplementedError


class DefaultUrlCondition(AbcUrlCondition):

    @classmethod
    def parser(cls, args: dict) -> (dict, dict, dict):
        """
        默认的url参数条件解析
        :param args:
        :return:
        """
        query = {}
        pager = {}
        sorter = {}
        if args:
            for k, v in args.items():
                if k == '_per_page':
                    pager['_per_page'] = v
                elif k == '_page':
                    pager['_page'] = v
                elif k == '_order_by':
                    sorter['_order_by'] = v
                elif k == '_desc':
                    sorter['_desc'] = v
                else:
                    query[k] = v
        return query, pager, sorter
