import asyncio
import quart
import datetime
from easy_admin import str2hump, default_url_condition


class QuartHandlerMeta(type):

    def __new__(cls, name, bases, attrs):
        """

        :param name:
        :param bases:
        :param attrs:
        :return:
        """
        if name == "BaseQuartHandler":
            return type.__new__(cls, name, bases, attrs)

        attrs['__blueprint__'] = attrs.get('__blueprint__') or quart.Blueprint(name=str2hump(name[:-7]) + 's',
                                                                               import_name=str2hump(name[:-7]) + 's',
                                                                               url_prefix='/'+str2hump(name[:-7]) + 's')
        attrs['__resource__'] = attrs.get('__resource__') or str2hump(name[:-7])
        attrs['__url_condition__'] = attrs.get('__url_condition__') or default_url_condition

        if not attrs.get('__controller__'):
            raise NotImplementedError("Handler require a  controller.")

        attrs['__blueprint__'].route(path="/<int:id>", methods=['GET'])(cls.get)
        attrs['__blueprint__'].route(path="/<int:id>", methods=['PUT'])(cls.put)
        attrs['__blueprint__'].route(path="/<int:id>", methods=['DELETE'])(cls.put)
        attrs['__blueprint__'].route(path="/", methods=['POST'])(cls.query_and_post)

        return type.__new__(cls, name, bases, attrs)

    async def get(cls, id: int):
        """
        获取单个资源
        :param id:
        :return:
        """
        data = await cls.__controller__.get(id)
        return quart.jsonify(**{
            'msg': '',
            'code': 200,
            cls.__resource__: data
        })

    async def query_and_post(cls):
        """
        处理 查询和新增
        :return:
        """
        body = quart.request.json
        method = body.get("_method") or "POST"

        if method == 'GET':
            query, pager, sorter = cls.__url_condition__(body.get("_args"))
            res, count = await asyncio.gather(cls.__controller__.query(query, pager, sorter),
                                              cls.__controller__.count(query))
            return quart.jsonify(code=200, msg='', request_infos=res, total=count)
        else:
            await cls.__controller__.insert(body)
            return quart.jsonify(code=200, msg='')

    async def put(cls, id):
        """
        新增的路由
        :return:
        """
        body = quart.request.json
        await cls.__controller__.put(id, body)
        return quart.jsonify(code=200, msg='')

    async def delete(cls, id):
        """
        删除的路由
        :param id:
        :return:
        """
        await cls.__controller__.put(id, {'deleted_at': datetime.datetime.now()})
        return quart.jsonify(code=200, msg='')


class BaseQuartHandler(metaclass=QuartHandlerMeta):
    pass
