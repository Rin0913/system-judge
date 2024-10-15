from datetime import datetime
from flask import jsonify, request, Blueprint, current_app, abort

problem_bp = Blueprint('problem', __name__)


@problem_bp.route('/', methods=['POST'])
def create_problem():
    problem_id = current_app.problem_repository.create()
    return jsonify({'problem_id': problem_id})

@problem_bp.route('/<string:problem_id>', methods=['PUT'])
def update_problem(problem_id):

    def f_time(time):
        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    problem_name = request.json.get('problem_name')
    start_time = f_time(request.json.get('start_time'))
    deadline = f_time(request.json.get('deadline'))
    subtasks = request.json.get('subtasks')
    playbooks = request.json.get('playbooks')

    current_app.problem_repository.clear_content(problem_id)
    result = current_app.problem_repository.update(problem_id,
                                                   problem_name,
                                                   start_time,
                                                   deadline)

    existing_task_name = set()
    for subtask in subtasks:
        if subtask['task_name'] in existing_task_name:
            return jsonify({'successful': False, 'message': 'Conflicting subtasks.'})
        current_app.problem_repository.add_subtask(problem_id,
                                                   subtask['task_name'],
                                                   subtask['point'],
                                                   subtask['script'])
        existing_task_name.add(subtask['task_name'])

    existing_playbook_name = set()
    for playbook in playbooks:
        if playbook['playbook_name'] in existing_playbook_name:
            return jsonify({'successful': False, 'message': 'Conflicting playbooks.'})
        current_app.problem_repository.add_playbook(problem_id,
                                                    playbook['playbook_name'],
                                                    playbook['script'])
        existing_playbook_name.add(playbook['playbook_name'])
    return jsonify({'successful': result})

@problem_bp.route('/<string:problem_id>', methods=['GET'])
def query_problem(problem_id):
    problem_data = current_app.problem_repository.query(problem_id)
    if problem_data is None:
        abort(404)
    return jsonify(problem_data)

@problem_bp.route('/', methods=['GET'])
def list_problems():
    problem_data = current_app.problem_repository.list()
    return jsonify(problem_data)

@problem_bp.route('/<string:problem_id>', methods=['DELETE'])
def del_problem(problem_id):
    result = current_app.problem_repository.delete(problem_id)
    return jsonify({'successful': result})
