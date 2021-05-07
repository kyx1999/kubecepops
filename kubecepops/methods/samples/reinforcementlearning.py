from kubecepops.core.config import Config
from kubecepops.methods.method import Method
from kubecepops.models.templates.graph import Graph

import os
from typing import AnyStr, Dict


class ReinforcementLearning(Method):

    @staticmethod
    def get_plan(graph: Graph) -> Dict[AnyStr, AnyStr]:
        node_map = {'0': 'kubernetes-master-01', '1': 'kubernetes-worker-01', '2': 'kubernetes-worker-02',
                    '3': 'kubernetes-worker-03', '4': 'kubernetes-worker-04'}

        try:
            file = open(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), Config.reinforcement_learning_strategy), 'r')

            level = Config.burden_level if Config.burden_level < 8 else 7
            s = 8 + level * 15 if level > 0 else 5
            for i in range(s):
                file.readline()

            plan = {}

            for i in range(int(file.readline().strip())):
                line = file.readline().strip().split(' ')
                if line[1] == '0':
                    plan['SpeedOperator' + line[0]] = node_map[line[2]]
                elif line[1] == '1':
                    plan['LaneOperator' + line[0]] = node_map[line[2]]
                elif line[1] == '2':
                    plan['AccidentOperator' + line[0]] = node_map[line[2]]

            file.close()

            plan['DataSource'] = Config.source_node
            plan['DataConsumer'] = Config.consumer_node

            return plan

        except IOError as e:
            print(e)


if __name__ == '__main__':
    from kubecepops.models.samples.trafficsystemgraph import TrafficSystemGraph

    print(ReinforcementLearning.get_plan(TrafficSystemGraph()))
