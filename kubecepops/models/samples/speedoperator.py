from kubecepops.models.event import Event
from kubecepops.models.templates.operator import Operator

from logging import Logger
from typing import AnyStr, Optional


class SpeedOperator(Operator):

    def __init__(self, name: AnyStr, logger: Logger):
        super().__init__(name, logger)
        self._vehicles = {}

    def _initialize(self):
        pass

    def _process_event(self, event: Event) -> Optional[Event]:
        if event.vehicle_id in self._vehicles.keys():
            if event.time_step >= self._vehicles[event.vehicle_id].time_step:
                if self._vehicles[event.vehicle_id].speed < event.speed:
                    event.speed_accelerated = True
                else:
                    event.speed_accelerated = False
                self._vehicles[event.vehicle_id] = event
                return event
            else:
                return event
        else:
            self._vehicles[event.vehicle_id] = event
            return event
