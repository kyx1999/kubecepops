from kubecepops.core.config import Config
from kubecepops.methods.method import Method
from kubecepops.models.templates.graph import Graph

import os
from typing import AnyStr, Dict


class ResponseTimeAware(Method):

    @staticmethod
    def get_plan(graph: Graph) -> Dict[AnyStr, AnyStr]:
        node_map = {'0': 'kubernetes-master-01', '1': 'kubernetes-worker-01', '2': 'kubernetes-worker-02',
                    '3': 'kubernetes-worker-03', '4': 'kubernetes-worker-04'}

        try:
            file = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), Config.response_time_aware_strategy),
                        'r')

            for i in range(1 + 11 * Config.burden_level):
                file.readline()

            plan = {}

            line1 = file.readline().strip()
            line2 = file.readline().strip()
            line = line1[:-13].split(' -- ') + line2[:-13].split(' -- ')
            for i in range(4):
                temp = line[i][:-5 - (i % 2)].split(' on ')
                if temp[0] == '0':
                    plan['SpeedOperator0'] = node_map[temp[1]]
                elif temp[0] == '1':
                    plan['LaneOperator0'] = node_map[temp[1]]
                elif temp[0] == '2':
                    plan['AccidentOperator0'] = node_map[temp[1]]

            file.readline()

            line1 = file.readline().strip()
            line2 = file.readline().strip()
            line = line1[:-13].split(' -- ') + line2[:-13].split(' -- ')
            for i in range(4):
                temp = line[i][:-5 - (i % 2)].split(' on ')
                if temp[0] == '0':
                    plan['SpeedOperator1'] = node_map[temp[1]]
                elif temp[0] == '1':
                    plan['LaneOperator1'] = node_map[temp[1]]
                elif temp[0] == '2':
                    plan['AccidentOperator1'] = node_map[temp[1]]

            file.readline()

            line1 = file.readline().strip()
            line2 = file.readline().strip()
            line = line1[:-13].split(' -- ') + line2[:-13].split(' -- ')
            for i in range(4):
                temp = line[i][:-5 - (i % 2)].split(' on ')
                if temp[0] == '0':
                    plan['SpeedOperator2'] = node_map[temp[1]]
                elif temp[0] == '1':
                    plan['LaneOperator2'] = node_map[temp[1]]
                elif temp[0] == '2':
                    plan['AccidentOperator2'] = node_map[temp[1]]

            file.close()

            plan['DataSource'] = Config.source_node
            plan['DataConsumer'] = Config.consumer_node

            return plan

        except IOError as e:
            print(e)


if __name__ == '__main__':
    from kubecepops.models.samples.trafficsystemgraph import TrafficSystemGraph

    print(ResponseTimeAware.get_plan(TrafficSystemGraph()))
