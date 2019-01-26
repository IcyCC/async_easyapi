import asyncio
from .errors import BusinessError
from sqlalchemy.exc import OperationalError, IntegrityError, DataError


class ControllerMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "BaseController":
            return type.__new__(cls, name, bases, attrs)
        if attrs.get('__dao__') is None:
            raise NotImplementedError("Should have __dao__ value.")
        return type.__new__(cls, name, bases, attrs)


class BaseController(metaclass=ControllerMetaClass):
    @classmethod
    async def get(self, id: int):
        """
        获取单个资源
        :param id:
        :return:
        """
        query = {"id": id}
        try:
            data = await self.__dao__.query(query=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        if not data:
            return None
        return data[0]

    @classmethod
    async def query(self, query: dict, pager: dict, sorter: dict) -> (list, dict):
        """
        获取多个资源
        :param filter_dict:
        :param pager:
        :param sorter:
        :return:
        """
        try:
            res, total = await asyncio.gather(self.__dao__.query(query, pager, sorter),
                                              self.__dao__.count(query))
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res, total

    @classmethod
    async def insert(self, data: dict):
        """
        插入单个资源
        :param body:
        :return:
        """
        if self.__validator__ is not None:
            err = self.__validator__.validate(data)
            if err is not None:
                raise BusinessError(code=500, http_code=200, err_info=err)
        try:
            res = await self.__dao__.insert(data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    async def update(self, id: int, data: dict):
        """
        修改单个资源
        :param id:
        :param data:
        :return:
        """
        if self.__validator__ is not None:
            err = self.__validator__.validate(data)
            if err is not None:
                raise BusinessError(code=500, http_code=200, err_info=err)
        query = {"id": id}
        try:
            res = await self.__dao__.update(where_dict=query, data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    async def delete(self, id: int):
        """
        删除单个资源
        :param id:
        :return:
        """
        query = {"id": id}
        try:
            res = await self.__dao__.delete(where_dict=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res
