import logging
from types import SimpleNamespace

import mongomock
import mongoengine as me
from app.repositories import SubmissionRepository

me.connect('testdb', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
submission_repository = SubmissionRepository()
submission_repository.init_app(SimpleNamespace(), logging)

def test_create_list_submission():

    assert (uid1 := submission_repository.create(1, 1))
    assert (uid2 := submission_repository.create(1, 1))
    for submission in submission_repository.list(1):
        if submission['_id'] == uid1:
            uid1 = None
        if submission['_id'] == uid2:
            uid2 = None
    assert uid1 is None and uid2 is None

def test_add_subtask_result():

    uid = submission_repository.create(1, 1)
    submission_repository.add_result(uid, "Testcase1", 5, "NoOutput.")
    flag = 0
    for submission in submission_repository.list(1):
        if submission['_id'] == uid:
            if submission['subtask_results'][0]['task_name'] == "Testcase1":
                flag = 1
                break
    assert flag

def test_operate_on_null():
    uid = 10000
    assert not submission_repository.add_result(uid, "", 0, "")
