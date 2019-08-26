import datetime
import functools
from sqlalchemy import Table
from sqlalchemy.sql import select, func
from easyapi_tools.util import str2hump, type_to_json
from easyapi.sql import search_sql, Pager, Sorter
from easyapi.context import EasyApiContext


class DaoMetaClass(type):
    """
        dao的元类 读取 db 和 table信息 生成
    """

    def __new__(cls, name, bases, attrs):
        """

        :param name:
        :param bases:from easyapi import MysqlDB

        :param attrs:
        :return:
        """
        if "BaseDao" in name:
            return type.__new__(cls, name, bases, attrs)
        if attrs.get('__db__') is None:
            raise NotImplementedError("Should have __db__ value.")

        attrs['__tablename__'] = attrs.get('__tablename__') or str2hump(name[:-3]) + 's'

        table = attrs['__db__'][attrs['__tablename__']]  # type: Table
        attrs['__table__'] = table

        for c in table.c:
            attrs[c.name] = c.name
            attrs['_gte_' + c.name] = '_gte_' + c.name
            attrs['_gt_' + c.name] = '_gt_' + c.name

            attrs['_lte_' + c.name] = '_lte_' + c.name
            attrs['_lt_' + c.name] = '_lt_' + c.name

            attrs['_like_' + c.name] = '_like_' + c.name
            attrs['_in_' + c.name] = '_in_' + c.name

        return type.__new__(cls, name, bases, attrs)


class BaseDao(metaclass=DaoMetaClass):
    @classmethod
    def reformatter(cls, ctx: EasyApiContext = None, data: dict = None):
        """
        将model数据转换成dao数据
        :param ctx:
        :param data:
        :return:
        """
        if data is None:
            return dict()
        return data

    @classmethod
    def formatter(cls, ctx: EasyApiContext = None, data: dict = None):
        """
        将dao数据转换成model数据
        :param ctx:
        :param data:
        :return:
        """
        if data is None:
            return dict()
        return type_to_json(data)

    @classmethod
    def get(cls, ctx: EasyApiContext = None, query: dict = None, sorter: Sorter = None):
        """
        通用get查询
        :param ctx:
        :param query:
        :param args:
        :param kwargs:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if query is None:
            query = {}
        query = cls.reformatter(ctx=ctx, data=query)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        sql = sql.order_by(table.c.id.desc())
        if sorter:
            order_by = sorter.sort_by
            desc = sorter.desc
            if desc:
                sql = sql.order_by(getattr(table.c, order_by, table.c.id).desc())
            else:
                sql = sql.order_by(getattr(table.c, order_by, table.c.id))
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        data = res.first()
        if not data:
            return None
        return cls.formatter(ctx, data)

    @classmethod
    def query(cls, ctx: EasyApiContext = None, query: dict = None, pager: Pager = None, sorter: Sorter = None):
        """
        通用query查询
        :param ctx:
        :param query:
        :param pager:
        :param sorter:
        :param args:
        :param kwargs:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if query is None:
            query = {}
        query = cls.reformatter(ctx=ctx, data=query)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        if pager is not None:
            per_page = pager.per_page
            page = pager.page
            if per_page:
                sql = sql.limit(per_page)
            if page:
                if per_page is None:
                    sql = sql.offset((page - 1) * 30).limit(30)
                else:
                    sql = sql.offset((page - 1) * per_page)
        if sorter:
            order_by = sorter.sort_by
            desc = sorter.desc
            if desc:
                sql = sql.order_by(getattr(table.c, order_by, table.c.id).desc())
            else:
                sql = sql.order_by(getattr(table.c, order_by, table.c.id))
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        data = res.fetchall()
        return list(map(lambda  d : cls.formatter(ctx=ctx, data=d), data))

    @classmethod
    def insert(cls, ctx: EasyApiContext = None, data: dict = None):
        """
        通用插入
        :param ctx:
        :param data:
        :param args:
        :param kwargs:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if data is None:
            return None
        table = cls.__db__[cls.__tablename__]
        data = cls.reformatter(ctx=ctx, data=data)
        sql = table.insert().values(**data)
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.inserted_primary_key[0]

    @classmethod
    def count(cls, ctx: EasyApiContext = None, query: dict = None):
        """
        插入
        :param ctx:
        :param query:
        :param args:
        :param kwargs:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if query is None:
            query = {}
        query = cls.reformatter(ctx=ctx, data=query)
        table = cls.__db__[cls.__tablename__]
        sql = select([func.count('*')], from_obj=table)
        if query:
            sql = search_sql(sql, query, table)

        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.scalar()

    @classmethod
    def execute(cls, ctx: EasyApiContext = None, sql='SELECT 1', *args, **kwargs):
        """
        直接执行sql
        :param ctx:
        :param sql:
        :param args:
        :param kwargs:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        res = cls.__db__.execute(ctx=ctx, sql=sql, *args, **kwargs)
        return res

    @classmethod
    def update(cls, ctx: EasyApiContext = None, where_dict: dict = None, data: dict = None, *args, **kwargs):
        """
        通用修改
        :param ctx:
        :param where_dict:
        :param data:
        :param args:
        :param kwargs:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if where_dict is None:
            where_dict = {}
        where_dict = cls.reformatter(ctx, where_dict)
        table = cls.__db__[cls.__tablename__]
        data = cls.reformatter(ctx, data)
        sql = table.update()
        if where_dict is not None:
            for key, value in where_dict.items():
                if hasattr(table.c, key):
                    sql = sql.where(getattr(table.c, key) == value)
        sql = sql.values(**data)
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.rowcount

    @classmethod
    def delete(cls, ctx: EasyApiContext = None, where_dict: dict = None, *args, **kwargs):
        """
        通用删除
        :param ctx:
        :param where_dict:
        :param data:
        :return:
        """
        if ctx is None:
            ctx = EasyApiContext()
        if where_dict is None:
            where_dict = {}
        where_dict = cls.reformatter(ctx, where_dict)
        table = cls.__db__[cls.__tablename__]
        sql = table.delete()
        for key, value in where_dict.items():
            if hasattr(table.c, key):
                sql = sql.where(getattr(table.c, key) == value)
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.rowcount


