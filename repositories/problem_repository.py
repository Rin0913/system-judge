from datetime import datetime
from models import Problem


class ProblemRepository:

    def __init__(self, logger=None):
        self.logger = logger

    def init_app(self, app, logger):
        app.problem_repository = self
        self.logger = logger

    def create(self, problem_name="New Problem"):
        problem = Problem(
            problem_name=problem_name,
            subtasks=[],
            playbooks=[],
            allow_submission=False
        )
        problem.save()
        return problem.id


    def list(self):
        problems = Problem.objects(is_valid=True).only("id",
                                                       "problem_name",
                                                       "start_time",
                                                       "deadline")
        return [problem.to_mongo().to_dict() for problem in problems]

    def query(self, problem_id):
        return Problem.objects(is_valid=True, id=problem_id).first()

    def delete(self, problem_id):
        self.query(problem_id).update(is_valid=False)

    def update(self, problem_id, problem_name, start_time, deadline):
        current_time = datetime.now()
        allow_submissions = False

        if start_time <= current_time < deadline:
            allow_submissions = True

        problem = self.query(problem_id)
        if problem:
            problem.problem_name = problem_name
            problem.allow_submissions = allow_submissions
            problem.start_time = start_time
            problem.deadline = deadline
            problem.save()
            return True
        return False
