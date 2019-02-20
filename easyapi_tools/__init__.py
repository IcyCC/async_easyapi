import easyapi
import sqlalchemy.exc


def add_business_field(mysql_db:easyapi.MysqlDB):
    """
    增加业务字段
    :param mysql_db:
    :return:
    """
    tables = []
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
        ignore_err_execute("""ALTER TABLE {table} ADD created_at TIMESTAMP DEFAULT  NULL;""".format(table=table))
        ignore_err_execute("""ALTER TABLE {table} ADD updated_at TIMESTAMP DEFAULT  NULL;""".format(table=table))
        ignore_err_execute("""ALTER TABLE {table} ADD deleted_at TIMESTAMP DEFAULT  NULL;""".format(table=table))
        ignore_err_execute("""ALTER TABLE {table} ADD updated_by VARCHAR(255) DEFAULT '';""".format(table=table))
        ignore_err_execute("""ALTER TABLE {table} ADD created_by VARCHAR(255) DEFAULT '';""".format(table=table))


