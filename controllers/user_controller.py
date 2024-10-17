from flask import Blueprint, current_app, g, request, abort
from .utils import access_control

user_bp = Blueprint('auth', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    profile = current_app.ldap_service.authenticate(username, password)
    if profile:
        return current_app.auth_service.issue_token(profile)
    abort(401)

@user_bp.route('/request_vpn', methods=['POST'])
@access_control.require_login
def request_vpn_conf():
    pool = set()
    for i in range(20000, 60000):
        pool.add(i)
    pool = current_app.user_repository.filter_used_wg_id(pool)
    for i in pool:
        result = current_app.wireguard_service.generate_config(i, if_up=False)
        if result is not None:
            user_conf, judge_conf = result
            current_app.user_repository.set_wireguard(g.user['uid'], i, user_conf, judge_conf)
            return {"successful": True}
    return {'successful': False, 'messsage': 'No avaliable port for vpn.'}, 503

@user_bp.route('/whoami', methods=['GET'])
@access_control.require_login
def whoami():
    user = current_app.user_repository.query(g.user['uid'])
    if 'wireguard_conf' in user:
        del user['wireguard_conf']['judge_conf']
    return user

@user_bp.route('/set_credential', methods=['PUT'])
@access_control.require_login
def set_credential():
    credential = request.json.get('credential')
    current_app.user_repository.set_credential(g.user['uid'], credential)
    return {"successful": True}

@user_bp.route('/submit/<string:problem_id>', methods=['POST'])
@access_control.require_login
def user_submit(problem_id):
    user_id = current_app.user_repository.query(g.user['uid'])['_id']
    current_app.submission_repository.create(user_id, problem_id)
    return {'sucessfully': True}

@user_bp.route('/get_user_token', methods=['POST'])
@access_control.require_development_environment
def get_user_token():
    return current_app.auth_service.issue_token({'uid': 'user', 'role': 'user'})

@user_bp.route('/get_admin_token', methods=['POST'])
@access_control.require_development_environment
def get_admin_token():
    return current_app.auth_service.issue_token({'uid': 'user', 'role': 'admin'})
