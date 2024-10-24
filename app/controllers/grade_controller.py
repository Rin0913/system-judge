from datetime import datetime
from flask import Blueprint, current_app
from .utils import access_control


grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/problems/<int:problem_id>')
@access_control.require_login
@access_control.require_admin
def download_problem(problem_id):

    def convert_time(date_string):
        return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    user_submissions = {}
    result = {}
    deadline = current_app.problem_repository.query(problem_id)['deadline']
    submissions = current_app.submission_repository.fetch_by_problem_id(problem_id)
    for s in submissions:
        if s['user_id'] not in user_submissions:
            user_submissions[s['user_id']] = []
        user_submissions[s['user_id']].append(s)
    user_mapping = current_app.user_repository.query_by_ids(list(user_submissions.keys()))
    for user, submissions_by_user in user_submissions.items():
        username = user_mapping[user]['name']
        user_submissions[user].sort(key=lambda s: (-s['point'], s['creation_time']))
        before_deadline = []
        for s in submissions_by_user:
            if convert_time(s['creation_time']) <= convert_time(deadline):
                before_deadline.append(s)
        last_submission_pt = 0
        highest_pt_before_deadline = 0
        highest_pt = 0
        if before_deadline:
            last_submission_pt = max(before_deadline, key=lambda x: x['creation_time'])['point']
            highest_pt_before_deadline = before_deadline[0]['point']
        highest_pt = user_submissions[user][0]['point']
        result[username] = {
            "score": highest_pt,
            "before_deadline": {
                "score": highest_pt_before_deadline,
                "last_submission_score": last_submission_pt
            }
        }
    return result
