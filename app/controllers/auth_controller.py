from flask import Blueprint, current_app, request, abort

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    the format of profile would be like:
    {
        "uid": username,
        "role": role
    }
    and the role would be 'admin' or 'user'.
    """
    username = request.json.get('username', 'nobody')
    password = request.json.get('password', '')
    profile = current_app.ldap_service.authenticate(username, password)
    if profile:
        return current_app.auth_service.issue_token(profile)
    abort(401)
