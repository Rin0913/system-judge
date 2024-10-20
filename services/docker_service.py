import tempfile
import os
import shutil
import random
import string
import docker

class DockerService:

    def __init__(self):
        self.client = docker.from_env()
        self.harbor_host = None
        self.harbor_project = None
        self.logger = None
        self.username = None
        self.password = None

    def init_app(self, app, config, logger):
        app.docker_service = self
        self.username = config.get('HARBOR_USER')
        self.password = config.get('HARBOR_PASSWORD')
        self.harbor_host = config.get('HARBOR_HOST')
        self.harbor_project = config.get('HARBOR_PROJECT')
        self.logger = logger

    def build_image(self, problem_data):

        self.client.login(username=self.username,
                          password=self.password,
                          registry=self.harbor_host)

        def generate_random_string(length=64):
            characters = string.ascii_lowercase + string.digits
            random_string = ''.join(random.choices(characters, k=length))
            return random_string

        temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(temp_dir, "scripts/"))

        # Copy from MongoDB to temp_dir
        for task in problem_data['subtasks']:
            file_path = os.path.join(temp_dir, f"scripts/{task['task_name']}.sh")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(task['script'])
        for playbook in problem_data['playbooks']:
            file_path = os.path.join(temp_dir, f"scripts/{playbook['playbook_name']}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(playbook['script'])

        # Copy the templates
        shutil.copyfile('./templates/dockerfile.temp', os.path.join(temp_dir, 'Dockerfile'))
        shutil.copyfile('./templates/default.sh.temp', os.path.join(temp_dir, 'default.sh'))
        shutil.copyfile('./templates/ansible.cfg.temp', os.path.join(temp_dir, 'ansible.cfg'))

        # Build the image
        image_name = generate_random_string(16)
        image_tag = f"{self.harbor_host}/{self.harbor_project}/{image_name}:latest"
        _, logs = self.client.images.build(path=temp_dir, tag=image_tag)

        for log in logs:
            self.logger.debug(log)
        self.logger.info(self.client.images.push(image_tag))

        shutil.rmtree(temp_dir)
        return image_tag
