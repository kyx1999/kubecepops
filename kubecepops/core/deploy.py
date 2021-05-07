from kubecepops.core.config import Config
from kubecepops.methods.method import Method
from kubecepops.cluster.kubetools.kubecontrol import K8sApi
from kubecepops.models.samples.trafficsystemgraph import TrafficSystemGraph

from typing import Callable
from kubernetes import client


class Deploy:

    @staticmethod
    def do_deploy(method: Callable[..., Method]):  # 部署
        print('Deploying...')

        graph = TrafficSystemGraph()
        if hasattr(method, 'get_plan'):
            plan = method.get_plan(graph)

            addresses = {}
            selectors = {}
            for operator_name in plan.keys():
                service_ip, selector = K8sApi.create_service(operator_name.lower(), 'operator', Config.service_port,
                                                             Config.operator_port)
                addresses[operator_name] = plan[operator_name], service_ip
                selectors[operator_name] = selector

            command = str(addresses)

            deploy_list = graph.get_sorted_deploy_list()

            for operator_name in deploy_list:
                if operator_name in plan.keys():
                    K8sApi.create_pod(operator_name.lower(), selectors[operator_name], plan[operator_name].lower(),
                                      Config.image,
                                      command=['python3', './kubecepops/models/starter.py', command, operator_name,
                                               str(Config.service_port), str(Config.event_quantity),
                                               str(Config.burden_level)])

                    while True:
                        pod = K8sApi.k8s_conn().read_namespaced_pod(namespace='default', name=operator_name.lower())
                        try:
                            if pod.status.container_statuses[0].state.running:
                                break
                        except TypeError:
                            continue

            print('Deploy finished.')
        else:
            print('Deploy failed.')

    @staticmethod
    def clear_deploy():
        print('Clearing...')

        services = K8sApi.get_services_ip('operator').keys()
        for service in services:
            K8sApi.delete_service(service)

        pods = K8sApi.get_pods_ip('operator').keys()
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
    from kubecepops.methods.samples.reinforcementlearning import ReinforcementLearning

    Deploy.do_deploy(ReinforcementLearning)
    Deploy.clear_deploy()
