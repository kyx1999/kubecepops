from kubecepops.models.templates.graph import Graph

from typing import AnyStr, Dict
from abc import ABCMeta, abstractmethod


class Method(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def get_plan(graph: Graph) -> Dict[AnyStr, AnyStr]:
        # 继承并覆盖此静态方法，内容是根据物理网络的Status和复杂事件处理模型的graph得到部署方案，用的时候直接通过类名调用
        # 返回结果为一个字典，键是operator_name(str)，值是node_name(str)
        pass
