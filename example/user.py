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


class UserHandler(async_easyapi.QuartBaseHandler):
    __controller__ = UserController

    def get(self, id: int):
        return super().get(id)


async_easyapi.register_api(app=app, view=UserHandler, endpoint='user_api', url='/users', )

if __name__ == '__main__':
    app.run()
