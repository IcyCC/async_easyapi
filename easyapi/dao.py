import datetime
import functools
from sqlalchemy.sql import select, func
from easyapi_tools.util import str2hump, type_to_json
from easyapi_tools.errors import BusinessError
from .db_util import MysqlDB


class Transaction():
    def __init__(self, db: MysqlDB):
        self._db = db
        self._transaction = None
        self._connect = None

    def __enter__(self):
        self._connect = self._db._engine.connect()
        self._transaction = self._connect.begin()
        return self._connect

    def __exit__(self, exc_type, exc, tb):
        try:
            self._transaction.commit()
        except Exception as e:
            self._transaction.rollback()
            raise e
        finally:
            self._connect.close()


def get_tx(db: MysqlDB):
    return Transaction(db)


def search_sql(sql, query: dict, table):
    for k in query.keys():
        if type(query[k]) is not list:
            # 兼容处理
            values = [query[k]]
        else:
            values = query[k]
        if k.startswith('_gt_'):
            for v in values:
                sql = sql.where(getattr(table.c, k[4:]) > v)
        elif k.startswith('_gte_'):
            for v in values:
                sql = sql.where(getattr(table.c, k[5:]) >= v)
        elif k.startswith('_lt_'):
            for v in values:
                sql = sql.where(getattr(table.c, k[4:]) < v)
        elif k.startswith('_lte_'):
            for v in values:
                sql = sql.where(getattr(table.c, k[5:]) <= v)
        elif k.startswith('_like_'):
            for v in values:
                sql = sql.where(getattr(table.c, k[6:]).like(v + '%'))
        elif k.startswith('_in_'):
            sql = sql.where(getattr(table.c, k[4:]).in_(values))
        else:
            sql = sql.where(getattr(table.c, k) == values[0])
    return sql


class DaoMetaClass(type):
    """
        dao的元类 读取 db 和 table信息 生成
    """

    def __new__(cls, name, bases, attrs):
        """

        :param name:
        :param bases:
        :param attrs:
        :return:
        """
        if "BaseDao" in name:
            return type.__new__(cls, name, bases, attrs)
        if attrs.get('__db__') is None:
            raise NotImplementedError("Should have __db__ value.")

        attrs['__tablename__'] = attrs.get('__tablename__') or str2hump(name[:-3]) + 's'
        return type.__new__(cls, name, bases, attrs)


