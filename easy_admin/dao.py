import functools
from sqlalchemy.sql import select, and_, func, between, distinct, text
from . import MysqlDB, str2hump


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
        if name == "BaseDao":
            return type.__new__(cls, name, bases, attrs)
        cls.db = attrs.get('__db__')
        if cls.db is None:
            raise NotImplementedError("Should have __db__ value.")

        cls.tablename = attrs.get('__tablename_') or str2hump(name[:-3])
        return type.__new__(cls, name, bases, attrs)

    def __getattr__(cls, item):
        """
        用于Model.Field 方式获取字段
        :param item:
        :return:
        """
        return cls.__mappings__[item]

    async def query(cls, query, pager, sorter):
        """
        通用查询
        :param query:
        :param pager:
        :param sorter:
        :return:
        """
        table = cls.db[cls.tablename]
        sql = select([table])
        if query:
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
                else:
                    sql = sql.where(getattr(table.c, k).in_(values))

        if pager:
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
        res = await cls.db.execute(sql)
        return await res.fetchall()


class BaseDao(metaclass=DaoMetaClass):
    pass
