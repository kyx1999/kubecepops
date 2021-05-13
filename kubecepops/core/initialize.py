from kubecepops.core.config import Config
from kubecepops.cluster.kubetools.kubecontrol import K8sApi

from kubernetes import client


class Initialize:

    @staticmethod
    def do_initialize():  # 用于部署测量node间延时的所需的nginx，主要被Greedy算法所用
        print('Initializing...')

        node_names = K8sApi.get_nodes_ip().keys()
        for node_name in node_names:
            K8sApi.create_service(node_name.lower(), 'initialize', Config.nginx_port, 80)

        for node_name in node_names:
            K8sApi.create_pod(node_name.lower(), {'initialize': node_name.lower()}, node_name.lower(), 'nginx')

        for node_name in node_names:
            while True:
                pod = K8sApi.k8s_conn().read_namespaced_pod(namespace='default', name=node_name.lower())
                try:
                    if pod.status.container_statuses[0].state.running:
                        break
                except TypeError:
                    continue

        print('Initialize finished.')

    @staticmethod
    def clear_initialize():
        print('Clearing...')

        services = K8sApi.get_services_ip('initialize').keys()
        for service in services:
            K8sApi.delete_service(service)

        pods = K8sApi.get_pods_ip('initialize').keys()
        for pod in pods:
            K8sApi.delete_pod(pod)

        for pod in pods:
            while True:
                try:
                    K8sApi.k8s_conn().read_namespaced_pod(namespace='default', name=pod)
                except client.exceptions.ApiException:
                    break

        print('Clear finished.')


if __name__ == '__main__':
    Initialize.do_initialize()
    Initialize.clear_initialize()
