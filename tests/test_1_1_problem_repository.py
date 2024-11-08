import logging
from datetime import datetime, timedelta
from types import SimpleNamespace

import mongomock
import mongoengine as me
from app.repositories import ProblemRepository

me.connect('testdb', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
problem_repository = ProblemRepository()
problem_repository.init_app(SimpleNamespace(), logging)

def test_create_problem():

    assert (problem_id := problem_repository.create())
    problem_repository.delete(problem_id)

def test_list_problems():

    problem_list = set()

    for _ in range(5):
        problem_id = problem_repository.create()
        problem_list.add(problem_id)

    for problem in problem_repository.list():
        if problem['_id'] in problem_list:
            problem_list.remove(problem['_id'])

    assert len(problem_list) == 0

def test_delete_problem():

    problem_id = problem_repository.create()
    problem_repository.delete(problem_id)
    assert problem_repository.query(problem_id) is None

def test_update_query_problem():

    problem_id = problem_repository.create()
    problem_name = "testProblem"
    start_time = datetime.now()
    deadline = start_time + timedelta(days=365)
    problem_repository.update_info(problem_id,
                                   problem_name,
                                   start_time,
                                   deadline,
                                   True)
    problem_repository.set_image(problem_id, '', 'a')
    problem_repository.set_order(problem_id, ['a'])
    problem_data = problem_repository.query(problem_id)

    def f_time(time):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    assert problem_data['problem_name'] == problem_name
    assert problem_data['start_time'] == f_time(start_time)
    assert problem_data['deadline'] == f_time(deadline)
    assert 'image_name' in problem_data and problem_data['image_name'] == 'a'
    assert 'order' in problem_data and problem_data['order'] == ['a']

    problem_repository.add_subtask(problem_id, 'test_task', 100, 'true')
    problem_repository.add_playbook(problem_id, 'test_playbook', '')
    problem_data = problem_repository.query(problem_id)
    assert len(problem_data['subtasks']) > 0
    assert problem_data['subtasks'][0]['task_name'] == 'test_task'
    assert len(problem_data['playbooks']) > 0
    assert problem_data['playbooks'][0]['playbook_name'] == 'test_playbook'

    problem_repository.clear_content(problem_id)
    problem_data = problem_repository.query(problem_id)
    assert len(problem_data['subtasks']) == 0
    assert len(problem_data['playbooks']) == 0

    problem_repository.delete(problem_id)

def test_operate_on_null():
    problem_id = 10000
    now = datetime.now()
    assert not problem_repository.query(problem_id)
    assert not problem_repository.delete(problem_id)
    assert not problem_repository.update_info(problem_id, '', now, now, True)
    assert not problem_repository.clear_content(problem_id)
    assert not problem_repository.add_subtask(problem_id, '', 0, '')
    assert not problem_repository.add_playbook(problem_id, '', '')
    assert not problem_repository.set_image(problem_id, '', '')
    assert not problem_repository.set_order(problem_id, [])
