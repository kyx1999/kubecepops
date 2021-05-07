from kubecepops.cluster.samples.raspberrypidelayrules import RaspberryPiDelayRules
# from kubecepops.cluster.samples.virtualmachinedelayrules import VirtualMachineDelayRules


class Config:
    kube_config = 'kubeconfig-rp.yaml'  # 连接集群用的kube_config文件名(默认需先放置于kubecepops.core.kubetools包下)
    nginx_port = 31162  # _curl_time测试时延时使用的nginx-service端口
    resource_capacity = 5  # 每个node的最大资源容量(然而实际上只有Greedy算法在用。。。)
    source_node = 'kubernetes-master-01'  # 用于部署DataSource的默认node
    consumer_node = 'kubernetes-worker-04'  # 用于部署DataConsumer的默认node
    image = 'kyx1999/kubecepops:latest'  # operator镜像仓库
    image_pull_policy = 'IfNotPresent'  # Always：总是拉取镜像，IfNotPresent：本地有则使用本地镜像，否则拉取，Never：只使用本地镜像，从不拉取，即使本地没有
    service_port = 9663  # 用于帮助每个pod通信的service的端口
    event_quantity = 10000  # 最大发送事件数量
    burden_level = 0  # operator等效负载等级(0 - 8)
    response_time_aware_strategy = 'responsetimeaware.txt'  # 响应时间感知算法策略文件名(默认需先放置于kubecepops.methods.samples包下)
    reinforcement_learning_strategy = 'reinforcementlearning.txt'  # 强化学习算法策略文件名(默认需先放置于kubecepops.methods.samples包下)
    # 以上设置修改后即可生效

    operator_port = 80  # operator端口(容器端口，修改后要同时修改Dockerfile文件中暴露的端口)
    delay_open = False  # 是否开启等效时延放大(理论上需要集群开启NTP服务支持，目前的kubecepops.core.initialize中并未设置NTP服务，不建议开启)
    delay_rules = RaspberryPiDelayRules  # 等效时延放大规则(RaspberryPiDelay或VirtualMachineDelay)
    # 以上设置需要重新打包镜像后生效
