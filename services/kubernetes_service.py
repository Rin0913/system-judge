import random
import string
from time import sleep
from kubernetes import client, config

class KubernetesService:

    def __init__(self, kube_config=None, namespace=None):
        self.v1 = None
        if kube_config:
            config.load_kube_config(config_file=kube_config)
            self.namespace = namespace
            self.v1 = client.CoreV1Api()

    def init_app(self, app, kube_config, namespace):
        app.kubernetes_service = self
        config.load_kube_config(config_file=kube_config)
        self.namespace = namespace
        self.v1 = client.CoreV1Api()

    def __create_config_map(self, name_prefix, wg_config_data):

        config_map_name = f"{name_prefix}"
        config_map_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": config_map_name
            },
            "data": {
                "wg0.conf": wg_config_data
            }
        }

        self.v1.create_namespaced_config_map(namespace=self.namespace, body=config_map_manifest)
        return config_map_name

    def __create_pod(self, name, image, command, config_map_name):

        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": name
            },
            "spec": {
                "containers": [{
                    "name": name,
                    "image": image,
                    "volumeMounts": [{
                        "name": "wg-config",
                        "mountPath": "/etc/wireguard/wg0.conf",
                        "subPath": "wg0.conf"
                    }],
                    "command": command,
                }],
                "volumes": [{
                    "name": "wg-config",
                    "configMap": {
                        "name": config_map_name
                    }
                }],
                "restartPolicy": "Never"
            }
        }

        self.v1.create_namespaced_pod(namespace=self.namespace, body=pod_manifest)

    def __wait_for_pod_completion(self, name):
        while True:
            pod_status = self.v1.read_namespaced_pod_status(name=name, namespace=self.namespace)
            if pod_status.status.phase in ['Succeeded', 'Failed']:
                break
            sleep(1)

    def __get_log(self, name):
        log = self.v1.read_namespaced_pod_log(name=name, namespace=self.namespace)
        return log

    def __get_exit_code(self, name):
        pod_status = self.v1.read_namespaced_pod_status(name=name, namespace=self.namespace)
        container_statuses = pod_status.status.container_statuses
        if container_statuses and container_statuses[0].state.terminated:
            exit_code = container_statuses[0].state.terminated.exit_code
            return exit_code
        return None

    def __delete_resources(self, name, config_map_name):
        self.v1.delete_namespaced_pod(name=name,
                                      namespace=self.namespace,
                                      body=client.V1DeleteOptions())
        self.v1.delete_namespaced_config_map(name=config_map_name,
                                             namespace=self.namespace,
                                             body=client.V1DeleteOptions())

    def execute_pod(self, image, task_name, wg_config_data):

        def generate_random_string(length=32):
            characters = string.ascii_lowercase + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        name = generate_random_string()
        command = ["/bin/bash", "/app/default.sh", f"{task_name}.sh"]
        config_map_name = self.__create_config_map(f"{image}-{name}", wg_config_data)
        self.__create_pod(name, image, command, config_map_name)
        self.__wait_for_pod_completion(name)
        result = (self.__get_exit_code(name), self.__get_log(name))
        self.__delete_resources(name, config_map_name)
        return result
