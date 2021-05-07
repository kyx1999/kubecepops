from kubecepops.models.templates.operator import Operator

from logging import Logger
from abc import ABCMeta, abstractmethod
from typing import AnyStr, Callable, Dict, List, Tuple


class Graph(metaclass=ABCMeta):

    def __init__(self, logger: Logger = None):
        self._logger = logger
        self._map = {}  # operator_name(str): Operator
        self._edges = {}  # operator_name(str): [operator1_name(str), operator2_name(str), operator3_name(str)...]
        self._reversed_edges = {}  # 同上

        for edge in self._generate_graph():  # 根据_generate_graph返回的内容填充_map、_edges、_reversed_edges
            if not self._map.get(edge[0][0]):
                self._map[edge[0][0]] = edge[0][1](edge[0][0], self._logger)
            if not self._map.get(edge[1][0]):
                self._map[edge[1][0]] = edge[1][1](edge[1][0], self._logger)

            if not self._edges.get(edge[0][0]):
                self._edges[edge[0][0]] = []
            if not self._reversed_edges.get(edge[1][0]):
                self._reversed_edges[edge[1][0]] = []
            self._edges[edge[0][0]].append(edge[1][0])
            self._edges[edge[0][0]].sort()
            self._reversed_edges[edge[1][0]].append(edge[0][0])
            self._reversed_edges[edge[1][0]].sort()

    @abstractmethod
    def _generate_graph(self) -> List[
        Tuple[
            Tuple[AnyStr, Callable[..., Operator]],
            Tuple[AnyStr, Callable[..., Operator]]
        ]
    ]:
        # 继承后只需覆盖此方法，在此方法中照着OperatorGraph1返回Graph的结构即可
        pass

    def set_operator_addresses(self, addresses: Dict[AnyStr, Tuple[AnyStr, AnyStr]]):
        # addresses是以operator_name为键、node_name和service_ip的二元组为值的字典
        for operator in self._map.values():
            operator.set_node('')
            operator.set_destinations([])

        keys = list(addresses.keys())
        keys.sort()
        for operator_name1 in keys:
            if operator_name1 in self._map.keys():
                self._map[operator_name1].set_node(addresses[operator_name1][0])

                if self._reversed_edges.get(operator_name1):
                    for operator_name2 in self._reversed_edges[operator_name1]:
                        destinations = self._map[operator_name2].get_destinations()
                        destinations.append(addresses[operator_name1][1])
                        self._map[operator_name2].set_destinations(destinations)

    def get_operator_names(self) -> List[AnyStr]:  # 提供给部署使用
        names = list(self._map.keys())
        names.sort()
        return names

    def get_operator(self, operator_name: AnyStr) -> Operator:  # 提供给部署或算法使用
        if operator_name in self._map.keys():
            return self._map[operator_name]

    def get_sorted_deploy_list(self) -> List[AnyStr]:  # 从graph的DataConsumer开始，返回向源头的层次遍历结果，便于部署使用
        deploy_list = ['DataConsumer']
        i = 0
        while i < len(deploy_list):
            previous_operators = self._reversed_edges.get(deploy_list[i])
            if previous_operators:
                for previous_operator in previous_operators:
                    if previous_operator not in deploy_list:
                        deploy_list.append(previous_operator)
            i += 1

        return deploy_list
