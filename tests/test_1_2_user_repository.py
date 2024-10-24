import logging
from types import SimpleNamespace

import mongomock
import mongoengine as me
from app.repositories import UserRepository

me.connect('testdb', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
user_repository = UserRepository()
user_repository.init_app(SimpleNamespace(), logging)

def test_create_user():

    assert user_repository.create("tuser1")

def test_query_user():

    user_repository.create("tuser2")
    assert (user_data := user_repository.query("tuser2"))
    assert user_data['name'] == "tuser2"

def test_set_wireguard():

    user_repository.create("tuser3")
    assert user_repository.set_wireguard("tuser3", 1, "test123", "test321")
    assert (user_data := user_repository.query("tuser3"))
    assert user_data['wireguard_conf']['user_conf'] == "test123"
    assert user_data['wireguard_conf']['judge_conf'] == "test321"
    pool = {1, 2, 3, 4, 5}
    pool = user_repository.filter_used_wg_id(pool)
    assert len(pool) == 4

def test_revoke_wireguard():

    user_repository.create("tuser4")
    user_repository.set_wireguard("tuser4", 2, "test123", "test321")
    user_repository.revoke_wireguard("tuser4")
    user_data = user_repository.query("tuser4")
    assert 'wireguard_conf' not in user_data

def test_set_credential():

    user_repository.create("tuser5")
    user_repository.set_credential("tuser5", "abc123")
    user_data = user_repository.query("tuser5")
    assert user_data['credential'] == "abc123"

def test_operate_on_null():
    uid = "tuser"
    assert not user_repository.query(uid)
    assert not user_repository.revoke_wireguard(uid)
    assert not user_repository.set_credential(uid, "")
    assert not user_repository.set_wireguard(uid, 2, "", "")
