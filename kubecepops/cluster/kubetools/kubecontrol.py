from kubecepops.core.config import Config

# import yaml
from os import path
from typing import AnyStr, Dict, List, Tuple
from kubernetes import client, config, stream, watch


class K8sApi:

    @staticmethod
    def _k8s_conn_metrics() -> client.CustomObjectsApi:
        config.kube_config.load_kube_config(
            config_file=path.join(path.dirname(path.realpath(__file__)), Config.kube_config))
        conn = client.CustomObjectsApi()
        return conn

    @staticmethod
    def k8s_conn() -> client.CoreV1Api:
        # config 地址用个人的
        config.kube_config.load_kube_config(
            config_file=path.join(path.dirname(path.realpath(__file__)), Config.kube_config))
        conn = client.CoreV1Api()
        return conn

    @staticmethod
    def execute_command(command: List[AnyStr], pod_name: AnyStr):  # 在pod中执行命令
        return stream.stream(K8sApi.k8s_conn().connect_get_namespaced_pod_exec, pod_name, 'default', command=command,
                             stderr=True, stdin=True, stdout=True, tty=True)

    # @staticmethod
    # def create():  # 暂时不可用
    #     config.load_kube_config()
    #     with open(path.join(path.dirname(__file__), "deploy.yaml")) as f:
    #         dep = yaml.safe_load(f)
    #         k8s_apps_v1 = client.AppsV1Api()
    #         resp = k8s_apps_v1.create_namespaced_deployment(
    #             body=dep, namespace="default")
    #         print("Deployment created. status='%s'" % resp.metadata.name)

    @staticmethod
    def create_pod(pod_name: AnyStr, selector: Dict, node_name: AnyStr, image: AnyStr, command: List[AnyStr] = None):
        # 结构体创建pod基本模板
        conn = K8sApi.k8s_conn()
        pod = client.V1Pod()
        pod.metadata = client.V1ObjectMeta(name=pod_name, labels=selector)
        container = client.V1Container(name=pod_name, image=image)
        container.image_pull_policy = Config.image_pull_policy
        if command:
            container.command = command
        # 不要删下面的，可以满足有资源限制需求的pod创建
        # ===============================================================
        # container.resources = {'requests': {'cpu': '200m'}}
        # container.command = ['/bin/bash', '-ce', 'tail -f /dev/null']
        # ===============================================================
        # 下面为测试空pod时持续Running的命令
        # container.args = ['while true; do sleep 10; done;']
        spec = client.V1PodSpec(containers=[container])
        spec.node_name = node_name
        spec.restart_policy = 'OnFailure'
        pod.spec = spec
        conn.create_namespaced_pod(namespace='default', body=pod)

    @staticmethod
    def create_service(service_name: AnyStr, type_: AnyStr, port: int, target_port: int) -> Tuple[AnyStr, Dict]:
        # 返回标签给pod用
        # 结构体创建service基本模板
        conn = K8sApi.k8s_conn()
        meta = client.V1ObjectMeta(namespace='default', name=service_name)
        selector_name = service_name
        body_spec = client.V1ServiceSpec()
        body_spec.type = 'ClusterIP'
        meta.labels = {type_: selector_name}
        body_spec.selector = {type_: selector_name}
        body_spec.ports = []
        # 下面注入service.spec.ports里的各类端口，如果需要暴露多个端口，就要添加到一个列表里
        service_ports = client.V1ServicePort(port=port)  # service_ports.port 这个不是optional，必须写成参数传达
        service_ports.target_port = target_port  # 与制作容器时暴露的端口一致（使用DockerFile中的EXPOSE）
        service_ports.protocol = 'TCP'
        body_spec.ports.append(service_ports)
        # 每多需暴露一个端口即重复一次
        body = client.V1Service(metadata=meta, spec=body_spec)
        service = conn.create_namespaced_service(namespace='default', body=body)
        return service.spec.cluster_ip, {type_: selector_name}  # 返回cluster_ip和meta.labels的dict

    @staticmethod
    def delete_pod(pod_name: AnyStr):  # 删除pod
        conn = K8sApi.k8s_conn()
        conn.delete_namespaced_pod(namespace='default', name=pod_name)

    @staticmethod
    def delete_service(service_name: AnyStr):
        conn = K8sApi.k8s_conn()
        conn.delete_namespaced_service(namespace='default', name=service_name)

    # @staticmethod
    # def print_namespaces():  # 列出 namespaces
    #     conn = K8sApi.k8s_conn()
    #     ret = conn.list_pod_for_all_namespaces(watch=False)
    #     for i in ret.items:
    #         print('%s\t%s\t%s' % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    @staticmethod
    def get_nodes_ip() -> Dict[AnyStr, AnyStr]:
        conn = K8sApi.k8s_conn()
        ret = conn.list_node(watch=False)
        nodes_ip = {}
        for i in ret.items:
            node_name = i.metadata.name
            node_ip = i.status.addresses[0].address
            nodes_ip[node_name] = node_ip
        return nodes_ip

    @staticmethod
    def get_nodes_source() -> Dict:
        conn = K8sApi._k8s_conn_metrics()
        temp = conn.list_cluster_custom_object('metrics.k8s.io', 'v1beta1', 'nodes')
        return temp

    # @staticmethod
    # def get_pod_source() -> Dict:  # 获得所有operator pod的当前资源用量
    #     conn = K8sApi.k8s_conn_metrics()
    #     temp = conn.list_namespaced_custom_object('metrics.k8s.io', 'v1beta1', 'default', 'pods')
    #     return temp

    @staticmethod
    def get_pods_ip(type_: AnyStr) -> Dict[AnyStr, AnyStr]:  # 获得所有type_标签下的pod
        conn = K8sApi.k8s_conn()
        # ret = conn.list_pod_for_all_namespaces(watch=False)
        ret = conn.list_namespaced_pod(namespace='default')
        pods = {}
        for i in ret.items:
            # print('%s\t%s\t%s' % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            if type_ in i.metadata.labels.keys():
                pods[i.metadata.name] = i.status.pod_ip
        return pods

    @staticmethod
    def get_services_ip(type_: AnyStr) -> Dict[AnyStr, AnyStr]:  # 获得所有type_标签下的service
        conn = K8sApi.k8s_conn()
        # ret = conn.list_service_for_all_namespaces(watch=False)
        ret = conn.list_namespaced_service(namespace='default')
        services = {}
        for i in ret.items:
            # print('%s\t%s\t%s\t%s\t%s\n' % (
            #     i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports))
            if type_ in i.metadata.labels.keys():
                services[i.metadata.name] = i.spec.cluster_ip
        return services

    @staticmethod
    def save_log(name: AnyStr, file_path: AnyStr):
        conn = K8sApi.k8s_conn()
        w = watch.Watch()
        file_handle = open(file_path, mode='w')
        for e in w.stream(conn.read_namespaced_pod_log, name=name, namespace='default'):
            file_handle.write(e.strip() + '\n')
            print(e)
        file_handle.close()

    # @staticmethod
    # def patch_pod(pod_name: AnyStr, namespace: AnyStr):  # 只能改镜像和其它一些，资源改不了
    #     conn = K8sApi.k8s_conn()
    #     old_pod = conn.read_namespaced_pod(namespace=namespace, name=pod_name)
    #     old_pod.spec.containers[0].resources = {'requests': {'cpu': '200m'}}
    #     # old_pod.spec.containers[0].resources.requests.cpu = "250m"
    #     conn.patch_namespaced_pod(namespace=namespace, name=pod_name, body=old_pod)

    # @staticmethod
    # def redeploy_pod(pod_name: AnyStr, node_name: AnyStr, namespace: AnyStr):  # 重部署pod使用
    #     conn = K8sApi.k8s_conn()
    #     old_pod = conn.read_namespaced_pod(namespace=namespace, name=pod_name)
    #     selector = old_pod.metadata.labels
    #     image_name = old_pod.spec.containers[0].image
    #     conn.delete_namespaced_pod(namespace=namespace, name=pod_name)
    #
    #     while True:
    #         try:
    #             conn.read_namespaced_pod(namespace=namespace, name=pod_name)
    #         except client.exceptions.ApiException:
    #             K8sApi.create_pod(pod_name=pod_name, selector=selector, node_name=node_name)
    #             break


# 以上都是示例代码，真正运行的时候得自己手写结构体


if __name__ == '__main__':
    K8sApi.k8s_conn()
    # ===============测试代码使用空行================

    # selector_dict1 = K8sApi.create_service(name="lane-4test", port=5123)
    # selector_dict2 = K8sApi.create_service(name="speed-4test", port=5123)
    # selector_dict3 = K8sApi.create_service(name="accident-4test", port=5123)

    # K8sApi.delete_pod(pod_name="lane-test")
    # K8sApi.delete_pod(pod_name="accident-test")
    # K8sApi.delete_pod(pod_name="speed-test")

    # K8sApi.create_pod(pod_name="lane-test", selector={'name': 'lane'},
    #                  node_name="k8s-node1", image_name="nginx:latest")
    # K8sApi.create_pod(pod_name="speed-test", selector={'name': 'speed'},
    #                  node_name="k8s-node2", image_name="nginx:latest")
    # K8sApi.create_pod(pod_name="accident-test", selector={'name': 'accident'},
    #                  node_name="k8s-node3", image_name="nginx:latest")
    # K8sApi.redeploy_pod(pod_name="speed-test", node_name="k8s-node2", namespace="default")

    # ===============测试结束清空空行================
