import random
import string
import traceback
from queue import Queue
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from services import KubernetesService

JUDGE_ID = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
task_queue = Queue()

def fetch_job(submission_repository, logger):
    while True:
        jobs = submission_repository.fetch_uncompleted_submissions()
        for job in jobs:
            if job['status'] == f'judging-{JUDGE_ID}':
                continue
            task_queue.put((job['_id'], job['user_id'], job['problem_id']))
            submission_repository.set_status(job['_id'], f'judging-{JUDGE_ID}')
            logger.debug(f"Received job from user {job['user_id']} with status {job['status']}.")
        sleep(2)

def judge_worker(problem_repository,
                 user_repository,
                 submission_repository,
                 kubernetes_service,
                 logger):
    logger.debug("Worker is ready.")
    while True:
        task = task_queue.get()
        logger.debug(f"task is {task}")
        submission_id, user_id, problem_id = task
        problem_data = problem_repository.query(problem_id)
        user_data = user_repository.query_by_id(user_id)
        task_point = {task['task_name']: task['point'] for task in problem_data['subtasks']}
        score = 0
        for task in problem_data['order']:
            try:
                code, log = (1, "Unable to establish wireguard tunnel.")
                if 'wireguard_conf' in user_data:
                    code, log = kubernetes_service.execute_pod(
                        problem_data['image_name'],
                        task,
                        user_data['wireguard_conf']['judge_conf'],
                        user_data['credential'] if 'credential' in user_data else ''
                    )
            except Exception: # pylint: disable=W0718
                logger.error(traceback.format_exc())
            logger.debug(f"Finished task {task} with code {code} and log {log}.")
            submission_repository.add_result(
                submission_id,
                task,
                task_point[task] * (code == 0),
                log
            )
            score += task_point[task] * (code == 0)
        submission_repository.score(submission_id, score)
        logger.debug(f"Finished submission {submission_id} with score {score}.")

def initialize_judge(config, problem_repository, user_repository, submission_repository, logger):
    kubernetes_service = KubernetesService(config.get('K8S_KUBE_CONFIG'),
                                           config.get('K8S_NAMESPACE'))
    thread_num = config.get('WORKER_NUM')

    executor = ThreadPoolExecutor()
    executor.submit(fetch_job, submission_repository, logger)
    for _ in range(thread_num):
        executor.submit(judge_worker,
                        problem_repository,
                        user_repository,
                        submission_repository,
                        kubernetes_service,
                        logger)
