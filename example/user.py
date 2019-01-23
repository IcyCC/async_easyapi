import asyncio
import easy_admin
from quart import Quart, Blueprint

loop = asyncio.get_event_loop()

app = Quart(__name__)

my_db = easy_admin.MysqlDB('root', 'Root!!2018', 'localhost', 3306, 'EDUCATION')
loop.run_until_complete(my_db.connect())

class UserDao(easy_admin.BaseDao):
    __db__ = my_db


class UserController(easy_admin.BaseController):
    __dao__ = UserDao


class UserHandler(easy_admin.BaseQuartHandler):
    __controller__ = UserController


app.register_blueprint(UserHandler.__blueprint__)

if __name__ == '__main__':
        app.run()
