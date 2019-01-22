import functools
from sqlalchemy.sql import select, and_, func, between, distinct, text
from . import MysqlDB, str2hump


class Transaction():
    def __init__(self, db: MysqlDB):
        self._db = db
        self._transaction = None
        self._connect = None

    def __enter__(self):
        self._connect = self._db.engine().connect()
        self._transaction = self._connect.begin()
        return self._connect

    def __exit__(self, type, value, trace):
        try:
            self._transaction.commit()
        except Exception as e:
            self._transaction.rollback()
            raise e


def get_tx(db: MysqlDB):
    return Transaction(db)


def comm_count(db, table_name, query):
    table = db[table_name]
    sql = select([func.count('*')], from_obj=table)
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
                    sql = sql.where(getattr(table.c, k[6:]).like("%" + v))
            else:
                sql = sql.where(getattr(table.c, k).in_(values))

    res = db.execute(sql)
    return res.scalar()


class DaoMetaClass(type):
    """
        dao的元类 读取 db 和 table信息 生成
    """

    def __new__(cls, name, bases, attrs):
        """"""
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

    def query(cls, query, pager, sorter):
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
        res = cls.db.execute(sql)
        return res.fetchall()

    async def insert(cls, tx, args):
        pass


class BaseDao(metaclass=DaoMetaClass):
    pass
