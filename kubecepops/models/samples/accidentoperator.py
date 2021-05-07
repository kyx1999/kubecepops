from kubecepops.models.event import Event
from kubecepops.models.templates.operator import Operator

from logging import Logger
from typing import AnyStr, Optional


class AccidentOperator(Operator):

    def __init__(self, name: AnyStr, logger: Logger):
        super().__init__(name, logger)
        self._vehicles = {}

    def _initialize(self):
        pass

    def _process_event(self, event: Event) -> Optional[Event]:
        if event.vehicle_id in self._vehicles.keys():
            if event.time_step > self._vehicles[event.vehicle_id].time_step:
                self._vehicles[event.vehicle_id] = event
                return event
            elif event.time_step == self._vehicles[event.vehicle_id].time_step:
                if (self._vehicles[event.vehicle_id].lane_changed and event.speed_accelerated) or (
                        self._vehicles[event.vehicle_id].speed_accelerated and event.lane_changed) or (
                        event.lane_changed and event.speed_accelerated):
                    event.lane_changed = True
                    event.speed_accelerated = True
                    for e in self._vehicles.values():
                        if e.lane_id == event.lane_id and e.vehicle_id != event.vehicle_id and \
                                event.position - 5 <= e.position <= event.position + 5:
                            event.close_to_other_vehicles = True
                        else:
                            event.close_to_other_vehicles = False
                self._vehicles[event.vehicle_id] = event
                return event
            else:
                return event
        else:
            self._vehicles[event.vehicle_id] = event
            return event
