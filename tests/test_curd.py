import pytest
import threading
import easyapi
import pymysql
import flask as fk
import requests


@pytest.fixture(scope="module", autouse=True)
def flask_app(esayapi_session):
    app = fk.Flask(__name__)
    easyapi.register_api(app=app, view=esayapi_session['handler'],
                         endpoint='user_api',
                         url='/users')
    t = threading.Thread(target=app.run)
    t.start()


@pytest.mark.run(order=1)
def test_post_and_handler(db_session):
    with db_session.cursor() as cursor:
        cursor.execute("""
            truncate table users;
        """)
    # post
    req = requests.post('http://127.0.0.1:5000/users', json={
        'name': 'test',
        'note': 'test'
    })
    print(req)
    assert req.status_code == 200
    resp = req.json()
    assert resp['code'] == 200
    user_id = resp['id']

    # get
    req = requests.get(f"http://127.0.0.1:5000/users/{user_id}")
    assert req.status_code == 200
    resp = req.json()
    assert resp['code'] == 200
    assert resp['user']['id'] == 1


@pytest.mark.run(order=2)
def test_post_and_query(db_session):
    with db_session.cursor() as cursor:
        cursor.execute("""
            truncate table users;
        """)
    # post test1
    req = requests.post('http://127.0.0.1:5000/users', json={
        'name': 'test1',
        'note': 'test'
    })
    print(req)
    assert req.status_code == 200
    resp = req.json()
    assert resp['code'] == 200

    # post test2
    req = requests.post('http://127.0.0.1:5000/users', json={
        'name': 'test2',
        'note': 'test'
    })
    print(req)
    assert req.status_code == 200
    resp = req.json()
    assert resp['code'] == 200

    # query
    req = requests.post('http://127.0.0.1:5000/users', json={
        "_method": "GET",
        "_args": {

        }
    })
    assert req.status_code == 200
    resp = req.json()
    assert resp['code'] == 200
    assert len(resp['users']) == 2

    # complex query
    req = requests.post('http://127.0.0.1:5000/users', json={
        "_method": "GET",
        "_args": {
            'name': 'test2'
        }
    })
    assert req.status_code == 200
    resp = req.json()
    assert resp['code'] == 200
    assert len(resp['users']) == 1
