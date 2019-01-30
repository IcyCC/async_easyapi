import async_easyapi
from flask import Flask, Blueprint

app = Flask(__name__)

my_db = async_easyapi.MysqlDB('root', 'wshwoaini', 'localhost', 3306, 'EDUCATION')
my_db.connect()


class UserDao(async_easyapi.BaseDao):
    __db__ = my_db
    __tablename__ = "senders"


class UserController(async_easyapi.BaseController):
    __dao__ = UserDao

bp = Blueprint(name='users', import_name='users', url_prefix='')


class UserHandler(async_easyapi.FlaskBaseHandler):
    __controller__ = UserController


async_easyapi.register_api(app=bp, view=UserHandler, endpoint='user_api', url='/users')



app.register_blueprint(bp)
if __name__ == '__main__':
    app.run(port=8000)
