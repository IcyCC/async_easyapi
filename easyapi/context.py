import typing
from easyapi.transcation import Transaction


class EasyApiContext:

    def __init__(self, tx: Transaction=None):
        self._tx = tx
        self._data = {}
        self.formatter = None
        self.reformatter = None

    @property
    def tx(self):
        """
        读取事务 不可修改
        :return:
        """
        return self._tx

    def read(self, key:str):
        """
        读取数据
        :param key:
        :return:
        """
        return self._data.get(key)

    def set(self, key:str, value:typing.Any):
        """
        设置数据
        :param key:
        :param value:
        :return:
        """
        self._data[key] = value



