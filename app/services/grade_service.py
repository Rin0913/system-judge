from datetime import datetime


class GradeService:

    def __init__(self,
                 user_repository=None,
                 problem_repository=None,
                 submission_repository=None,
                 logger=None):

        self.user_repository = user_repository
        self.problem_repository = problem_repository
        self.submission_repository = submission_repository
        self.logger = logger

    def init_app(self, app, user_repository, problem_repository, submission_repository, logger):

        app.grade_service = self
        self.user_repository = user_repository
        self.problem_repository = problem_repository
        self.submission_repository = submission_repository
        self.logger = logger

    def export(self, problem_id):

        def convert_time(date_string):
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

        user_submissions = {}
        result = {}
        deadline = self.problem_repository.query(problem_id)['deadline']
        submissions = self.submission_repository.fetch_by_problem_id(problem_id)
        for s in submissions:
            if s['user_id'] not in user_submissions:
                user_submissions[s['user_id']] = []
            user_submissions[s['user_id']].append(s)
        user_mapping = self.user_repository.query_by_ids(list(user_submissions.keys()))
        for user, submissions_by_user in user_submissions.items():
            username = user_mapping[user]['name']
            result[username] = {
                "highest_score": 0,
                "before_deadline": {
                    "highest_score": 0,
                    "last_submission_score": 0 
                }
            }
            user_submissions[user].sort(key=lambda s: (-s['point'], s['creation_time']))
            before_deadline = []
            for s in submissions_by_user:
                if convert_time(s['creation_time']) <= convert_time(deadline):
                    before_deadline.append(s)
            if before_deadline:
                result[username]['before_deadline']['last_submission_score'] = max(
                    before_deadline,
                    key=lambda x: x['creation_time']
                )['point']
                result[username]['before_deadline']['highest_score'] = before_deadline[0]['point']
            result[username]['highest_score'] = user_submissions[user][0]['point']
            return result
