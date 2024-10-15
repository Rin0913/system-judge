import logging
import warnings
from datetime import datetime, timedelta
from sqlalchemy import create_engine

from repositories import ProblemRepository
from config import Config as config

CONNECTION_STRING = (
    f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PSWD}"
    f"@{config.MYSQL_HOST}/{config.MYSQL_DB}"
)
sql_engine = create_engine(CONNECTION_STRING)
problem_repository = ProblemRepository(sql_engine, logging)

def test_create_problem():

    assert (problem_id := problem_repository.create_problem())
    problem_repository.delete_problem(problem_id)
    if problem_repository.query_problem(problem_id):
        warnings.warn(f"Test problem was not deleted for id = {problem_id}.")

def test_list_problem():

    problem_list = set()

    for _ in range(5):
        problem_id = problem_repository.create_problem()
        problem_list.add(problem_id)

    for problem in problem_repository.list_problems():
        if problem['problem_id'] in problem_list:
            problem_list.remove(problem['problem_id'])

    assert len(problem_list) == 0

    for problem_id in problem_list:
        problem_repository.delete_problem(problem_id)
        if problem_repository.query_problem(problem_id):
            warnings.warn(f"Test problem was not deleted for id = {problem_id}.")

def test_delete_problem():

    problem_id = problem_repository.create_problem()
    assert problem_repository.delete_problem(problem_id)
    if problem_repository.query_problem(problem_id):
        warnings.warn(f"Test problem was not deleted for id = {problem_id}.")

def test_update_query_problem():

    problem_id = problem_repository.create_problem()
    problem_name = "testProblem"
    start_time = datetime.now()
    deadline = start_time + timedelta(days=365)
    problem_repository.update_problem(problem_id,
                                      problem_name,
                                      start_time,
                                      deadline)
    problem_data = problem_repository.query_problem(problem_id)

    def ftime(time):
        return time.strftime('%Y-%m-%d')

    assert problem_data['problem_name'] == problem_name
    assert ftime(problem_data['start_time']) == ftime(start_time)
    assert ftime(problem_data['deadline']) == ftime(deadline)
    problem_repository.delete_problem(problem_id)
    if problem_repository.query_problem(problem_id):
        warnings.warn(f"Test problem was not deleted for id = {problem_id}.")
