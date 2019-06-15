import pytest
import easyapi
import os.path
import pymysql


def pytest_addoption(parser):
    parser.addoption("--db-host", action="store", metavar="DB HOST",
                     help="db host", default='127.0.0.1', )
    parser.addoption("--db-port", action="store", metavar="DB HOST",
                     type=int, help="db port", default=3306, )
    parser.addoption("--db-user", action="store", metavar="DB USER",
                     help="db user", default='root', )
    parser.addoption("--db-password", action="store", metavar="DB password",
                     help="db password", default='password')


@pytest.fixture(scope='module', autouse=True)
def db_session(request):
    db_info = {
        'host': request.config.getoption("db_host"),
        'port': request.config.getoption("db_port"),
        'user': request.config.getoption("db_user"),
        'password': request.config.getoption("db_password"),
        'db': 'easy_api_for_test'
    }
    conn = pymysql.connect(db_info['host'],
                           db_info['user'],
                           db_info['password'])

    with conn.cursor() as  cursor:
        cursor.execute("""
            create database If Not Exists easy_api_for_test default character set utf8mb4 collate utf8mb4_unicode_ci;
        """)

        cursor.execute("""
            use easy_api_for_test;
        """)

        cursor.execute("""
                DROP TABLE  IF EXISTS users;
        """)

        cursor.execute("""
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `note` varchar(234) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '123',
   `created_at`  timestamp default CURRENT_TIMESTAMP not null,
  `updated_at`  timestamp default CURRENT_TIMESTAMP not null,
  `deleted_at` timestamp                           null,
  `updated_by`  varchar(255)                        null,
  `created_by`  varchar(255) default ''             not null,
  PRIMARY KEY (`id`)
  
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        cursor.execute("""
    truncate table users;
        """)
        print("新建数据库成功")

    yield conn

    cursor = conn.cursor()
    cursor.execute("""
        DROP DATABASE  IF EXISTS easy_api_for_test;
    """)
    print("删除据库成功")
    cursor.close()


@pytest.fixture(scope='module', autouse=True)
def esayapi_session(request):
    db_info = {
        'host': request.config.getoption("db_host"),
        'port': request.config.getoption("db_port"),
        'user': request.config.getoption("db_user"),
        'password': request.config.getoption("db_password"),
        'db': 'easy_api_for_test'
    }

    mysql_db = easyapi.MysqlDB(
        host=db_info['host'],
        port=db_info['port'],
        user=db_info['user'],
        password=db_info['password'],
        database=db_info['db']
    )

    mysql_db.connect()

    class UserDao(easyapi.BusinessBaseDao):
        __tablename__ = 'users'
        __db__ = mysql_db

    class UserController(easyapi.BaseController):
        __dao__ = UserDao

    class UserHandler(easyapi.FlaskBaseHandler):
        __controller__ = UserController

    return {
        'db': mysql_db,
        'dao': UserDao,
        'controller': UserController,
        'handler': UserHandler
    }


@pytest.fixture(scope='module', autouse=True)
def transaction_session(request):
    db_info = {
        'host': request.config.getoption("db_host"),
        'port': request.config.getoption("db_port"),
        'user': request.config.getoption("db_user"),
        'password': request.config.getoption("db_password"),
        'db': 'easy_api_for_test'
    }

    conn = pymysql.connect(db_info['host'],
                           db_info['user'],
                           db_info['password'])

    with conn.cursor() as  cursor:
        cursor.execute("""
                create database If Not Exists easy_api_for_test default character set utf8mb4 collate utf8mb4_unicode_ci;
            """)

        cursor.execute("""
                use easy_api_for_test;
            """)

        cursor.execute("""
                    DROP TABLE  IF EXISTS users;
            """)

        cursor.execute("""
    CREATE TABLE `users` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
      `note` varchar(234) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '123',
       `created_at`  timestamp default CURRENT_TIMESTAMP not null,
      `updated_at`  timestamp default CURRENT_TIMESTAMP not null,
      `deleted_at` timestamp                           null,
      `updated_by`  varchar(255)                        null,
      `created_by`  varchar(255) default ''             not null,
      PRIMARY KEY (`id`)

    ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

        cursor.execute("""
        truncate table users;
            """)
        cursor.execute("""
                            DROP TABLE  IF EXISTS shares;
                    """)

        cursor.execute("""
            CREATE TABLE `shares` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `username` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
              `note` varchar(234) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '123',
               `created_at`  timestamp default CURRENT_TIMESTAMP not null,
              `updated_at`  timestamp default CURRENT_TIMESTAMP not null,
              `deleted_at` timestamp                           null,
              `updated_by`  varchar(255)                        null,
              `created_by`  varchar(255) default ''             not null,
              PRIMARY KEY (`id`)

            ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                    """)

        cursor.execute("""
                truncate table users;
                    """)
        print("新建数据库成功")

    mysql_db = easyapi.MysqlDB(
        host=db_info['host'],
        port=db_info['port'],
        user=db_info['user'],
        password=db_info['password'],
        database=db_info['db']
    )

    mysql_db.connect()
    yield mysql_db
