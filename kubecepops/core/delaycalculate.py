from typing import AnyStr


class DelayCalculate:

    @staticmethod
    def do_calculate(source_log: AnyStr, consumer_log: AnyStr) -> float:
        # 根据日志计算一次实验中的平均传输时延，单位为秒，注意由于节点间时间不完全同步，如果出现负数或者不同等效负载等级下时延数量级相差过大的情况，应人为给所有数据加上一个合适的时间
        source_dict = {}  # key: value => event_number<int>: time<float>，计event[i]发送时间
        connection_count = 0  # source的连接数
        count = 0  # event计数器，只给sender用

        try:
            source = open(source_log, 'r')
            line = source.readline().strip()

            #  完成source_dict
            while True:
                if not line:
                    break

                elif line.find('connected') != -1:  # 连接服务器一行略过
                    connection_count += 1

                elif line.find('sent') != -1 and count == 0:
                    vec = line.split(' ')

                    event_number = vec[9].strip('[')
                    event_number = event_number.strip(']')
                    event_number = int(event_number)

                    source_dict[event_number] = float(vec[0])
                    count += 1

                elif line.find('sent') != -1 and count == connection_count - 1:
                    vec = line.split(' ')

                    event_number = vec[9].strip('[')
                    event_number = event_number.strip(']')
                    event_number = int(event_number)

                    source_dict[event_number] += float(vec[0])
                    count = 0  # 重置计数器
                    source_dict[event_number] = float(source_dict[event_number] / connection_count)

                elif line.find('sent') != -1 and 0 < count < connection_count - 1:
                    count += 1
                    vec = line.split(' ')

                    event_number = vec[9].strip('[')
                    event_number = event_number.strip(']')
                    event_number = int(event_number)

                    source_dict[event_number] += float(vec[0])

                line = source.readline().strip()

            source.close()
        except IOError as e:
            print(e)

        consumer_dict = {}  # key: value => event_number<int>: max_time<float>，计event[i]最长接收时间

        try:
            consumer = open(consumer_log, 'r')
            line = consumer.readline().strip()

            #  完成consumer_dict
            while True:
                if not line:
                    break

                else:
                    vec = line.split(' ')
                    event_number = vec[9].strip('[')
                    event_number = event_number.strip(']')
                    event_number = int(event_number)

                    consumer_dict[event_number] = float(vec[0])

                line = consumer.readline().strip()

            consumer.close()
        except IOError as e:
            print(e)

        res = 0.0
        for i in range(0, len(consumer_dict)):
            res += (consumer_dict[i] - source_dict[i])

        res = res / len(consumer_dict)

        return res
