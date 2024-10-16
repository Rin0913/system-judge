from models import Submission, SubtaskResult
from .utils import mongo_utils


class SubmissionRepository:

    def __init__(self, logger=None):
        self.logger = logger

    def init_app(self, app, logger):
        app.submission_repository = self
        self.logger = logger

    def create(self, user_id, problem_id):
        submission = Submission(
            user_id=user_id,
            problem_id=problem_id
        )
        submission.save()
        return submission.id

    def list(self, user_id, problem_id):
        submissions = Submission.objects(user_id=user_id, problem_id=problem_id)
        return [mongo_utils.mongo_to_dict(s) for s in submissions]

    def add_result(self, submission_id, task_name, point, log):
        result = SubtaskResult(
            task_name=task_name,
            point=point,
            log=log
        )
        submission = Submission.objects(id=submission_id).first()
        if submission:
            submission.subtask_results.append(result)
            submission.save()
            return True
        return False

    def score(self, submission_id, point):
        submission = Submission.objects(id=submission_id).first()
        if submission:
            submission.update(point=point, status='completed')
            return True
        return False

    def set_status(self, submission_id, status):
        submission = Submission.objects(id=submission_id).first()
        if submission:
            submission.update(status=status)
            return True
        return False

    def fetch_uncompleted_submissions(self):
        submissions = Submission.objects(status__ne='completed')
        return [mongo_utils.mongo_to_dict(s) for s in submissions]
