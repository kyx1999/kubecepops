from kubecepops.cluster.delayrules import DelayRules

from typing import AnyStr, List, Tuple


class VirtualMachineDelayRules(DelayRules):

    def _generate_delay(self) -> List[Tuple[Tuple[AnyStr, AnyStr], float]]:
        return [
            (('kubernetes-master-01', 'kubernetes-worker-01'), 1.0),
            (('kubernetes-master-01', 'kubernetes-worker-02'), 3.0),
            (('kubernetes-master-01', 'kubernetes-worker-03'), 5.0),
            (('kubernetes-master-01', 'kubernetes-worker-04'), 7.0),
            (('kubernetes-worker-01', 'kubernetes-worker-02'), 2.0),
            (('kubernetes-worker-01', 'kubernetes-worker-03'), 4.0),
            (('kubernetes-worker-01', 'kubernetes-worker-04'), 6.0),
            (('kubernetes-worker-02', 'kubernetes-worker-03'), 3.0),
            (('kubernetes-worker-02', 'kubernetes-worker-04'), 5.0),
            (('kubernetes-worker-03', 'kubernetes-worker-04'), 4.0)
        ]
