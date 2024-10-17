from datetime import datetime
from collections import defaultdict
from flask import jsonify, request, Blueprint, current_app, abort, g
from .utils import access_control

problem_bp = Blueprint('problem', __name__)

@problem_bp.route('/', methods=['GET'])
def list_problems():
    problem_data = current_app.problem_repository.list()
    for p in problem_data:
        del p['image_name']
    return jsonify(problem_data)

@problem_bp.route('/', methods=['POST'])
@access_control.require_login
@access_control.require_admin
def create_problem():
    problem_id = current_app.problem_repository.create()
    return jsonify({'problem_id': problem_id})

@problem_bp.route('/<string:problem_id>', methods=['POST'])
@access_control.require_login
def user_submit(problem_id):
    current_app.submission_repository.create(g.user['uid'], problem_id)
    return jsonify({'sucessfully': True})

@problem_bp.route('/<string:problem_id>', methods=['PUT'])
@access_control.require_login
@access_control.require_admin
def update_problem(problem_id):

    def f_time(time):
        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    def dfs(graph, visited, stack, node, current_path):
        if visited[node] == -1:
            return False
        if visited[node] == 1:
            return True

        visited[node] = -1
        current_path.append(node)

        for neighbor in graph[node]:
            if not dfs(graph, visited, stack, neighbor, current_path):
                return False

        visited[node] = 1
        stack.append(node)
        current_path.pop()
        return True

    def topological_sort(tasks, dependencies):
        graph = defaultdict(list)
        for before, after in dependencies:
            graph[before].append(after)

        visited = defaultdict(int)
        stack = []

        for task in tasks:
            if visited[task] == 0:
                if not dfs(graph, visited, stack, task, []):
                    return None

        return reversed(stack)

    current_app.problem_repository.clear_content(problem_id)
    result = current_app.problem_repository.update(problem_id,
                                                   request.json.get('problem_name'),
                                                   f_time(request.json.get('start_time')),
                                                   f_time(request.json.get('deadline')))
    existing_task_name = set()
    dependencies_list = []
    for subtask in request.json.get('subtasks'):
        if subtask['task_name'] in existing_task_name:
            return jsonify({'successful': False, 'message': 'Conflicting subtasks.'}), 400
        current_app.problem_repository.add_subtask(problem_id,
                                                   subtask['task_name'],
                                                   subtask['point'],
                                                   subtask['script'])
        existing_task_name.add(subtask['task_name'])
        for depend_on in subtask['depend_on']:
            dependencies_list.append([depend_on, subtask['task_name']])

    tsort_result = topological_sort(existing_task_name, dependencies_list)
    if tsort_result is None:
        return jsonify({'successful': False, 'message': 'Circular dependency detected.'}), 400

    for dependency in dependencies_list:
        if dependency[0] not in existing_task_name:
            return jsonify({'successful': False, 'message': 'Not existing dependency.'}), 400

    existing_playbook_name = set()
    for playbook in request.json.get('playbooks'):
        if playbook['playbook_name'] in existing_playbook_name:
            return jsonify({'successful': False, 'message': 'Conflicting playbooks.'}), 400
        current_app.problem_repository.add_playbook(problem_id,
                                                    playbook['playbook_name'],
                                                    playbook['script'])
        existing_playbook_name.add(playbook['playbook_name'])

    problem_data = current_app.problem_repository.query(problem_id)
    image_name = current_app.docker_service.build_image(problem_data)
    current_app.problem_repository.set_image_name(problem_id, image_name)
    current_app.problem_repository.set_order(problem_id, tsort_result)
    return jsonify({'successful': result})

@problem_bp.route('/<string:problem_id>', methods=['GET'])
@access_control.require_login
@access_control.require_admin
def query_problem(problem_id):
    problem_data = current_app.problem_repository.query(problem_id)
    if problem_data is None:
        abort(404)
    return jsonify(problem_data)

@problem_bp.route('/<string:problem_id>', methods=['DELETE'])
@access_control.require_login
@access_control.require_admin
def del_problem(problem_id):
    result = current_app.problem_repository.delete(problem_id)
    return jsonify({'successful': result})
