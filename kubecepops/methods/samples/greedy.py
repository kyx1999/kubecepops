from kubecepops.core.config import Config
from kubecepops.cluster.status import Status
from kubecepops.methods.method import Method
from kubecepops.models.templates.graph import Graph

from typing import AnyStr, Dict

''' 
    Greedy算法解释：
        贪心算法判断依据为执行部署命令的node到每个node之间时延，对于pod的部署优先部署在时延低的node上
'''


class Greedy(Method):

    @staticmethod
    def get_plan(graph: Graph) -> Dict[AnyStr, AnyStr]:
        delay = Status.get_nodes_with_delay()
        delay_list = list(delay.keys())
        delay_list.sort(key=lambda x: delay[x], reverse=False)  # 按时间升序排列nodes

        plan = {}
        i = 0
        count = 0
        dest_node = delay_list[i]
        for operator_name in graph.get_operator_names():
            if operator_name == 'DataSource':
                plan[operator_name] = Config.source_node
            elif operator_name == 'DataConsumer':
                plan[operator_name] = Config.consumer_node
            else:
                if count < Config.resource_capacity:
                    plan[operator_name] = dest_node
                else:
                    i += 1
                    count = 0
                    dest_node = delay_list[i]
                    plan[operator_name] = dest_node
                count += 1

        return plan


if __name__ == '__main__':
    from kubecepops.models.samples.trafficsystemgraph import TrafficSystemGraph

    print(Greedy.get_plan(TrafficSystemGraph()))
