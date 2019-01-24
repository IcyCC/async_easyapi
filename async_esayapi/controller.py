from async_esayapi.errors import *
from sqlalchemy.exc import *


class ControllerMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "BaseController":
            return type.__new__(cls, name, bases, attrs)
        if attrs.get('__dao__') is None:
            raise NotImplementedError("Should have __dao__ value.")
        return type.__new__(cls, name, bases, attrs)

    async def get(cls, id: int):
        """
        获取单个资源
        :param id:
        :return:
        """
        query = {"id": id}
        data = await cls.__dao__.query(query=query)
        if not data:
            return None
        return data[0]

    async def query(cls, filter_dict: dict, pager: dict, sorter: dict):
        """
        获取多个资源
        :param filter_dict:
        :param pager:
        :param sorter:
        :return:
        """
        res = await cls.__dao__.query(query=filter_dict, pager=pager, sorter=sorter)
        return res

    async def count(cls, query: dict):
        """
        获取资源总数
        :param query:
        :return:
        """
        num = await cls.__dao__.count(query=query)
        return num

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

    async def delete(cls, id: int):
        """
        删除单个资源
        :param id:
        :return:
        """
        query = {"id": id}
        res = await cls.__dao__.delete(where_dict=query)
        return res


class BaseController(metaclass=ControllerMetaClass):
    pass
