# async_easyapi

一个方便拓展快速构建异步curd的后端api工具 基于 flask 

## Example

### 查询条件

比如一个字段叫 field,

发一个 POST 请求
{
    "_method": "GET",
    "_agrs": {
        "field": "A"
    }
}
 
就是查询 filed 值为 "A"的结果

类似的还有

```

_gt_field: 小于
_gte_field: 小于等于

_lt_field: 大于
_gte_filed: 大于等于

_in_filed: in

_like_field: 前缀 like

_search_field 模糊匹配
```


还可以做分页:

```
_per_page: 每一页多少
_page: 第几页
```

排序:

```
_order_by
_desc
```



### 基础curd

```python3

import asyncio
import async_esayapi
from fkask import Flask, Blueprint

loop = asyncio.get_event_loop()

app = Flask(__name__)

my_db = async_esayapi.MysqlDB('root', 'Root!!2018', 'localhost', 3306, 'EDUCATION')
loop.run_until_complete(my_db.connect())


class UserDao(async_esayapi.BaseDao):
    __db__ = my_db // 定义dao传入


class UserController(async_esayapi.BaseController):
    __dao__ = UserDao


class UserHandler(async_easyapi.BaseFlaskHandler):
    __controller__ = UserController

async_easyapi.register_api(app=app, view=UserHandler, endpoint='user_api', url='/users')

if __name__ == '__main__':
    app.run()

```

### 新增复杂业务

```python

import asyncio
import async_easyapi
from flask import Flask, Blueprint

loop = asyncio.get_event_loop()

app = Flask(__name__)

my_db = async_easyapi.MysqlDB('root', 'Root!!2018', 'localhost', 3306, 'EDUCATION')
loop.run_until_complete(my_db.connect())


class UserDao(async_easyapi.BusinessBaseDao):
    __db__ = my_db


class UserController(async_easyapi.BaseController):
    __dao__ = UserDao

    @classmethod
    def complex_bussiness(cls):
        return "complex"


bp = Blueprint(name='users', import_name='users', url_prefix='/users')


class UserHandler(async_easyapi.FlaskBaseHandler):
    __controller__ = UserController


async_easyapi.register_api(app=bp, view=UserHandler, endpoint='user_api', url='')


@bp.route('/complex')
async def complex_api():
    res = UserController.complex_bussiness()
    return res

app.register_blueprint(bp)
if __name__ == '__main__':
    app.run()


```

### 运行时字段检查

```
    user = dao.query(query={dao._like_name: 'test'})

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



