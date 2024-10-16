import logging

import mongomock
import mongoengine as me
from repositories import SubmissionRepository

me.connect('testdb', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
submission_repository = SubmissionRepository(logging)

def test_create_list_submission():

    assert (uid1 := submission_repository.create(1, 1))
    assert (uid2 := submission_repository.create(1, 1))
    for submission in submission_repository.list(1, 1):
        if submission['_id'] == uid1:
            uid1 = None
        if submission['_id'] == uid2:
            uid2 = None
    assert len(submission_repository.list(1, 2)) == 0
    assert uid1 is None and uid2 is None

def test_add_subtask_result():

    uid = submission_repository.create(1, 1)
    submission_repository.add_result(uid, "Testcase1", 5, "NoOutput.")
    for submission in submission_repository.list(1, 1):
        if submission['_id'] == uid:
            assert submission['subtask_results'][0]['task_name'] == "Testcase1"
            return
    assert 0
