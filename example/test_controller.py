import async_esayapi
import asyncio

my_db = async_esayapi.MysqlDB('root', 'wshwoaini', 'localhost', 3306, 'EDUCATION')


class UserDao(async_esayapi.BaseDao):
    __db__ = my_db
    __tablename_ = 'users'


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(UserDao.query())
