import easy_admin
import asyncio

my_db = easy_admin.MysqlDB('root', 'wshwoaini', 'localhost', 3306, 'EDUCATION')


class UserDao(easy_admin.BaseDao):
    __db__ = my_db
    __tablename_ = 'users'


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(UserDao.query())