class BusinessBaseDao(BaseDao):

    @classmethod
    def formatter(cls, ctx: EasyApiContext = None, data: dict = None):
        """
        将dao数据转换成model数据
        :param data:
        :return:
        """
        return super().formatter(ctx=ctx, data=data)

    @classmethod
    def reformatter(cls, ctx: EasyApiContext = None, data: dict = None):
        """
        将model数据转换成dao数据
        :param data:
            unscoped: 是否处理软删除
        :return:
        """
        return super().reformatter(ctx=ctx, data=data)

    @classmethod
    def update(cls, ctx: EasyApiContext = None, data: dict = None, where_dict: dict = None, unscoped=False,
               modify_by: str = ''):
        """
        业务修改
        :param ctx:
        :param where_dict: 修改数据的条件
        :param unscoped: 是否可以查询到被软删除的
        :param data: 修改的数据
        :param modify_by: 修改用户
        :return:
        """
        if where_dict is None:
            where_dict = {}
        data['updated_at'] = datetime.datetime.now()
        data['updated_by'] = modify_by
        if not unscoped:
            where_dict['deleted_at'] = None
        return super().update(ctx=ctx, where_dict=where_dict, data=data)

    @classmethod
    def delete(cls, ctx: EasyApiContext = None, where_dict: dict = None, unscoped=False, modify_by: str = ''):
        """
        业务删除
        :param ctx:
        :param where_dict:
        :param unscoped: 是否可以查询到被软删除的
        :param modify_by:
        :return:
        """
        if where_dict is None:
            where_dict = {}
        data = dict()
        data['deleted_at'] = datetime.datetime.now()
        data['updated_by'] = modify_by
        if not unscoped:
            where_dict['deleted_at'] = None
        return super().update(ctx=ctx, where_dict=where_dict, data=data)

    @classmethod
    def insert(cls, ctx: EasyApiContext = None, data: dict = None, modify_by=''):
        """
        业务插入
        :param ctx:
        :param data:
        :param modify_by:
        :return:
        """
        if data is None:
            data = {}
        data['created_at'] = datetime.datetime.now()
        data['created_by'] = modify_by
        return super().insert(ctx=ctx, data=data)

    @classmethod
    def get(cls, ctx: EasyApiContext = None, query:dict=None, sorter: Sorter = None, unscoped=False):
        """
        业务查询get
        :param ctx:
        :param query:
        :param unscoped: 是否可以查询到被软删除的
        :return:
        """
        if query is None:
            query = {}
        if not unscoped:
            query['deleted_at'] = None
        return super().get(ctx=ctx, query=query)

    @classmethod
    def query(cls, ctx: EasyApiContext = None, query: dict = None, pager: Pager = None, sorter: Sorter = None,
              unscoped=False):
        """
        业务查询query
        :param ctx:
        :param query:
        :param pager:
        :param sorter:
        :param unscoped:
        :return:
        """
        if query is None:
            query = {}
        if not unscoped:
            query['deleted_at'] = None
        return super().query(ctx=ctx, query=query, pager=pager, sorter=sorter)
