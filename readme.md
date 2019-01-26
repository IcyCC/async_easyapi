# async_easyapi

一个方便拓展快速构建异步curd的后端api工具 基于 quart 

## Example

### 基础curd

```python3

import asyncio
import async_esayapi
from quart import Quart, Blueprint

loop = asyncio.get_event_loop()

app = Quart(__name__)

my_db = async_esayapi.MysqlDB('root', 'Root!!2018', 'localhost', 3306, 'EDUCATION')
loop.run_until_complete(my_db.connect())


class UserDao(async_esayapi.BaseDao):
    __db__ = my_db // 定义dao传入


class UserController(async_esayapi.BaseController):
    __dao__ = UserDao


class UserHandler(async_easyapi.BaseQuartHandler):
    __controller__ = UserController

async_easyapi.register_api(app=app, view=UserHandler, endpoint='user_api', url='/users', )

if __name__ == '__main__':
    app.run()

```

### 新增复杂业务

```python

class UserController(async_esayapi.BaseController):
    __dao__ = UserDao
    
    @classmethod
    async def complex_business(cls):
        res = await my_db.excute(sql="""
        复杂的sql
        """).fetchall()    
        # 格式化
        return res
        
bp = Blueprint(name='users', url_prefix='/users')

class UserHandler(async_esayapi.BaseQuartHandler):
    __controller__ = UserController

async_easyapi.register_api(app=bp, view=UserHandler, endpoint='user_api', url='/users')

@bp.route('xxx') 
async def complex_api():
    res = UserController.complex_model()
    return res


if __name__ == '__main__':
    app.run()

```


### 表单检验

```python
class MyValidator(async_esayapi.AbcValidator):
    
    @classmethod
    def validate(cls):
        pass

class UserController(async_esayapi.BaseController):
    __dao__ = UserDao
    __validator__ = MyValidator
```



