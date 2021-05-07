from kubecepops.models.event import Event
from kubecepops.models.templates.operator import Operator

from logging import Logger
from typing import AnyStr, Optional


class LaneOperator(Operator):

    def __init__(self, name: AnyStr, logger: Logger):
        super().__init__(name, logger)
        self._vehicles = {}

    def _initialize(self):
        pass

    def _process_event(self, event: Event) -> Optional[Event]:
        if event.vehicle_id in self._vehicles.keys():
            if event.time_step >= self._vehicles[event.vehicle_id].time_step:
                if self._vehicles[event.vehicle_id].lane_id != event.lane_id:
                    event.lane_changed = True
                else:
                    event.lane_changed = False
                self._vehicles[event.vehicle_id] = event
                return event
            else:
                return event
        else:
            self._vehicles[event.vehicle_id] = event
            return event
