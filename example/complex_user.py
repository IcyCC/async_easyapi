import asyncio
import async_easyapi
from quart import Quart, Blueprint

loop = asyncio.get_event_loop()

app = Quart(__name__)

my_db = async_easyapi.MysqlDB('root', 'wshwoaini', 'localhost', 3306, 'EDUCATION')
loop.run_until_complete(my_db.connect())


class UserDao(async_easyapi.BaseDao):
    __db__ = my_db
    __tablename__ = "senders"


class UserController(async_easyapi.BaseController):
    __dao__ = UserDao

    @classmethod
    async def complex_bussiness(cls):
        return "complex"

    @classmethod
    async def insert(cls, data: dict):
        if cls.__validator__ is not None:
            err = cls.__validator__.validate(data)
            if err is not None:
                raise async_easyapi.BusinessError(code=500, http_code=200, err_info=err)
        try:
            async with async_easyapi.get_tx(my_db) as tx:
                ctx = {"connection": tx}
                res = await UserDao.execute(ctx=ctx, sql="select * from users")
                data = await res.fetchall()
                print(data)
        except async_easyapi.BusinessError as e:
            raise e
        return res


bp = Blueprint(name='users', import_name='users', url_prefix='')


class UserHandler(async_easyapi.QuartBaseHandler):
    __controller__ = UserController


async_easyapi.register_api(app=bp, view=UserHandler, endpoint='user_api', url='/users')


@bp.route('/complex')
async def complex_api():
    res = await UserController.complex_bussiness()
    return res


app.register_blueprint(bp)
if __name__ == '__main__':
    app.run(port=8000)
