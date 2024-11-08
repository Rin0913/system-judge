from flask import jsonify, request, Blueprint, current_app, abort, g
from .utils import access_control

problem_bp = Blueprint('problem', __name__)

@problem_bp.route('/', methods=['GET'])
@access_control.authenticate
def list_problems():
    problem_data = current_app.problem_repository.list()
    is_admin = True
    if (not hasattr(g, 'user')) or g.user is None or g.user['role'] != 'admin':
        is_admin = False
    for p in problem_data:
        if 'image_name' in p:
            del p['image_name']
        if 'order' in p:
            del p['order']
        if 'dockerfile' in p:
            del p['dockerfile']
        del p['description']
    for i in range(len(problem_data) - 1, -1, -1):
        if (not problem_data[i]['allow_submission']) and (not is_admin):
            del problem_data[i]
    return jsonify(problem_data)

@problem_bp.route('/', methods=['POST'])
@access_control.require_login
@access_control.require_admin
def create_problem():
    problem_id = current_app.problem_repository.create()
    return jsonify({'problem_id': problem_id})

@problem_bp.route('/<int:problem_id>', methods=['PUT'])
@access_control.require_login
@access_control.require_admin
def update_problem(problem_id):
    try:
        current_app.problem_service.validate(request.json)
    except ValueError as e:
        return {"successful": False, "message": str(e)}, 400
    except TypeError:
        abort(400)
    current_app.problem_service.submit(problem_id, request.json)
    return {"successful": True}

@problem_bp.route('/<string:problem_id>', methods=['GET'])
@access_control.authenticate
def query_problem(problem_id):
    problem_data = current_app.problem_repository.query(problem_id)
    if problem_data is None:
        abort(404)
    if (not hasattr(g, 'user')) or g.user is None or g.user['role'] != 'admin':
        del problem_data['subtasks']
        del problem_data['playbooks']
        del problem_data['dockerfile']
    if 'image_name' in problem_data:
        del problem_data['image_name']
    if 'order' in problem_data:
        del problem_data['order']
    if g.user:
        user_id = current_app.user_repository.query(g.user['uid'])['_id']
        cooldown_key = f"cooldown_p{problem_id}_u{user_id}"
        problem_data['cooldown'] = current_app.redis.ttl(cooldown_key)
    return jsonify(problem_data)

@problem_bp.route('/<string:problem_id>', methods=['DELETE'])
@access_control.require_login
@access_control.require_admin
def del_problem(problem_id):
    result = current_app.problem_repository.delete(problem_id)
    return jsonify({'successful': result})
