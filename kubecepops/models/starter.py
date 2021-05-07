from kubecepops.models.samples.trafficsystemgraph import TrafficSystemGraph

import ast
import sys
import logging


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # fh = logging.FileHandler('log.txt', mode='w')
    # fh.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(created)f - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    graph = TrafficSystemGraph(logger)

    # logger.addHandler(sh)

    if sys.argv[2] == 'DataSource' or sys.argv[2] == 'DataConsumer':
        logger.addHandler(sh)

    addresses = ast.literal_eval(sys.argv[1])
    graph.set_operator_addresses(addresses)

    data_source = graph.get_operator('DataSource')
    if hasattr(data_source, 'set_event_quantity'):
        data_source.set_event_quantity(int(sys.argv[4]))

    if sys.argv[2] in graph.get_operator_names():
        graph.get_operator(sys.argv[2]).run(int(sys.argv[3]), int(sys.argv[5]))


if __name__ == '__main__':
    main()
