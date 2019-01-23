import asyncio
import async_esayapi
from quart import Quart, Blueprint

loop = asyncio.get_event_loop()

app = Quart(__name__)

my_db = async_esayapi.MysqlDB('root', 'Root!!2018', 'localhost', 3306, 'EDUCATION')
loop.run_until_complete(my_db.connect())


class UserDao(async_esayapi.BaseDao):
    __db__ = my_db


class UserController(async_esayapi.BaseController):
    __dao__ = UserDao


class UserHandler(async_esayapi.BaseQuartHandler):
    __controller__ = UserController


app.register_blueprint(UserHandler.__blueprint__)

if __name__ == '__main__':
    app.run()
