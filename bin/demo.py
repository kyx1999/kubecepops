from kubecepops.core.config import Config
from kubecepops.core.deploy import Deploy
from kubecepops.methods.method import Method
from kubecepops.core.initialize import Initialize
from kubecepops.methods.samples.greedy import Greedy
from kubecepops.core.delaycalculate import DelayCalculate
from kubecepops.cluster.kubetools.kubecontrol import K8sApi
from kubecepops.methods.samples.loadbalance import LoadBalance
from kubecepops.methods.samples.responsetimeaware import ResponseTimeAware
from kubecepops.methods.samples.reinforcementlearning import ReinforcementLearning

import time
from typing import Callable


def test(method: Callable[..., Method]):
    for burden_level in range(9):
        Deploy.clear_deploy()

        Config.burden_level = burden_level
        Deploy.do_deploy(method)

        while True:
            time.sleep(20)
            pod = K8sApi.k8s_conn().read_namespaced_pod(namespace='default', name='DataSource'.lower())
            try:
                if pod.status.container_statuses[0].state.terminated.reason == 'Completed':
                    break
            except TypeError:
                continue

        while True:
            time.sleep(20)
            pod = K8sApi.k8s_conn().read_namespaced_pod(namespace='default', name='DataConsumer'.lower())
            try:
                if pod.status.container_statuses[0].state.terminated.reason == 'Completed':
                    break
            except TypeError:
                continue

        source_log = method.__name__.lower() + '-source-' + str(burden_level) + '.log'
        consumer_log = method.__name__.lower() + '-consumer-' + str(burden_level) + '.log'

        K8sApi.save_log('DataSource'.lower(), source_log)
        K8sApi.save_log('DataConsumer'.lower(), consumer_log)

        with open(method.__name__.lower() + '-result.txt', 'a') as f:
            delay = str(DelayCalculate.do_calculate(source_log, consumer_log))
            f.write(delay + '\n')
            print('Result of ' + method.__name__.lower() + ' whit burden_level = '
                  + str(burden_level) + ': ' + delay + 's')


def main():
    Initialize.clear_initialize()
    Initialize.do_initialize()

    test(Greedy)
    test(LoadBalance)
    test(ResponseTimeAware)
    test(ReinforcementLearning)

    Deploy.clear_deploy()
    Initialize.clear_initialize()


if __name__ == '__main__':
    main()
