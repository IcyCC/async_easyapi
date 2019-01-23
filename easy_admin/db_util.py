from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy_aio import ASYNCIO_STRATEGY


def get_engine(user: str, password: str, host: str, port: str, database: str):
    print('mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(
        user=user,
        password=password,
        host=host,  # your host
        port=port,
        database=database,
    ))
    engine = create_engine(
        'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(
            user=user,
            password=password,
            host=host,  # your host
            port=port,
            database=database
        ),
        strategy=ASYNCIO_STRATEGY
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
        self._metadata = None
        self._tables = None

    def connect(self):
        """
        链接数据库 初始化engine
        :return:
        """
        self._engine = get_engine(user=self.user, password=self.password, host=self.host, port=self.port,
                                  database=self.database)
        self._metadata = MetaData(self._engine)
        self._metadata.reflect(bind=self._engine)
        self._tables = self._metadata.tables

    def __getitem__(self, name):
        return self._tables[name]

    def __getattr__(self, item):
        return self._tables[item]

    async def execute(self, ctx: dict, sql, *args, **kwargs):
        """
        执行sql
        :param ctx:
        :param sql:
        :param args:
        :param kwargs:
        :return:
        """
        conn = ctx.get("connection", None)
        if conn is None:
            conn = await self._engine.connect()
        return await conn.execute(sql, *args, **kwargs)
