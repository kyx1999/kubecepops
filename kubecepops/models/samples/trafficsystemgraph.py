from kubecepops.models.templates.graph import Graph
from kubecepops.models.templates.operator import Operator
from kubecepops.models.samples.datasource import DataSource
from kubecepops.models.samples.dataconsumer import DataConsumer
from kubecepops.models.samples.laneoperator import LaneOperator
from kubecepops.models.samples.speedoperator import SpeedOperator
from kubecepops.models.samples.accidentoperator import AccidentOperator

from typing import AnyStr, Callable, List, Tuple


class TrafficSystemGraph(Graph):

    def _generate_graph(self) -> List[
        Tuple[
            Tuple[AnyStr, Callable[..., Operator]],
            Tuple[AnyStr, Callable[..., Operator]]
        ]
    ]:
        return [
            (('DataSource', DataSource), ('LaneOperator0', LaneOperator)),
            (('DataSource', DataSource), ('SpeedOperator0', SpeedOperator)),
            (('DataSource', DataSource), ('LaneOperator1', LaneOperator)),
            (('DataSource', DataSource), ('SpeedOperator1', SpeedOperator)),
            (('DataSource', DataSource), ('LaneOperator2', LaneOperator)),
            (('DataSource', DataSource), ('SpeedOperator2', SpeedOperator)),
            (('LaneOperator0', LaneOperator), ('AccidentOperator0', AccidentOperator)),
            (('SpeedOperator0', SpeedOperator), ('AccidentOperator0', AccidentOperator)),
            (('LaneOperator1', LaneOperator), ('AccidentOperator1', AccidentOperator)),
            (('SpeedOperator1', SpeedOperator), ('AccidentOperator1', AccidentOperator)),
            (('LaneOperator2', LaneOperator), ('AccidentOperator2', AccidentOperator)),
            (('SpeedOperator2', SpeedOperator), ('AccidentOperator2', AccidentOperator)),
            (('AccidentOperator0', AccidentOperator), ('DataConsumer', DataConsumer)),
            (('AccidentOperator1', AccidentOperator), ('DataConsumer', DataConsumer)),
            (('AccidentOperator2', AccidentOperator), ('DataConsumer', DataConsumer))
        ]
