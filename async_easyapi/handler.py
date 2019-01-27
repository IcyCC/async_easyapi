import asyncio
import functools
import quart
from quart import views
import datetime
from .util import str2hump, DefaultUrlCondition
from .errors import BusinessError


class QuartHandlerMeta(views.MethodViewType):

    def __new__(cls, name, bases, attrs):
        """

        :param name:
        :param bases:
        :param attrs:
        :return:
        """
        if "BaseHandler" in name:
            return type.__new__(cls, name, bases, attrs)

        attrs['__resource__'] = attrs.get('__resource__') or str2hump(name[:-7])
        attrs['__url_condition__'] = attrs.get('__url_condition__') or DefaultUrlCondition
        if not attrs.get('__controller__'):
            raise NotImplementedError("Handler require a  controller.")

        return type.__new__(cls, name, bases, attrs)


class BaseQuartHandler(views.MethodView, metaclass=QuartHandlerMeta):

    async def get(self, id: int):
        """
        获取单个资源
        :param id:
        :return:
        """
        try:
            data = await self.__controller__.get(id)
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
            self.__resource__: data
        })

    async def put(self, id):
        """
        新增的路由
        :return:
        """
        body = await quart.request.json
        try:
            await self.__controller__.put(id, body)
        except BusinessError as e:
            return quart.jsonify(code=e.code, msg=e.err_info), e.http_code
        return quart.jsonify(code=200, msg='')

    async def delete(self, id):
        """
        删除的路由
        :param id:
        :return:
        """
        try:
            await self.__controller__.put(id, {'deleted_at': datetime.datetime.now()})
        except BusinessError as e:
            return quart.jsonify(code=e.code, msg=e.err_info), e.http_code
        return quart.jsonify(code=200, msg='')

    async def post(self):
        """
        处理 查询和新增
        :return:
        """
        body = await quart.request.json
        method = body.get("_method") or "POST"

        if method == 'GET':
            query, pager, sorter = self.__url_condition__.parser(body.get("_args"))
            try:
                res, count = await self.__controller__.query(query, pager, sorter)

            except BusinessError as e:
                return quart.jsonify(code=e.code, msg=e.err_info), e.http_code
            return quart.jsonify(**{
                'msg': '',
                'code': 200,
                self.__resource__ + 's': res,
                'total': count
            })
        else:
            await self.__controller__.insert(body)
            return quart.jsonify(code=200, msg='')


def register_api(app, view, endpoint: str, url: str, pk='id', pk_type='int'):
    """
    将一个handler类的路由注册到app里
    :param app: 注册的app
    :param view: 试图类
    :param endpoint: 挂载
    :param url: 链接
    :param pk: 主键
    :param pk_type: 类型
    :return:
    """
    view_func = view.as_view(endpoint)
    app.add_url_rule(url,
                     view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s/<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])
