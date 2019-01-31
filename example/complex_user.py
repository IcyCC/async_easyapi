import easyapi
from flask import Flask, Blueprint

app = Flask(__name__)

my_db = easyapi.MysqlDB('root', 'wshwoaini', 'localhost', 3306, 'EDUCATION')
my_db.connect()


class UserDao(easyapi.BaseDao):
    __db__ = my_db
    __tablename__ = "senders"


class UserController(easyapi.BaseController):
    __dao__ = UserDao

bp = Blueprint(name='users', import_name='users', url_prefix='')


class UserHandler(easyapi.FlaskBaseHandler):
    __controller__ = UserController


easyapi.register_api(app=bp, view=UserHandler, endpoint='user_api', url='/users')



app.register_blueprint(bp)
if __name__ == '__main__':
    app.run(port=8000)
