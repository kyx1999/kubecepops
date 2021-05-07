from kubecepops.models.event import Event
from kubecepops.models.sumo.datareader import DataReader
from kubecepops.models.templates.operator import Operator

import time
from logging import Logger
from typing import AnyStr, Optional


class DataSource(Operator):

    def __init__(self, name: AnyStr, logger: Logger):
        super().__init__(name, logger)
        self._event_quantity = 0

    def _initialize(self):
        count = 0
        data_reader = DataReader()

        t1 = time.perf_counter()
        event = data_reader.readline()
        while event and count < self._event_quantity:
            self._get_queue().put(event)
            count += 1
            t2 = time.perf_counter()

            t = 1 / 600 * count - t2 + t1
            t = t if t > 0 else 0
            time.sleep(t)

            event = data_reader.readline()

        data_reader.close()

        self.stop()

    def _process_event(self, event: Event) -> Optional[Event]:
        pass

    def set_event_quantity(self, event_quantity: int):
        self._event_quantity = event_quantity
