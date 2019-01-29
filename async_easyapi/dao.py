import functools
from sqlalchemy.sql import select, and_, func, between, distinct, text
from .util import str2hump
from .db_util import MysqlDB
from sqlalchemy.exc import NoSuchColumnError
import datetime


class Transaction():
    def __init__(self, db: MysqlDB):
        self._db = db
        self._transaction = None
        self._connect = None

    async def __aenter__(self):
        self._connect = await self._db.engine.acquire()
        self._transaction = await self._connect.begin()
        return self._connect

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self._transaction.commit()
        except Exception as e:
            await self._transaction.rollback()
            raise e
        finally:
            await self._connect.close()


def get_tx(db: MysqlDB):
    return Transaction(db)


def search_sql(sql, query: dict, table):
    for k, values in query.items():
        if not values:
            continue
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
                sql = sql.where(getattr(table.c, k[6:]).like(v))
        elif k.startswith('_in_'):
            sql = sql.where(getattr(table.c, k).in_(values))
        else:
            sql = sql.where(getattr(table.c, k) == values)
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
    def reformatter(cls, data: dict):
        """
        将model数据转换成dao数据
        :param data:
        :return:
        """
        return data

    @classmethod
    def formatter(cls, data: dict):
        """
        将dao数据转换成model数据
        :param data:
        :return:
        """
        return dict(data)

    @classmethod
    async def first(cls, ctx: dict = None, query=None, sorter_key: str = 'id'):
        """
        获取根据sorter_key倒叙第一个资源 sorter_key 默认id
        :param ctx:
        :param query:
        :return:
        """
        query = cls.reformatter(query)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        sql = sql.order_by(getattr(table.c, sorter_key, table.c.id).desc())
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        data = await res.fetchone()
        if not data:
            return None
        return cls.formatter(data)

    @classmethod
    async def last(cls, ctx: dict = None, query=None, sorter_key: str = 'id'):
        """
        获取根据sorter_key倒叙最后一个资源 sorter_key 默认id
        :param ctx:
        :param query:
        :param sorter_key:
        :return:
        """
        query = cls.reformatter(query)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        sql = sql.order_by(getattr(table.c, sorter_key, table.c.id))
        res = await cls.__db__.execute(ctx=ctx, sql=sql)

        data = await res.fetchone()
        if not data:
            return None
        return cls.formatter(data)

    @classmethod
    async def get(cls, ctx: dict = None, query=None):
        """
        获取单个资源 通常给予unique使用
        :param query:
        :return:
        """
        query = cls.reformatter(query)
        table = cls.__db__[cls.__tablename__]
        sql = select([table])
        if query:
            sql = search_sql(sql, query, table)
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        data = await res.fetchone()
        if not data:
            return None
        return cls.formatter(data)

    @classmethod
    async def query(cls, ctx: dict = None, query: dict = None, pager: dict = None, sorter: dict = None):
        """
        通用查询
        :param query:
        :param pager:
        :param sorter:
        :return:
        """
        query = cls.reformatter(query)
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
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        data = await res.fetchall()
        return list(map(cls.formatter, data))

    @classmethod
    async def insert(cls, ctx: dict = None, data: dict = None):
        """
        通用插入
        :param tx:
        :param args:
        :return:
        """
        table = cls.__db__[cls.__tablename__]
        data = cls.reformatter(data)
        sql = table.insert().values(**data)
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        return res.inserted_primary_key[0]

    @classmethod
    async def count(cls, query: dict = None):
        """
        计数
        :param query:
        :return:
        """
        query = cls.reformatter(query)
        table = cls.__db__[cls.__tablename__]
        sql = select([func.count('*')], from_obj=table)
        if query:
            sql = search_sql(sql, query, table)

        res = await cls.__db__.execute(sql=sql)
        return await res.scalar()

    @classmethod
    async def execute(cls, ctx: dict = None, sql: str = ""):
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        return res

    @classmethod
    async def update(cls, ctx: dict = None, where_dict: dict = None, data: dict = None):
        """
        通用修改
        :param ctx:
        :param primay_key:
        :param data:
        :return:
        """
        where_dict = cls.reformatter(where_dict)
        table = cls.__db__[cls.__tablename__]
        data = cls.reformatter(data)
        sql = table.update()
        if where_dict is not None:
            for key, value in where_dict.items():
                if hasattr(table.c, key):
                    sql = sql.where(getattr(table.c, key) == value)
        sql = sql.values(**data)
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        return res

    @classmethod
    async def delete(cls, ctx: dict, where_dict: dict = None):
        """
        通用删除
        :param ctx:
        :param where_didt:
        :param data:
        :return:
        """
        where_dict = cls.reformatter(where_dict)
        table = cls.__db__[cls.__tablename__]
        sql = table.delete()
        if where_dict is not None:
            for key, value in where_dict.items():
                if hasattr(table.c, key):
                    sql = sql.where(getattr(table.c, key) == value)
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        return res


class BusinessBaseDao(BaseDao):

    @classmethod
    def formatter(cls, data: dict):
        """
        将dao数据转换成model数据
        :param data:
        :return:
        """
        ignore_columns = ['created_at', 'deleted_at', 'updated_at']
        new_data = dict()
        for key, value in data.items():
            if key not in ignore_columns:
                new_data[key] = value
        return new_data

    @classmethod
    def reformatter(cls, data: dict):
        """
        将model数据转换成dao数据
        :param data:
        :return:
        """
        new_data = dict()
        for key, value in data.items():
            new_data[key] = value
        unscoped = data.get('unscoped', False)
        if not unscoped and 'deleted_at' not in data:
            new_data['deleted_at'] = None
        return new_data

    @classmethod
    async def update(cls, ctx: dict = None, where_dict: dict = None, data: dict = None):
        """
        通用修改
        :param ctx:
        :param primay_key:
        :param data:
        :return:
        """
        where_dict = cls.reformatter(where_dict)
        table = cls.__db__[cls.__tablename__]
        data = cls.reformatter(data)
        data['updated_at'] = datetime.datetime.now()
        sql = table.update()
        if where_dict is not None:
            for key, value in where_dict.items():
                if hasattr(table.c, key):
                    sql = sql.where(getattr(table.c, key) == value)
        sql = sql.values(**data)
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        return res.rowcount

    @classmethod
    async def delete(cls, ctx: dict, where_dict: dict = None):
        """
        通用删除
        :param ctx:
        :param where_didt:
        :param data:
        :return:
        """
        where_dict = cls.reformatter(where_dict)
        data = dict()
        data['deleted_at'] = datetime.datetime.now()
        table = cls.__db__[cls.__tablename__]
        sql = table.update()
        if where_dict is not None:
            for key, value in where_dict.items():
                if hasattr(table.c, key):
                    sql = sql.where(getattr(table.c, key) == value)
        sql = sql.values(**data)
        res = await cls.__db__.execute(ctx=ctx, sql=sql)
        return res
