import pytest
import  threading
import easyapi
import pymysql
import flask as fk
import requests


@pytest.fixture(scope="module",autouse=True)
def flask_app(esayapi_session):
    app = fk.Flask(__name__)
    easyapi.register_api(app=app, view=esayapi_session['handler'],
                         endpoint='user_api',
                         url='/users')
    t = threading.Thread(target=app.run)
    t.start()


def test_post_handler():
    req = requests.post('http://127.0.0.1:5000/users', json={
        'name': 'test',
        'note': 'test'
    })

    resp = req.json()

    assert resp['code'] == 200
