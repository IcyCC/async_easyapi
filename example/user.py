import asyncio
import async_easyapi
from quart import Quart, Blueprint

loop = asyncio.get_event_loop()

app = Quart(__name__)

my_db = async_easyapi.MysqlDB('root', 'Root!!2018', 'localhost', 3306, 'EDUCATION')
loop.run_until_complete(my_db.connect())


class UserDao(async_easyapi.BaseDao):
    __db__ = my_db


class UserController(async_easyapi.BaseController):
    __dao__ = UserDao


class UserHandler(async_easyapi.BaseQuartHandler):
    __controller__ = UserController


app.register_blueprint(UserHandler.__blueprint__)

if __name__ == '__main__':
    app.run()
