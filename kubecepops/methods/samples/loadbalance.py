from kubecepops.core.config import Config
from kubecepops.cluster.status import Status
from kubecepops.methods.method import Method
from kubecepops.models.templates.graph import Graph

from typing import AnyStr, Dict

''' 
    LoadBalance算法解释：
        负载均衡算法将获取当前集群状态（可用资源信息），根据剩余资源数量，部署在剩余资源最多的node上，
        具体执行时，一方面Config中规定了一个node最多能部署多少operator，因此每个node可部署的剩余量为排序的第一依据，第二依据为内存
'''


class LoadBalance(Method):

    @staticmethod
    def get_plan(graph: Graph) -> Dict[AnyStr, AnyStr]:
        node_source = Status.get_nodes_with_allocatable_source()
        node_source_list = list(node_source.keys())
        node_source_list.sort(key=lambda x: node_source[x]['mem'], reverse=False)  # 按内存已使用从少到多

        plan = {}
        i = 0
        dest_node = node_source_list[i]
        i = (i + 1) % len(node_source_list)
        for operator_name in graph.get_operator_names():
            if operator_name == 'DataSource':
                plan[operator_name] = Config.source_node
            elif operator_name == 'DataConsumer':
                plan[operator_name] = Config.consumer_node
            else:
                plan[operator_name] = dest_node
                dest_node = node_source_list[i]
                i = (i + 1) % len(node_source_list)

        return plan


if __name__ == '__main__':
    from kubecepops.models.samples.trafficsystemgraph import TrafficSystemGraph

    print(LoadBalance.get_plan(TrafficSystemGraph()))
