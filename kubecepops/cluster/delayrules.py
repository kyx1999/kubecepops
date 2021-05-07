from typing import AnyStr, List, Tuple
from abc import ABCMeta, abstractmethod


class DelayRules(metaclass=ABCMeta):

    def __init__(self):
        self._map = {}
        for delay in self._generate_delay():
            self._map[(delay[0][0], delay[0][1])] = float(delay[1])
            self._map[(delay[0][1], delay[0][0])] = float(delay[1])

    @abstractmethod
    def _generate_delay(self) -> List[Tuple[Tuple[AnyStr, AnyStr], float]]:
        # 继承后只需覆盖此方法，在此方法中写出node之间的延时放大倍数即可，node名称必须是小写
        pass

    def get_delay(self, address1: AnyStr, address2: AnyStr) -> float:
        delay = self._map.get(address1, address2)
        if delay:
            return delay
        return 1.0
