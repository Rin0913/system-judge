from datetime import datetime
from models import Problem, Subtask, Playbook
from .utils import mongo_utils


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
        problems = Problem.objects(is_valid=True)
        problems = [mongo_utils.mongo_to_dict(problem) for problem in problems]
        for problem in problems:
            del problem['subtasks']
            del problem['playbooks']
        return problems

    def __query(self, problem_id):
        return Problem.objects(is_valid=True, id=problem_id).first()

    def query(self, problem_id):
        problem = self.__query(problem_id)
        if problem:
            return mongo_utils.mongo_to_dict(problem)
        return None

    def delete(self, problem_id):
        problem = self.__query(problem_id)
        if problem:
            problem.update(is_valid=False)
            return True
        return False

    def update(self, problem_id, problem_name, start_time, deadline):
        current_time = datetime.now()
        allow_submissions = False

        if start_time <= current_time < deadline:
            allow_submissions = True

        problem = self.__query(problem_id)
        if problem:
            problem.problem_name = problem_name
            problem.allow_submissions = allow_submissions
            problem.start_time = start_time
            problem.deadline = deadline
            problem.save()
            return True
        return False

    def clear_content(self, problem_id):

        problem = self.__query(problem_id)
        if not problem:
            return False

        problem.subtasks = []
        problem.playbooks = []
        problem.save()

        return True

    def add_subtask(self, problem_id, task_name, point, script):

        problem = self.__query(problem_id)
        if not problem:
            return False

        subtask = Subtask(
            task_name=task_name,
            point=point,
            script=script
        )
        problem.subtasks.append(subtask)
        problem.save()
        return True

    def add_playbook(self, problem_id, playbook_name, script):

        problem = self.__query(problem_id)
        if not problem:
            return False

        playbook = Playbook(
            playbook_name=playbook_name,
            script=script
        )
        problem.playbooks.append(playbook)
        problem.save()
        return True

    def set_image_name(self, problem_id, image_name):
        problem = self.__query(problem_id)
        if problem:
            problem.update(image_name=image_name)
            return True
        return False

    def set_order(self, problem_id, order):
        problem = self.__query(problem_id)
        if problem:
            problem.update(order=order)
            return True
        return False

    def update_description(self, problem_id, description):
        problem = self.__query(problem_id)
        if problem:
            problem.update(description=description)
            return True
        return False
