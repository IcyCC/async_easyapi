from easyapi_tools.errors import BusinessError
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
    def formatter(cls, data: dict):
        """
        限制资源返回
        :param data:
        :return:
        """
        return data

    @classmethod
    def reformatter(cls, data: dict):
        """
        限制资源查询方式
        :param data:
        :return:
        """
        return data

    @classmethod
    def get(cls, id: int, *args, **kwargs):
        """
        获取单个资源
        :param id:
        :param query: 附加的查询
        :return:
        """
        query = {"id": id}
        query.update(kwargs.get("query", {}))
        try:
            data = cls.__dao__.get(query=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        if not data:
            return None
        return cls.formatter(data)

    @classmethod
    def query(cls, query: dict, pager: dict, sorter: dict, *args, **kwargs) -> (list, dict):
        """
        获取多个资源
        :param filter_dict:
        :param pager:
        :param sorter:
        :return:
        """
        query = cls.reformatter(data=query)
        try:
            res = cls.__dao__.query(query=query, pager=pager, sorter=sorter)
            total = cls.__dao__.count(query=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return list(map(cls.formatter, res)), total

    @classmethod
    def insert(cls, data: dict, *args, **kwargs):
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
            res = cls.__dao__.insert(data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    def update(cls, id: int, data: dict, *args, **kwargs):
        """
        修改单个资源
        :param id:
        :param data:
        :param query: 附加的查询
        :return:
        """
        if cls.__validator__ is not None:
            err = cls.__validator__.validate(data)
            if err is not None:
                raise BusinessError(code=500, http_code=200, err_info=err)
        query = {"id": id}
        query.update(kwargs.get("query", {}))
        try:
            res = cls.__dao__.update(where_dict=query, data=data)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res

    @classmethod
    def delete(cls, id: int, *args, **kwargs):
        """
        删除单个资源
        :param query: 附加的查询
        :param id:
        :return:
        """

        query = {"id": id}
        query.update(kwargs.get("query", {}))
        try:
            res = cls.__dao__.delete(where_dict=query)
        except (OperationalError, IntegrityError, DataError) as e:
            raise BusinessError(code=500, http_code=500, err_info=str(e))
        return res
