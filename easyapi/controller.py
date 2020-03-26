from easyapi_tools.errors import BusinessError
from easyapi import EasyApiContext
from easyapi.sql import Pager, Sorter
from sqlalchemy.exc import OperationalError, IntegrityError, DataError


class ControllerMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if "BaseController" in name:
            return type.__new__(cls, name, bases, attrs)
        if attrs.get('__dao__') is None:
            raise NotImplementedError("Should have __dao__ value.")
        cls.__validator__ = attrs.get('__validator__', None)
        return type.__new__(cls, name, bases, attrs)


class BaseController(metaclass=ControllerMetaClass):
    @classmethod
    def formatter(cls, ctx: EasyApiContext, data: dict):
        """
        限制资源返回
        :param data:
        :return:
        """
        return data.copy()

    @classmethod
    def reformatter(cls, ctx: EasyApiContext, data: dict):
        """
        限制资源查询方式
        :param data:
        :return:
        """
        return data.copy()

    @classmethod
    def get(cls, id: int, ctx: EasyApiContext = None):
        """
        获取单个资源
        :param id:
        :param query: 附加的查询
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()

        query = ctx.read('query')
        if query is None:
            query = {}

        query = {"id": id, **query}
        try:
            data = cls.__dao__.get(ctx=ctx, query=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        if not data:
            return None
        return cls.formatter(ctx=ctx, data=data)

    @classmethod
    def query(cls, ctx: EasyApiContext = None, query: dict = None, pager: Pager = None, sorter: Sorter = None) -> (
            list, dict):
        """
        获取多个资源
        :param filter_dict:
        :param pager:
        :param sorter:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if query is None:
            query = {}
        if pager is None:
            pager = Pager(page=1, per_page=20)
        if sorter is None:
            sorter = Sorter(sort_by='id', desc=True)
        query = cls.reformatter(ctx=ctx, data=query)
        try:
            res = cls.__dao__.query(ctx=ctx, query=query, pager=pager, sorter=sorter)
            total = cls.__dao__.count(ctx=ctx, query=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return list(map(lambda  d : cls.formatter(ctx=ctx, data=d), res)), total

    @classmethod
    def insert(cls, ctx: EasyApiContext = None, data: dict = None):
        """
        插入单个资源
        :param body:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if data is None:
            data = {}
        data = cls.reformatter(ctx=ctx, data=data)
        if cls.__validator__ is not None:
            err = cls.__validator__.validate(data)
            if err is not None:
                raise BusinessError(code=500, http_code=200, err_info=err)
        try:
            res = cls.__dao__.insert(ctx=ctx, data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    def update(cls, id: int, ctx: EasyApiContext = None, data: dict = None, ):
        """
        修改单个资源
        :param id:
        :param data:
        :param query: 附加的查询
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        query = ctx.read('query')
        if query is None:
            query = {}
        if data is None:
            data = {}
        if cls.__validator__ is not None:
            err = cls.__validator__.validate(data)
            if err is not None:
                raise BusinessError(code=500, http_code=200, err_info=err)
        query = {"id": id, **query}
        data = cls.reformatter(ctx=ctx, data=data)
        try:
            res = cls.__dao__.update(ctx=ctx, where_dict=query, data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    def delete(cls, id: int, ctx: EasyApiContext = None):
        """
        删除单个资源
        :param query: 附加的查询
        :param id:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        query = ctx.read('query')
        if query is None:
            query = {}
        query = {"id": id, **query}
        try:
            res = cls.__dao__.delete(ctx=ctx, where_dict=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res
