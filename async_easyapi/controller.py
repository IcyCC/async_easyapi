import asyncio
from .errors import BusinessError
from sqlalchemy.exc import OperationalError, IntegrityError, DataError
from datetime import datetime

class ControllerMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "BaseController" or name == "BusinessControllerBase":
            return type.__new__(cls, name, bases, attrs)
        if attrs.get('__dao__') is None:
            raise NotImplementedError("Should have __dao__ value.")
        cls.__validator__ = attrs.get('__validator__', None)
        return type.__new__(cls, name, bases, attrs)


class BaseController(metaclass=ControllerMetaClass):
    @classmethod
    def formatter(cls, data: dict):
        return data

    @classmethod
    async def get(cls, id: int):
        """
        获取单个资源
        :param id:
        :return:
        """
        query = {"id": id}
        try:
            data = await cls.__dao__.get(query=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        if not data:
            return None
        return cls.formatter(data)

    @classmethod
    async def query(cls, query: dict, pager: dict, sorter: dict) -> (list, dict):
        """
        获取多个资源
        :param filter_dict:
        :param pager:
        :param sorter:
        :return:
        """
        try:
            res, total = await asyncio.gather(cls.__dao__.query(query, pager, sorter),
                                              cls.__dao__.count(query))
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return list(map(cls.formatter, res)), total

    @classmethod
    async def insert(cls, data: dict):
        """
        插入单个资源
        :param body:
        :return:
        """
        if cls.__validator__ is not None:
            err = cls.__validator__.validate(data)
            if err is not None:
                raise BusinessError(code=500, http_code=200, err_info=err)
        try:
            res = await cls.__dao__.insert(data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    async def update(cls, id: int, data: dict):
        """
        修改单个资源
        :param id:
        :param data:
        :return:
        """
        if cls.__validator__ is not None:
            err = cls.__validator__.validate(data)
            if err is not None:
                raise BusinessError(code=500, http_code=200, err_info=err)
        query = {"id": id}
        try:
            res = await cls.__dao__.update(where_dict=query, data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    async def delete(cls, id: int):
        """
        删除单个资源
        :param id:
        :return:
        """
        query = {"id": id}
        try:
            res = await cls.__dao__.delete(where_dict=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res
