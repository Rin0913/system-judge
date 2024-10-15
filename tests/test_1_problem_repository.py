import logging
import warnings
from datetime import datetime, timedelta

import mongomock
import mongoengine as me
from repositories import ProblemRepository

me.connect('testdb', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
problem_repository = ProblemRepository(logging)

def test_create_problem():

    assert (problem_id := problem_repository.create())
    problem_repository.delete(problem_id)
    if problem_repository.query(problem_id):
        warnings.warn(f"Test problem was not deleted for id = {problem_id}.")

def test_list_problems():

    problem_list = set()

    for _ in range(5):
        problem_id = problem_repository.create()
        problem_list.add(problem_id)

    for problem in problem_repository.list():
        if problem['_id'] in problem_list:
            problem_list.remove(problem['_id'])

    assert len(problem_list) == 0

    for problem_id in problem_list:
        problem_repository.delete(problem_id)
        if problem_repository.query(problem_id):
            warnings.warn(f"Test problem was not deleted for id = {problem_id}.")

def test_delete_problem():

    problem_id = problem_repository.create()
    problem_repository.delete(problem_id)
    assert problem_repository.query(problem_id) is None
    if problem_repository.query(problem_id):
        warnings.warn(f"Test problem was not deleted for id = {problem_id}.")

def test_update_query_problem():

    problem_id = problem_repository.create()
    problem_name = "testProblem"
    start_time = datetime.now()
    deadline = start_time + timedelta(days=365)
    problem_repository.update(problem_id,
                                      problem_name,
                                      start_time,
                                      deadline)
    problem_data = problem_repository.query(problem_id)

    def ftime(time):
        return time.strftime('%Y-%m-%d')

    assert problem_data['problem_name'] == problem_name
    assert ftime(problem_data['start_time']) == ftime(start_time)
    assert ftime(problem_data['deadline']) == ftime(deadline)
    problem_repository.delete(problem_id)
    if problem_repository.query(problem_id):
        warnings.warn(f"Test problem was not deleted for id = {problem_id}.")
