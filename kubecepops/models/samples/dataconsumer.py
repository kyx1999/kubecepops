from kubecepops.models.event import Event
from kubecepops.models.templates.operator import Operator

from typing import Optional


class DataConsumer(Operator):

    def _initialize(self):
        pass

    def _process_event(self, event: Event) -> Optional[Event]:
        if event.lane_changed and event.speed_accelerated and event.close_to_other_vehicles:
            if self._get_logger():
                self._get_logger().warning(
                    'Vehicle [' + event.vehicle_id + '] may have a risk of an accident on Lane[' + event.lane_id + ']')

        return None
