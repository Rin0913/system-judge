import random
import string
from queue import Queue
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from services import KubernetesService

JUDGE_ID = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
task_queue = Queue()

def fetch_job(submission_repository):
    while True:
        jobs = submission_repository.fetch_uncompleted_submissions()
        for job in jobs:
            if job['status'] == f'juding-{JUDGE_ID}':
                continue
            task_queue.put((job['_id'], job['user_id'], job['problem_id']))
            submission_repository.set_status(job['_id'], f'judging-{JUDGE_ID}')
        sleep(2)

def judge_worker(problem_repository, user_repository, submission_repository, kubernetes_service):
    while True:
        task = None
        while True:
            task = task_queue.get()
            if task is not None:
                break
            sleep(2)
        submission_id, user_id, problem_id = task
        problem_data = problem_repository.query(problem_id)
        user_data = user_repository.query(user_id)
        task_point = {task['task_name']: task['point'] for task in problem_data['subtasks']}
        score = 0
        for task in problem_data['order']:
            code, log = kubernetes_service.execute_pod(
                problem_data['image'],
                task,
                (user_data['wireguard_conf']['judge_conf'], user_data['credential'])
            )
            submission_repository.add_result(
                submission_id,
                task,
                task_point[task] * (code == 0),
                log
            )
            score += task_point[task] * (code == 0)
        submission_repository.score(submission_id, score)

def initialize_judge(config, problem_repository, user_repository, submission_repository):
    kubernetes_service = KubernetesService(config.get('K8S_KUBE_CONFIG'),
                                           config.get('K8S_NAMESPACE'))
    thread_num = config.get('WORKER_NUM')

    executor = ThreadPoolExecutor()
    executor.submit(fetch_job, submission_repository)
    for _ in range(thread_num):
        executor.submit(judge_worker,
                        problem_repository,
                        user_repository,
                        submission_repository,
                        kubernetes_service)
