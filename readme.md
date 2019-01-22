# EasyAdmin

## Example
链接数据库

```python3

my_db = MysqlDB('user', 'pass', 'localhost', 3306, 'db')

await my_db.connect()

```

定义dao 并且写好转换函数
```python3

class UserDao(BaseDao):
     
    __db__=my_db
    @classmethod
    def formatter(cls, data):
        return dict(data)
        
    @classmethod
    def reformatter(cls, data):
        return dict(data)
```

dao操作

```python3

await UserDao.get(1) # 查id为一的
await UserDao.put({'name':'a'}) # 修改
await UserDao.insert({'name':'1'}) # 修改
await UserDao.query(query, pager, sorter) # 查
await UserDao.count(query, pager, sorter)  # 数
await UserDao.delte(1)
UserDao._c # 获取表结构
await UserDao.select(UserDao._c.id  > 10) # 查2

```

事务操作

```python3
async with get_tx() as tx:
	XxxDao.get(tx=tx)
    XxxDao.insert(tx=tx,xxx)
```

controller

```

class UserController(BaseController):
    __dao__ = UserDao
    pass
```

handler

```python
class UserHandler(QuartHandler):
    __ctl__ = UserController
    pass

```


