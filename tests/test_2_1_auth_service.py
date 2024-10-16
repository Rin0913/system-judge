import logging
from types import SimpleNamespace

import mongomock
import mongoengine as me

from services import AuthService
from repositories import UserRepository

me.connect('testdb', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
user_repository = UserRepository()
user_repository.init_app(SimpleNamespace(), logging)

auth_service = AuthService()
auth_service.init_app(SimpleNamespace(), "salt", user_repository, logging)

def test_issue_authenticate_token():
    profile = {
        "uid": "test_user",
        "role": "test_role"
    }
    token = auth_service.issue_token(profile)
    assert user_repository.query(profile['uid'])
    payload = auth_service.authenticate_token(token)
    assert payload is not None
    assert payload['uid'] == profile['uid'] and payload['role'] == profile['role']

def test_authenticate_failure():
    profile = {
        "uid": "test_user",
        "role": "test_role"
    }
    token = auth_service.issue_token(profile) + 'a'
    assert auth_service.authenticate_token(token) is None

    token = auth_service.issue_token(profile, expire_time=0)
    assert auth_service.authenticate_token(token) is None

    try:
        assert auth_service.authenticate_token('') is None
    except ValueError:
        assert 1
