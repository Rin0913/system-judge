import json
from flask import Blueprint, current_app, request, abort
from .utils import access_control


grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/problems/<int:problem_id>')
@access_control.require_login
@access_control.require_admin
def download_grade(problem_id):
    file_format = request.args.get('type', 'json').lower()
    json_result = current_app.grade_service.export(problem_id)
    if file_format == 'json':
        return json.dumps(json_result)
    if file_format == 'csv':
        csv_result = ["username,highest_score,"
                      "highest_score_before_deadline,last_submission_before_deadline"]
        for username, entry in json_result.items():
            csv_result.append(f"{username},{entry['highest_score']},"
                              f"{entry['before_deadline']['highest_score']},"
                              f"{entry['before_deadline']['last_submission_score']}")
        return '\n'.join(csv_result)
    abort(400)
