from sqlalchemy import MetaData
import sqlalchemy as sa
from aiomysql.sa import create_engine


def get_sync_engine(user: str, password: str, host: str, port: str, database: str):
    print('mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(
        user=user,
        password=password,
        host=host,  # your host
        port=port,
        database=database,
    ))
    engine = sa.create_engine(
        'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(
            user=user,
            password=password,
            host=host,  # your host
            port=port,
            database=database
        ),
    )
    return engine


async def get_engine(user: str, password: str, host: str, port: str, database: str):
    print('mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(
        user=user,
        password=password,
        host=host,  # your host
        port=port,
        database=database,
    ))
    engine = await create_engine(
        user=user,
        password=password,
        host=host,  # your host
        port=port,
        db=database
    )
    return engine


class MysqlDB(object):
    """
    用于操作 mysql 的db对象
    """

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self._engine = None
        self._sync_engine = None
        self._metadata = None
        self._tables = None

    async def connect(self):
        """
        链接数据库 初始化engine
        :return:
        """
        self._sync_engine = get_sync_engine(user=self.user, password=self.password, host=self.host, port=self.port,
                                            database=self.database)
        self._engine = await get_engine(user=self.user, password=self.password, host=self.host, port=self.port,
                                        database=self.database)
        self._metadata = MetaData(self._sync_engine)
        self._metadata.reflect(bind=self._sync_engine)
        self._tables = self._metadata.tables

    def __getitem__(self, name):
        return self._tables[name]

    def __getattr__(self, item):
        return self._tables[item]

    async def execute(self, sql, ctx: dict = None, *args, **kwargs, ):
        """
        执行sql
        :param ctx:
        :param sql:
        :param args:
        :param kwargs:
        :return:
        """
        conn = None
        if ctx is not None:
            conn = ctx.get("connection", None)
        if conn is None:
            async with self._engine.acquire() as conn:
                return await conn.execute(sql, *args, **kwargs)
        else:
            return await conn.execute(sql, *args, **kwargs)
