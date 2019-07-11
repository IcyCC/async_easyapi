import pytest
import threading
import easyapi
import pymysql
import flask as fk
import requests


# @pytest.mark.run(order=1)
# def test_transaction(transaction_session):
#     class UserDao(easyapi.BusinessBaseDao):
#         __tablename__ = 'users'
#         __db__ = transaction_session

#     class ShareDao(easyapi.BusinessBaseDao):
#         __tablename__ = 'shares'
#         __db__ = transaction_session

#     old_user = UserDao.get()
#     old_share = ShareDao.get()
#     try:
#         with easyapi.get_tx(transaction_session) as tx:
#             ctx = easyapi.EasyApiContext(tx)
#             UserDao.insert(ctx=ctx, data={'username': 'test1', 'make': 1})
#             ShareDao.insert(ctx=ctx, data={'username': 'test1', 'note': 'test'})
#     except Exception as e:
#         new_user = UserDao.get()
#         new_share = ShareDao.get()
#         assert new_user['id'] == old_user['id']
#         assert new_share['id'] == old_share['id']
#     new_user = UserDao.get()
#     new_share = ShareDao.get()
#     assert old_share['id'] == new_share['id']
#     assert old_user['id'] == new_user['id']
