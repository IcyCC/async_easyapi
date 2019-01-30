import async_easyapi

my_db = async_easyapi.MysqlDB('root', 'wshwoaini', 'localhost', 3306, 'EDUCATION')


class UserDao(async_easyapi.BaseDao):
    __db__ = my_db
    __tablename_ = 'users'

