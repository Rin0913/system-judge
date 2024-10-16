import logging

import mongomock
import mongoengine as me
from repositories import UserRepository

me.connect('testdb', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
user_repository = UserRepository(logging)

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

def test_revoke_wireguard():

    user_repository.create("tuser4")
    user_repository.set_wireguard("tuser4", 2, "test123", "test321")
    user_repository.revoke_wireguard("tuser4")
    user_data = user_repository.query("tuser4")
    assert 'wireguard_conf' not in user_data
