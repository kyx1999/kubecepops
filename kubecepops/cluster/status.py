from kubecepops.core.config import Config
from kubecepops.cluster.kubetools.kubecontrol import K8sApi

from typing import AnyStr, Dict


class Status:

    @staticmethod
    def _curl_time(url: AnyStr) -> float:  # 计算Node之间延时
        command = ['curl', 'http://' + url,  # 指定请求的URL
                   '-L', '--max-redirs', '5',  # 开启重定向，并指定HTTP重定向的最大数
                   '-o', '/dev/null',  # 设置返回的资源数据写入到黑洞
                   '-s',  # 不输出错误和进度信息
                   '-w', '%{time_total}']  # 格式化返回传输结束所消耗的总时间
        http_total_time = float(K8sApi.execute_command(command, Config.source_node))  # 传输结束所消耗的总时间

        print('传输结束时间: %.8f ms' % (http_total_time * 1000))
        print('====================')

        return http_total_time * 1000  # unit <ms>

    @staticmethod
    def get_nodes_with_delay() -> Dict[AnyStr, float]:
        services_ip = K8sApi.get_services_ip('initialize')
        time_list = {}

        # 具体测试时延使用单独的一个nginx pod，使用service ip: 测试nginx port的方式测试延迟
        for i in services_ip.keys():
            # 测试用pod + nginx_port，pod service不参与之后部署
            test_time = Status._curl_time(services_ip[i] + ':' + str(Config.nginx_port))
            if Config.delay_open:
                time_list[i] = test_time * Config.delay_rules().get_delay(Config.source_node, i)
            else:
                time_list[i] = test_time

        return time_list

    @staticmethod
    def get_nodes_with_allocatable_source() -> Dict[AnyStr, Dict[AnyStr, int]]:
        temp = K8sApi.get_nodes_source()
        node_source = {}
        for i in temp.get('items'):
            node_name = i['metadata']['name']
            usage = {'cpu': int(str(i['usage']['cpu']).split('n')[0]),
                     'mem': int(str(i['usage']['memory']).split('K')[0])}
            node_source[node_name] = usage

        print("Node Source:")
        print(node_source)

        '''
                    return formation eg:
                    {
                        'k8s-node1': {'cpu': 23551662, 'mem': 497560},
                        'k8s-node2': {'cpu': 34643869, 'mem': 553368},
                        'k8s-node3': {'cpu': 19155916, 'mem': 332212}
                    }
        '''

        return node_source

    # @staticmethod
    # def get_pod_list_with_allocatable_source() -> list:
    #     temp = K8sApi.get_pod_source()
    #     pod_source_list = []
    #     for i in temp['items']:
    #         if i['metadata']['name'] == 'speed-test' \
    #                 or i['metadata']['name'] == 'lane-test' \
    #                 or i['metadata']['name'] == 'accident-test':
    #             pod_name = i['metadata']['name']
    #             usage = {'cpu': str(i['containers'][0]['usage']['cpu']).split('n')[0],
    #                      'mem': str(i['containers'][0]['usage']['memory']).split('K')[0]
    #                      }
    #             tem = {pod_name: usage}
    #             pod_source_list.append(tem)
    #
    #     '''
    #     return [
    #         {'accident-test': {'cpu': '0', 'mem': '1888'}},
    #         {'lane-test': {'cpu': '0', 'mem': '3376'}},
    #         {'speed-test': {'cpu': '0', 'mem': '3344'}}
    #         ]
    #     '''
    #
    #     return pod_source_list
