from flask import jsonify, request, Blueprint, current_app

problem_bp = Blueprint('problem', __name__)

@problem_bp.route('/create', methods=['POST'])
def create_problem():
    problem_id = current_app.problem_repository.create_problem()
    return jsonify({'problem_id': problem_id})

@problem_bp.route('/update/<string:problem_id>', methods=['PUT'])
def update_problem(problem_id):
    problem_name = request.json.get('problem_name')
    start_time = request.json.get('start_time')
    deadline = request.json.get('deadline')
    problem_id = current_app.problem_repository.update_problem_details(problem_id,
                                                                       problem_name,
                                                                       start_time,
                                                                       deadline)
    return jsonify({'problem_id': problem_id})

@problem_bp.route('/<string:problem_id>', methods=['GET'])
def query_problem(problem_id):
    problem_data = current_app.problem_repository.query_problem(problem_id)
    return jsonify(problem_data)

@problem_bp.route('/list', methods=['GET'])
def list_problems():
    problem_data = current_app.problem_repository.list_problems()
    return jsonify(problem_data)

@problem_bp.route('/<string:problem_id>', methods=['DELETE'])
def del_problem(problem_id):
    problem_id = current_app.problem_repository.del_problem(problem_id)
    return jsonify({'problem_id': problem_id})
