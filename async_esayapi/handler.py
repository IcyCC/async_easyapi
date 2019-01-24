import asyncio
import functools
import quart
import datetime
from async_esayapi import str2hump, default_url_condition, BusinessError


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
                                                                               url_prefix='/' + str2hump(
                                                                                   name[:-7]) + 's')
        attrs['__resource__'] = attrs.get('__resource__') or str2hump(name[:-7])
        attrs['__url_condition__'] = attrs.get('__url_condition__') or default_url_condition
        if not attrs.get('__controller__'):
            raise NotImplementedError("Handler require a  controller.")

        async def get(id: int):
            """
            获取单个资源
            :param id:
            :return:
            """
            nonlocal attrs
            try:
                data = await attrs['__controller__'].get(id)
            except BusinessError as e:
                return quart.jsonify(code=e.code, msg=e.err_info), e.http_code
            if not data:
                return quart.jsonify(**{
                    'msg': '',
                    'code': 404,
                }), 404
            return quart.jsonify(**{
                'msg': '',
                'code': 200,
                attrs['__resource__']: data
            })

        get.__name__ = attrs['__resource__'] + '_get'

        async def put(id):
            """
            新增的路由
            :return:
            """
            nonlocal attrs
            body = await quart.request.json
            try:
                await attrs['__controller__'].put(id, body)
            except BusinessError as e:
                return quart.jsonify(code=e.code, msg=e.err_info), e.http_code
            return quart.jsonify(code=200, msg='')

        put.__name__ = attrs['__resource__'] + '_name'

        async def delete(id):
            """
            删除的路由
            :param id:
            :return:
            """
            nonlocal attrs
            try:
                await attrs['__controller__'].put(id, {'deleted_at': datetime.datetime.now()})
            except BusinessError as e:
                return quart.jsonify(code=e.code, msg=e.err_info), e.http_code
            return quart.jsonify(code=200, msg='')
            delete.__name__ = attrs['__resource__'] + '_delete'

        async def query_and_post():
            """
            处理 查询和新增
            :return:
            """
            nonlocal attrs
            body = await quart.request.json
            method = body.get("_method") or "POST"

            if method == 'GET':
                query, pager, sorter = attrs['__url_condition__'](body.get("_args"))
                try:
                    res, count = await asyncio.gather(attrs['__controller__'].query(query, pager, sorter),
                                                  attrs['__controller__'].count(query))
                except BusinessError as e:
                    return quart.jsonify(code=e.code, msg=e.err_info), e.http_code
                return quart.jsonify(**{
                    'msg': '',
                    'code': 200,
                    attrs['__resource__'] + 's': res,
                    'total': count
                })
            else:
                await cls.__controller__.insert(body)
                return quart.jsonify(code=200, msg='')

        query_and_post.__name__ = attrs['__resource__'] + '_query_and_post'

        attrs['__blueprint__'].route(path="/<int:id>", methods=['GET'])(get)
        attrs['__blueprint__'].route(path="/<int:id>", methods=['PUT'])(put)
        attrs['__blueprint__'].route(path="/<int:id>", methods=['DELETE'])(delete)
        attrs['__blueprint__'].route(path="", methods=['POST'])(query_and_post)

        return type.__new__(cls, name, bases, attrs)


class BaseQuartHandler(metaclass=QuartHandlerMeta):
    pass
