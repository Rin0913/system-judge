import random
import string
import traceback
import threading
from queue import Queue
from time import sleep
from services import KubernetesService

class JudgeSystem:

    def __init__(self, config, user_repository, submission_repository, problem_repository, logger):
        self.judge_id = ''.join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
        )
        self.task_queue = Queue()

        self.kubernetes_service = KubernetesService(config.get('K8S_KUBE_CONFIG'),
                                                    config.get('K8S_NAMESPACE'))
        self.user_repository = user_repository
        self.submission_repository = submission_repository
        self.problem_repository = problem_repository
        self.logger = logger
        self.thread_num = config.get('WORKER_NUM')

        job_fetcher = threading.Thread(target=self.fetch_job)
        job_fetcher.daemon = True
        job_fetcher.start()

        for _ in range(self.thread_num):
            worker = threading.Thread(target=self.judge_worker)
            worker.daemon = True
            worker.start()

    def get_load(self):
        l = self.task_queue.qsize() / self.thread_num
        busy_condition = 10
        return 1 / (1 + (l / busy_condition))

    def fetch_job(self):
        while True:
            jobs = self.submission_repository.fetch_uncompleted_submissions()
            for job in jobs:
                if job['status'] == f'judging-{self.judge_id}':
                    continue
                self.task_queue.put((job['_id'], job['user_id'], job['problem_id']))
                self.submission_repository.set_status(job['_id'], f'judging-{self.judge_id}')
                self.logger.debug(f"Received job from user {job['user_id']}"
                                  " with status {job['status']}.")
            sleep(2)

    def judge_worker(self):
        self.logger.debug("Worker is ready.")
        while True:
            task = self.task_queue.get()
            self.logger.debug(f"task is {task}")
            submission_id, user_id, problem_id = task
            problem_data = self.problem_repository.query(problem_id)
            user_data = self.user_repository.query_by_id(user_id)
            task_point = {task['task_name']: task['point'] for task in problem_data['subtasks']}
            task_dependencies = {
                    task['task_name']: task['depends_on'] for task in problem_data['subtasks']
            }
            score = 0
            self.submission_repository.clear_result(submission_id)
            task_result = {}
            for task in problem_data['order']:
                try:
                    code, log = (1, "Unable to establish wireguard tunnel.")
                    for dependency in task_dependencies[task]:
                        if not task_result[dependency]:
                            code, log = (2, f"Dependency task {dependency} failed.")
                            break
                    if code == 1 and 'wireguard_conf' in user_data:
                        code, log = self.kubernetes_service.execute_pod(
                            problem_data['image_name'],
                            task,
                            user_data['wireguard_conf']['judge_conf'],
                            user_data['credential'] if 'credential' in user_data else ''
                        )
                except Exception: # pylint: disable=W0718
                    self.logger.error(traceback.format_exc())
                self.logger.debug(f"Finished task {task} with code {code} and log {log}.")
                self.submission_repository.add_result(
                    submission_id,
                    task,
                    task_point[task] * (code == 0),
                    log
                )
                score += task_point[task] * (code == 0)
                task_result[task] = code == 0
            self.submission_repository.score(submission_id, score)
            self.logger.debug(f"Finished submission {submission_id} with score {score}.")
