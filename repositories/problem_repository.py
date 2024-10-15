from datetime import datetime
from sqlalchemy.orm import scoped_session, sessionmaker  # Third-party imports
from models import db
from .utils import managed_session  # First-party imports


class ProblemRepository:

    def __init__(self, sql_engine=None, logger=None):
        self.sql_engine = sql_engine
        self.session_factory = scoped_session(sessionmaker(bind=self.sql_engine))
        self.logger = logger

    def init_app(self, app, sql_engine, logger):
        app.problem_repository = self
        self.sql_engine = sql_engine
        self.session_factory = scoped_session(sessionmaker(bind=self.sql_engine))
        self.logger = logger

    def create(self, problem_name="newProblem"):
        with managed_session(self.session_factory, self.logger) as session:
            problem = db.Problem(problem_name=problem_name)
            session.add(problem)
            session.commit()
            return problem.id
        return 0

    def list(self):
        with managed_session(self.session_factory, self.logger) as session:
            problems = session.query(db.Problem).filter_by(is_valid=True).all()
            problem_data = []
            for problem in problems:
                problem_data.append({
                    "problem_id": problem.id,
                    "problem_name": problem.problem_name,
                    "created_time": problem.created_time,
                    "start_time": problem.start_time,
                    "deadline": problem.deadline,
                    "allow_submission": problem.allow_submission,
                })
            return problem_data

    def query(self, problem_id):
        with managed_session(self.session_factory, self.logger) as session:
            problem = session.query(db.Problem).filter_by(id=problem_id, is_valid=True).first()
            if problem:
                problem_data = {
                    "problem_id": problem.id,
                    "problem_name": problem.problem_name,
                    "created_time": problem.created_time,
                    "start_time": problem.start_time,
                    "deadline": problem.deadline,
                    "allow_submission": problem.allow_submission,
                }
                return problem_data
        return None

    def delete(self, problem_id):
        with managed_session(self.session_factory, self.logger) as session:
            problem = session.query(db.Problem).filter_by(id=problem_id, is_valid=True).first()
            if problem:
                problem.is_valid = False
                session.commit()
                return problem.id
            return 0
        return 0

    def update(self, problem_id, problem_name, start_time, deadline):
        current_time = datetime.now()
        allow_submissions = False

        if start_time <= current_time < deadline:
            allow_submissions = True

        with managed_session(self.session_factory, self.logger) as session:
            problem = session.query(db.Problem).filter_by(id=problem_id).first()
            if problem:
                problem.problem_name = problem_name
                problem.allow_submissions = allow_submissions
                problem.start_time = start_time
                problem.deadline = deadline
                session.commit()
                return True
        return False
