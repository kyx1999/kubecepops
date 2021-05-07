from kubecepops.core.config import Config
from kubecepops.models.event import Event

import time
import socket
import struct
from queue import Queue
from logging import Logger
from threading import Lock, Thread
from abc import ABCMeta, abstractmethod
from typing import AnyStr, List, Optional
from socketserver import BaseRequestHandler, ThreadingTCPServer


class Operator(metaclass=ABCMeta):

    def __init__(self, name: AnyStr, logger: Logger):
        # Operator实例应只能被Graph创建，此构造方法是给Graph用的
        self._name = name
        self._burden_level = 0
        self._logger = logger
        self._event_lock = Lock()  # 事件处理锁
        self._node = ''
        self._destinations = []  # IP(str)
        self._destination_sockets = []
        self._queue = Queue()  # 事件发送队列
        self._stop = False  # operator准备终止运行标志
        self._send_finished = False  # operator消息发送完成标志
        self._connection_count = 0  # operator连接计数
        self._connection_lock = Lock()  # operator连接计数锁
        self._server = None  # TCP服务器
        self_ = self

        class Handler(BaseRequestHandler):  # 用内部类继承BaseRequestHandler，以便后续拉起TCP服务器

            def handle(self):
                self_._connection_lock.acquire()
                self_._connection_count += 1
                self_._connection_lock.release()

                find_head1 = False
                find_head2 = False
                find_size1 = False
                find_size2 = False
                find_size3 = False
                find_size4 = False
                size = b''
                payload = b''

                while True:
                    buffer = self.request.recv(1024)
                    if buffer:
                        for i in range(len(buffer)):
                            c = struct.pack('<B', buffer[i])
                            if (not find_head1) or (not find_head2):
                                if c == b'\xeb':
                                    find_head1 = True
                                elif find_head1 and c == b'\x90':
                                    find_head2 = True
                                else:
                                    find_head1 = False
                                    find_head2 = False
                            else:
                                if not find_size1:
                                    size += c
                                    find_size1 = True
                                    continue
                                if not find_size2:
                                    size += c
                                    find_size2 = True
                                    continue
                                if not find_size3:
                                    size += c
                                    find_size3 = True
                                    continue
                                if not find_size4:
                                    size += c
                                    find_size4 = True
                                    size = struct.unpack('<I', size)[0]
                                    continue
                                if size > 1:
                                    payload += c
                                    size -= 1
                                    continue
                                payload += c

                                event = Event.get_event(payload)

                                if event.name != '-1':
                                    if Config.delay_open:  # 如果开启了等效时延放大，此处会按照实现每条链路预定的规则等效放大传输时延
                                        t1 = time.time() - event.send_time
                                        if t1 > 0:
                                            t2 = Config.delay_rules().get_delay(event.send_node, self_._node) - 1
                                            time.sleep(t1 * t2)

                                    if self_._logger:
                                        self_._logger.info(
                                            'Operator [' + self_._name + '] received event [' + event.name + ']')

                                    self_._event_lock.acquire()  # 这里根据等效负载等级放大处理时间
                                    t1 = time.perf_counter()
                                    event = self_._process_event(event)
                                    t2 = time.perf_counter()
                                    time.sleep((t2 - t1) * ((600 + 275 * self_._burden_level) / 600 - 1))
                                    self_._event_lock.release()

                                    if event:
                                        event.send_node = self_._node
                                        self_._queue.put(event)  # 将处理完成的事件放入事件队列，交由发送线程发送
                                else:  # 如果收到终止包，返回通知对方可以终止
                                    self.request.send(event.get_bytes())
                                    self_._connection_lock.acquire()
                                    self_._connection_count -= 1
                                    if self_._connection_count == 0:  # 当连接数归零时，自身准备终止
                                        self_._stop = True
                                    self_._connection_lock.release()
                                    return

                                find_head1 = False
                                find_head2 = False
                                find_size1 = False
                                find_size2 = False
                                find_size3 = False
                                find_size4 = False
                                size = b''
                                payload = b''

        self._handler = Handler

    @abstractmethod
    def _initialize(self):  # 如果需要初始化，则继承后覆盖此方法
        pass

    @abstractmethod
    def _process_event(self, event: Event) -> Optional[Event]:
        # 继承后只需覆盖此方法，在此方法中写出对event的处理并返回处理后的event即可，若不再继续转发，则返回None
        pass

    def _send(self):  # 发送事件的方法，用于多线程处理
        while True:
            event = self._queue.get()
            if event.name != '-1':
                for s in self._destination_sockets:
                    event.send_time = time.time()
                    s.send(event.get_bytes())
                    if self._logger:
                        self._logger.info('Operator [' + self._name + '] sent event [' + event.name + ']')
            else:  # 如果是终止包，在此等待对方返回通知
                for s in self._destination_sockets:
                    s.send(event.get_bytes())
                for s in self._destination_sockets:
                    find_head1 = False
                    find_head2 = False
                    find_size1 = False
                    find_size2 = False
                    find_size3 = False
                    find_size4 = False
                    size = b''
                    payload = b''
                    while_flag = True

                    while while_flag:
                        buffer = s.recv(1024)
                        if buffer:
                            for i in range(len(buffer)):
                                c = struct.pack('<B', buffer[i])
                                if (not find_head1) or (not find_head2):
                                    if c == b'\xeb':
                                        find_head1 = True
                                    elif find_head1 and c == b'\x90':
                                        find_head2 = True
                                    else:
                                        find_head1 = False
                                        find_head2 = False
                                else:
                                    if not find_size1:
                                        size += c
                                        find_size1 = True
                                        continue
                                    if not find_size2:
                                        size += c
                                        find_size2 = True
                                        continue
                                    if not find_size3:
                                        size += c
                                        find_size3 = True
                                        continue
                                    if not find_size4:
                                        size += c
                                        find_size4 = True
                                        size = struct.unpack('<I', size)[0]
                                        continue
                                    if size > 1:
                                        payload += c
                                        size -= 1
                                        continue
                                    payload += c

                                    event = Event.get_event(payload)
                                    if event.name == '-1':
                                        if self._logger:
                                            address, port = s.getpeername()
                                            self._logger.info(
                                                'Operator [' + self._name + '] finished the connection with ['
                                                + address + ':' + str(port) + ']')
                                        while_flag = False
                                        break
                self._send_finished = True
                break

    def _stop_watcher(self):  # 监测终止的方法，用于多线程处理
        while not self._stop:  # 每5秒检查一次是否准备终止
            time.sleep(5)

        if self._server:  # 结束_server线程
            self._server.shutdown()
            self._server = None

        event = Event()  # 发送终止包
        event.name = '-1'
        self._queue.put(event)

        while not self._send_finished:  # 等待_send线程收到回应
            pass

        for s in self._destination_sockets:  # 关闭所有连接
            s.shutdown(socket.SHUT_RDWR)
            s.close()

    def _get_logger(self) -> Logger:
        return self._logger

    def _get_queue(self) -> Queue:
        return self._queue

    def set_node(self, node: AnyStr):  # 设置此operator所在的node
        self._node = node

    def set_destinations(self, destinations: List[AnyStr]):  # 设置此operator的目标service地址
        destinations.sort()
        self._destinations = destinations

    def get_destinations(self) -> List[AnyStr]:
        return self._destinations

    def run(self, service_port: int, burden_level: int):  # 初始化operator，拉起TCP服务器
        for address in self._destinations:
            s = socket.socket()
            s.connect((address, service_port))
            self._destination_sockets.append(s)
            if self._logger:
                self._logger.info(
                    'Operator [' + self._name + '] connected to [' + address + ':' + str(service_port) + ']')

        t1 = Thread(target=self._send)  # 事件发送线程
        t1.start()

        self._burden_level = burden_level
        self._server = ThreadingTCPServer(('', Config.operator_port), self._handler)
        t2 = Thread(target=self._server.serve_forever)  # 事件处理线程
        t2.start()

        t3 = Thread(target=self._stop_watcher)  # 终止监测线程
        t3.start()

        self._initialize()

    def stop(self):  # 用以终止自身，仅限位于源头的operator（即DataSource）使用，否则在server存在连接的情况下将进入死循环
        self._stop = True
