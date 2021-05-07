from kubecepops.models.event import Event

import os
from typing import AnyStr, Optional


class DataReader:

    def __init__(self, file_name: AnyStr = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data.tr')):
        self._file = None
        try:
            self._file = open(file_name, 'r')
        except IOError as e:
            print(e)

        self._count = 0

    def readline(self) -> Optional[Event]:
        if self._file:
            line = self._file.readline().strip()

            if line:
                items = line.split('"')
                event = Event()
                event.name = str(self._count)
                event.vehicle_id = items[1]
                event.position = float(items[3])
                event.speed = float(items[5])
                event.time_step = float(items[7])
                event.edge_id = items[9]
                event.lane_id = items[11]

                self._count += 1

                return event

        return None

    def close(self):
        if self._file:
            self._file.close()