class BaseDao(metaclass=DaoMetaClass):
    @classmethod
    def reformatter(cls, data: dict, *args, **kwargs):
        """
        将model数据转换成dao数据
        :param data:
        :return:
        """
        return data

    @classmethod
    def formatter(cls, data: dict, *args, **kwargs):
        """
        将dao数据转换成model数据
        :param data:
        :return:
        """
        return type_to_json(data)

    @classmethod
    def first(cls, ctx: dict = None, query=None, sorter_key: str = 'id', formatter=None, *args, **kwargs):
        """
        获取根据sorter_key倒叙第一个资源 sorter_key 默认id
        :param ctx:
        :param query:
        :param sorter_key:
        :param args:
        :param kwargs:
        :return:
        """
        if query is None:
            query = {}

        if formatter is None:
            formatter = cls.formatter
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        sql = sql.order_by(getattr(table.c, sorter_key, table.c.id).desc())
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        data = res.first()
        if not data:
            return None
        return formatter(data, *args, **kwargs)

    @classmethod
    def last(cls, ctx: dict = None, query=None, sorter_key: str = 'id', formatter=None, *args, **kwargs):
        """
        获取根据sorter_key倒叙最后一个资源 sorter_key 默认id
        :param ctx:
        :param query:
        :param sorter_key:
        :return:
        """
        if query is None:
            query = {}
        if formatter is None:
            formatter = cls.formatter
        query = cls.reformatter(query, *args, **kwargs)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        sql = sql.order_by(getattr(table.c, sorter_key, table.c.id))
        res = cls.__db__.execute(ctx=ctx, sql=sql)

        data = res.first()
        if not data:
            return None
        return formatter(data, *args, **kwargs)

    @classmethod
    def get(cls, ctx: dict = None, query=None, formatter=None, *args, **kwargs):
        """
        通用get查询
        :param ctx:
        :param query:
        :param args:
        :param kwargs:
        :return:
        """
        if query is None:
            query = {}
        if formatter is None:
            formatter = cls.formatter
        query = cls.reformatter(query, *args, **kwargs)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        data = res.first()
        if not data:
            return None
        return formatter(data, *args, **kwargs)

    @classmethod
    def query(cls, ctx: dict = None, query: dict = None, pager: dict = None, sorter: dict = None, formatter=None, *args,
              **kwargs):
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
        if query is None:
            query = {}
        if formatter is None:
            formatter = cls.formatter
        query = cls.reformatter(query, *args, **kwargs)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        if pager is not None:
            per_page = pager.get('_per_page')
            page = pager.get('_page')
            if per_page:
                sql = sql.limit(per_page)
            if page:
                if per_page is None:
                    sql = sql.offset((page - 1) * 30).limit(30)
                else:
                    sql = sql.offset((page - 1) * per_page)
        if sorter is None:
            sorter = {}
        order_by = sorter.get('_order_by', 'id')
        desc = sorter.get('_desc', True)
        if desc:
            sql = sql.order_by(getattr(table.c, order_by, table.c.id).desc())
        else:
            sql = sql.order_by(getattr(table.c, order_by, table.c.id))
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        data = res.fetchall()
        return list(map(functools.partial(formatter, *args, **kwargs), data))

    @classmethod
    def insert(cls, ctx: dict = None, data: dict = None, *args, **kwargs):
        """
        通用插入
        :param ctx:
        :param data:
        :param args:
        :param kwargs:
        :return:
        """
        if data is None:
            return None
        table = cls.__db__[cls.__tablename__]
        data = cls.reformatter(data, *args, **kwargs)
        sql = table.insert().values(**data)
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.inserted_primary_key[0]

    @classmethod
    def count(cls, ctx: dict = None, query: dict = None, *args, **kwargs):
        """
        插入
        :param ctx:
        :param query:
        :param args:
        :param kwargs:
        :return:
        """
        if query is None:
            query = {}
        query = cls.reformatter(query, *args, **kwargs)
        table = cls.__db__[cls.__tablename__]
        sql = select([func.count('*')], from_obj=table)
        if query:
            sql = search_sql(sql, query, table)

        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.scalar()

    @classmethod
    def execute(cls, ctx: dict = None, sql='SELECT 1',  *args, **kwargs):
        """
        直接执行sql
        :param ctx:
        :param sql:
        :param args:
        :param kwargs:
        :return:
        """
        res = cls.__db__.execute(ctx=ctx, sql=sql, *args, **kwargs)
        return res

    @classmethod
    def update(cls, ctx: dict = None, where_dict: dict = None, data: dict = None, *args, **kwargs):
        """
        通用修改
        :param ctx:
        :param where_dict:
        :param data:
        :param args:
        :param kwargs:
        :return:
        """
        if where_dict is None:
            where_dict = {}
        where_dict = cls.reformatter(where_dict, *args, **kwargs)
        table = cls.__db__[cls.__tablename__]
        data = cls.reformatter(data, *args, **kwargs)
        sql = table.update()
        if where_dict is not None:
            for key, value in where_dict.items():
                if hasattr(table.c, key):
                    sql = sql.where(getattr(table.c, key) == value)
        sql = sql.values(**data)
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.rowcount

    @classmethod
    def delete(cls, ctx: dict = None, where_dict: dict = None, *args, **kwargs):
        """
        通用删除
        :param ctx:
        :param where_didt:
        :param data:
        :return:
        """
        if where_dict is None:
            where_dict = {}
        where_dict = cls.reformatter(where_dict, *args, **kwargs)
        table = cls.__db__[cls.__tablename__]
        sql = table.delete()
        for key, value in where_dict.items():
            if hasattr(table.c, key):
                sql = sql.where(getattr(table.c, key) == value)
        res = cls.__db__.execute(ctx=ctx, sql=sql)
        return res.rowcount


