from collections import defaultdict
from datetime import datetime

class ProblemService:

    def __init__(self, problem_repository=None, docker_service=None):
        self.problem_repository = problem_repository
        self.docker_service = docker_service

    def init_app(self, app, problem_repository, docker_service):
        app.problem_service = self
        self.problem_repository = problem_repository
        self.docker_service = docker_service

    def __topological_sort(self, tasks, dependencies):

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

    def validate(self, problem_data):

        def assert_type(instance, instance_type):
            if not isinstance(instance, instance_type):
                raise TypeError("Wrong type")

        assert_type(problem_data.get('allow_submission'), bool)
        assert_type(problem_data.get('max_cooldown_time'), int)
        assert_type(problem_data.get('min_cooldown_time'), int)

        existing_task_name = set()
        dependencies_list = []

        # Check each subtask is unique
        for subtask in problem_data.get('subtasks'):
            if not subtask['task_name'] or subtask['task_name'] in existing_task_name:
                raise ValueError("Invalid or duplicate subtask name.")

            assert_type(subtask['point'], int)

            existing_task_name.add(subtask['task_name'])
            for depend_on in subtask['depends_on']:
                dependencies_list.append([depend_on, subtask['task_name']])

        # Check if there's circular dependency
        tsort_result = self.__topological_sort(existing_task_name, dependencies_list)
        if tsort_result is None:
            raise ValueError('Circular dependency detected.')

        # Check if there's non-existing dependency
        for dependency in dependencies_list:
            if dependency[0] not in existing_task_name:
                raise ValueError('Not existing dependency.')

        # Check each playbook is unique
        existing_playbook_name = set()
        for playbook in problem_data.get('playbooks'):
            if not playbook['playbook_name'] or playbook['playbook_name'] in existing_playbook_name:
                raise ValueError("Invalid or duplicate playbook name.")
            existing_playbook_name.add(playbook['playbook_name'])

    def submit(self, problem_id, problem_data):

        def f_time(time):
            return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

        # Modify the basic setting
        self.problem_repository.clear_content(problem_id)
        self.problem_repository.update_info(problem_id,
                                            problem_data.get('problem_name'),
                                            f_time(problem_data.get('start_time')),
                                            f_time(problem_data.get('deadline')),
                                            problem_data.get('allow_submission'))
        self.problem_repository.update_cooldown_time(problem_id,
                                                     problem_data.get('min_cooldown_time'),
                                                     problem_data.get('max_cooldown_time'))
        self.problem_repository.update_description(problem_id, problem_data.get('description'))

        # Add subtasks and playbooks
        for subtask in problem_data.get('subtasks'):
            self.problem_repository.add_subtask(problem_id,
                                                subtask['task_name'],
                                                subtask['point'],
                                                subtask['script'],
                                                subtask['depends_on'])

        for playbook in problem_data.get('playbooks'):
            self.problem_repository.add_playbook(problem_id,
                                                 playbook['playbook_name'],
                                                 playbook['script'])

        dockerfile = problem_data.get('dockerfile')

        # Build and upload the image
        problem_data = self.problem_repository.query(problem_id)
        image_name = self.docker_service.build_image(f"problem_{problem_id}_judge_image",
                                                     dockerfile,
                                                     problem_data)
        self.problem_repository.set_image(problem_id,
                                          dockerfile,
                                          image_name)

        existing_task_name = {task['task_name'] for task in problem_data['subtasks']}
        dependencies_list = [
            (dependency, task['task_name'])
                for task in problem_data['subtasks']
                for dependency in task['depends_on']
        ]

        tsort_result = self.__topological_sort(existing_task_name, dependencies_list)
        self.problem_repository.set_order(problem_id, tsort_result)
