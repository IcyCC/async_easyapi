import easyapi

my_db = easyapi.MysqlDB('root', 'wshwoaini', 'localhost', 3306, 'EDUCATION')


class UserDao(easyapi.BaseDao):
    __db__ = my_db
    __tablename_ = 'users'

