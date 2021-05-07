import struct


class Event:

    def __init__(self):
        self.name = ''  # 如果name为'-1' 则表示终止包
        self.send_time = 0.0
        self.send_node = ''

        self.vehicle_id = ''
        self.position = 0.0
        self.speed = 0.0
        self.time_step = 0.0
        self.edge_id = ''
        self.lane_id = ''

        # markers, all true -> Accident
        self.lane_changed = False
        self.speed_accelerated = False
        self.close_to_other_vehicles = False

    def get_bytes(self) -> bytes:
        a = b'\xeb\x90'

        c = self.name.encode('utf-8')
        b = struct.pack('<I', len(c))

        d = struct.pack('<d', self.send_time)

        f = self.send_node.encode('utf-8')
        e = struct.pack('<I', len(f))

        h = self.vehicle_id.encode('utf-8')
        g = struct.pack('<I', len(h))

        i = struct.pack('<ddd', self.position, self.speed, self.time_step)

        k = self.edge_id.encode('utf-8')
        j = struct.pack('<I', len(k))

        m = self.lane_id.encode('utf-8')
        l_ = struct.pack('<I', len(m))

        n = struct.pack('<???', self.lane_changed, self.speed_accelerated, self.close_to_other_vehicles)

        payload = b + c + d + e + f + g + h + i + j + k + l_ + m + n

        return a + struct.pack('<I', len(payload)) + payload

    @staticmethod
    def get_event(payload: bytes) -> __init__:
        event = Event()

        b = 4
        c = b + struct.unpack('<I', payload[0:b])[0]
        event.name = payload[b: c].decode('utf-8')

        event.send_time = struct.unpack('<d', payload[c:c + 8])[0]

        d = c + 8
        e = d + 4
        f = e + struct.unpack('<I', payload[d:e])[0]
        event.send_node = payload[e: f].decode('utf-8')

        g = f + 4
        h = g + struct.unpack('<I', payload[f:g])[0]
        event.vehicle_id = payload[g: h].decode('utf-8')

        event.position = struct.unpack('<d', payload[h:h + 8])[0]
        event.speed = struct.unpack('<d', payload[h + 8:h + 16])[0]
        event.time_step = struct.unpack('<d', payload[h + 16:h + 24])[0]

        i = h + 24
        j = i + 4
        k = j + struct.unpack('<I', payload[i:j])[0]
        event.edge_id = payload[j: k].decode('utf-8')

        l_ = k + 4
        m = l_ + struct.unpack('<I', payload[k:l_])[0]
        event.lane_id = payload[l_: m].decode('utf-8')

        event.lane_changed = struct.unpack('<?', payload[m:m + 1])[0]
        event.speed_accelerated = struct.unpack('<?', payload[m + 1:m + 2])[0]
        event.close_to_other_vehicles = struct.unpack('<?', payload[m + 2:m + 3])[0]

        return event
