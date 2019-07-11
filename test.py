import easyapi
import sqlalchemy.exc

tables = []

mysql_db = easyapi.MysqlDB('root', 'Root!!2018', '0.0.0.0', 3306,
                           'tracker')

mysql_db.connect()

res = mysql_db.execute("show tables;")

for r in res:
    tables.append(r[0])

def ignore_err_execute(sql):
    try:
        res = mysql_db.execute(sql)
        print("执行 sql {}".format(res))
    except sqlalchemy.exc.InternalError as e:
        print("错误{}".format(e))


for table in tables:
    # ignore_err_execute("""ALTER TABLE {table} ADD created_at TIMESTAMP DEFAULT  NULL;""".format(table=table))
    # ignore_err_execute("""ALTER TABLE {table} ADD updated_at TIMESTAMP DEFAULT  NULL;""".format(table=table))
    # ignore_err_execute("""ALTER TABLE {table} ADD deleted_at TIMESTAMP DEFAULT  NULL;""".format(table=table))
    # ignore_err_execute("""ALTER TABLE {table} ADD updated_by VARCHAR(255) NOT NULL DEFAULT '';""".format(table=table))
    # ignore_err_execute("""ALTER TABLE {table} ADD created_by VARCHAR(255) NOT NULL DEFAULT '';""".format(table=table))

    ignore_err_execute("""ALTER TABLE {table} MODIFY updated_by varchar(255) NOT NULL DEFAULT '';""".format(table=table))
    ignore_err_execute("""ALTER TABLE {table} MODIFY created_by varchar(255) NOT NULL DEFAULT '';""".format(table=table))