class BusinessBaseDao(BaseDao):

    @classmethod
    def formatter(cls, data: dict, *args, **kwargs):
        """
        将dao数据转换成model数据
        :param data:
        :return:
        """
        return super().formatter(data)

    @classmethod
    def reformatter(cls, data: dict, *args, **kwargs):
        """
        将model数据转换成dao数据
        :param data:
            unscoped: 是否处理软删除
        :return:
        """
        return super().reformatter(data)

    @classmethod
    def update(cls, ctx: dict = None, where_dict: dict = None, data: dict = None, unscoped=False, modify_by: str = ''):
        """
        业务修改
        :param ctx:
        :param where_dict: 修改数据的条件
        :param unscoped: 查询软删除
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
    def delete(cls, ctx: dict = None, where_dict: dict = None, unscoped=False, modify_by: str = ''):
        """
        业务删除
        :param ctx:
        :param where_dict:
        :param unscoped:
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
    def insert(cls, ctx: dict = None, data: dict = None, modify_by='', *args, **kwargs):
        """
        业务插入
        :param ctx:
        :param data:
        :param modify_by:
        :param args:
        :param kwargs:
        :return:
        """
        if data is None:
            data = {}
        data['created_at'] = datetime.datetime.now()
        data['created_by'] = modify_by
        return super().insert(ctx=ctx, data=data)

    @classmethod
    def first(cls, ctx: dict = None, query=None, sorter_key: str = 'id', unscoped=False, formatter=None, *args,
              **kwargs):
        """
        业务查询first
        :param ctx:
        :param query:
        :param sorter_key:
        :param unscoped:
        :param args:
        :param kwargs:
        :return:
        """
        if query is None:
            query = {}
        if not unscoped:
            query['deleted_at'] = None
        return super().first(ctx=ctx, query=query, sorter_key=sorter_key, formatter=formatter, *args, **kwargs)

    @classmethod
    def last(cls, ctx: dict = None, query=None, sorter_key: str = 'id', unscoped=False, formatter=None, *args,
             **kwargs):
        """
        业务查询last
        :param ctx:
        :param query:
        :param sorter_key:
        :param unscoped:
        :param args:
        :param kwargs:
        :return:
        """
        if query is None:
            query = {}
        if not unscoped:
            query['deleted_at'] = None
        return super().last(ctx=ctx, query=query, sorter_key=sorter_key, formatter=formatter, *args, **kwargs)

    @classmethod
    def get(cls, ctx: dict = None, query=None, unscoped=False, formatter=None, *args, **kwargs):
        """
        业务查询get
        :param ctx:
        :param query:
        :param unscoped:
        :param args:
        :param kwargs:
        :return:
        """
        if query is None:
            query = {}
        if not unscoped:
            query['deleted_at'] = None
        return super().get(ctx=ctx, query=query, formatter=formatter, *args, **kwargs)

    @classmethod
    def query(cls, ctx: dict = None, query: dict = None, pager: dict = None, formatter=None, sorter: dict = None,
              unscoped=False, *args,
              **kwargs):
        """
        业务查询query
        :param ctx:
        :param query:
        :param pager:
        :param sorter:
        :param unscoped:
        :param args:
        :param kwargs:
        :return:
        """
        if query is None:
            query = {}
        if not unscoped:
            query['deleted_at'] = None
        return super().query(ctx=ctx, dict=dict, query=query, pager=pager, sorter=sorter, formatter=formatter ,*args,
                             **kwargs)
