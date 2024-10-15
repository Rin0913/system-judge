from flask import Blueprint, current_app, g
from .utils import access_control

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@access_control.require_development_environment
def get_user_token():
    return current_app.auth_service.issue_token({'uid': 'user', 'role': 'user'})

@auth_bp.route('/login_admin', methods=['POST'])
@access_control.require_development_environment
def get_admin_token():
    return current_app.auth_service.issue_token({'uid': 'user', 'role': 'admin'})

@auth_bp.route('/whoami', methods=['GET'])
@access_control.require_login
def whoami():
    return g.user

@auth_bp.route('/admin_only', methods=['GET'])
@access_control.require_login
@access_control.require_admin
def test_admin():
    return "OK"
