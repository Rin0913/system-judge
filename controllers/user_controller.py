from flask import Blueprint, current_app, g, request, abort
from .utils import access_control

user_bp = Blueprint('user', __name__)

@user_bp.route('/request_vpn', methods=['POST'])
@access_control.require_login
def request_vpn_conf():
    lock = current_app.redis_dlm.lock("vpn_request", 2000)
    if lock:
        pool = set()
        for i in range(40000):
            pool.add(i)
        user_data = current_app.user_repository.query(g.user['uid'])
        wg_id = None
        if 'wireguard_conf' in user_data:
            wg_id = user_data['wireguard_conf']['id']
        pool = current_app.user_repository.filter_used_wg_id(pool)
        for i in pool:
            result = current_app.wireguard_service.generate_config(i)
            if result is not None:
                if wg_id is not None:
                    current_app.wireguard_service.revoke_config(wg_id)
                user_conf, judge_conf = result
                current_app.user_repository.set_wireguard(g.user['uid'], i, user_conf, judge_conf)
                current_app.redis_dlm.unlock(lock)
                return {"successful": True}
        current_app.redis_dlm.unlock(lock)
        return {'successful': False, 'messsage': 'No avaliable port for vpn.'}, 503
    return {'successful': False, 'message': 'This resource is locked, try again later'}, 429

@user_bp.route('/whoami', methods=['GET'])
@access_control.require_login
def whoami():
    user = current_app.user_repository.query(g.user['uid'])
    if 'wireguard_conf' in user:
        del user['wireguard_conf']['judge_conf']
    return user

@user_bp.route('/submissions', methods=['GET'])
@access_control.require_login
def list_my_submissions():
    user_id = current_app.user_repository.query(g.user['uid'])['_id']
    result = []
    for problem in current_app.problem_repository.list():
        result += current_app.submission_repository.list(user_id, problem['_id'])

    for r in result:
        del r['subtask_results']

    result.sort(key=lambda x: x['creation_time'])
    return result

@user_bp.route('/submission/<int:submission_id>', methods=['GET'])
@access_control.require_login
def get_submission(submission_id):
    user_id = current_app.user_repository.query(g.user['uid'])['_id']
    result = current_app.submission_repository.query(submission_id)
    if result is None:
        abort(404)
    if result['user_id'] == user_id or g.user['role'] == 'admin':
        return result
    abort(403)

@user_bp.route('/set_credential', methods=['PUT'])
@access_control.require_login
def set_credential():
    credential = request.json.get('credential')
    current_app.user_repository.set_credential(g.user['uid'], credential)
    return {"successful": True}

@user_bp.route('/submit/<int:problem_id>', methods=['POST'])
@access_control.require_login
def user_submit(problem_id):
    problem_data = current_app.problem_repository.query(problem_id)
    if g.user['role'] == 'admin' or problem_data["allow_submission"]:
        user_id = current_app.user_repository.query(g.user['uid'])['_id']
        current_app.submission_repository.create(user_id, problem_id)
        return {'sucessfully': True}
    abort(403)

@user_bp.route('/get_user_token', methods=['POST'])
@access_control.require_development_environment
def get_user_token():
    return current_app.auth_service.issue_token({'uid': 'user', 'role': 'user'})

@user_bp.route('/get_admin_token', methods=['POST'])
@access_control.require_development_environment
def get_admin_token():
    return current_app.auth_service.issue_token({'uid': 'user', 'role': 'admin'})
