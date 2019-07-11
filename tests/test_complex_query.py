import pytest
import threading
import easyapi
import pymysql
import flask as fk
import requests

@pytest.mark.run(order=1)
def test_post_and_handler(esayapi_session):
    dao = esayapi_session['dao']
    dao.insert(data={
        'name': 'test2',
        'note': 'test'
    })
    
    user = dao.query(query={dao._like_name: 'test'})
    
    assert user != 0