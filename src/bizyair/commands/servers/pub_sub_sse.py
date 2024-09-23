import json
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from queue import Queue

import requests

from bizyair.common.utils import truncate_long_strings


@dataclass
class SubscriberState:
    queue: Queue = field(default_factory=queue.Queue)
    stop_event: threading.Event = field(default_factory=threading.Event)


class Mediator:
    STOP_SIGNAL = "STOP"  # 定义一个类变量作为停止信号

    def __init__(self):
        self.subscribers = {}
        self.executor = ThreadPoolExecutor(max_workers=2)

    def subscribe(self, subscriber):
        self.subscribers[subscriber] = SubscriberState()
        self.executor.submit(self.handle_messages, subscriber)

    def unsubscribe(self, subscriber):
        if subscriber in self.subscribers:
            self.stop_subscriber(subscriber)
            print(f"{subscriber.name} has been unsubscribed.")

    def publish(self, message, subscriber=None):
        if subscriber:
            # 发送消息到特定订阅者
            if message == self.STOP_SIGNAL:
                self.subscribers[
                    subscriber
                ].stop_event.set()  # 设置特定订阅者的停止事件
            else:
                self.subscribers[subscriber].queue.put(message)
        else:
            # 广播消息到所有订阅者
            for sub_state in self.subscribers.values():
                sub_state.queue.put(message)

    def handle_messages(self, subscriber):
        sub_state = self.subscribers[subscriber]
        while not sub_state.stop_event.is_set():  # 检查特定订阅者的停止事件
            try:
                message = sub_state.queue.get(timeout=1)
                if message == self.STOP_SIGNAL:
                    break
                subscriber.receive(message)
                sub_state.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error handling message for {subscriber.name}: {e}")
        subscriber.receive(message=None)  # 发送 None 表示连接断开
        self._cleanup_subscriber(subscriber)

    def stop_subscriber(self, subscriber):
        self.publish(
            self.STOP_SIGNAL, subscriber=subscriber
        )  # 发送停止消息到特定订阅者

    def _cleanup_subscriber(self, subscriber):
        print(f"Cleaning up resources for {subscriber.name}")
        sub_state = self.subscribers[subscriber]
        while not sub_state.queue.empty():
            sub_state.queue.get()
            sub_state.queue.task_done()

        subscriber.is_subscribed = False  # 更新订阅状态为未订阅
        del self.subscribers[subscriber]

    def shutdown(self):
        for subscriber in list(self.subscribers.keys()):
            self.stop_subscriber(subscriber)
        self.executor.shutdown(wait=True)

    def start_sse_client(self, url, subscriber, headers=None, **kwargs):
        print(f"Starting SSE client for {subscriber.name}, {headers=} {url=}")
        """启动 SSE 客户端来接收数据"""

        def connect():
            from sseclient import SSEClient

            try:
                response = requests.get(url, headers=headers, **kwargs, stream=True)
                if response.status_code != 200:
                    print(
                        f"Failed to connect to {url}, status code: {response.status_code}"
                    )
                    return
                sse_client = SSEClient(response)
                for event in sse_client.events():
                    data = json.loads(event.data)
                    import pprint

                    pprint.pprint(truncate_long_strings(data))
                    self.publish(data, subscriber=subscriber)
            except Exception as e:
                print(f"Error connecting to {url}: {e}")
            finally:
                print(f"SSE client for {subscriber.name} disconnected")
                self.publish(self.STOP_SIGNAL, subscriber=subscriber)

        self.executor.submit(connect)


class Subscriber:
    def __init__(self, name, mediator):
        self.name = name
        self.mediator = mediator
        self.messages = queue.Queue()
        self.is_subscribed = True  # 订阅状态监测

    def receive(self, message):
        self.messages.put(message)

    def is_empty(self):
        return self.messages.empty()

    def pop(self, timeout=5):
        try:
            if self.is_subscribed or not self.messages.empty():
                return self.messages.get(timeout=timeout)
            else:
                return None
        except queue.Empty:
            print(f"No messages received for {self.name} within the timeout period.")
            return None

    def unsubscribe(self):
        self.mediator.unsubscribe(self)
        self.is_subscribed = False  # 更新订阅状态为未订阅

    def get_result(self, node_id, timeout=12):
        while True:
            result = self.pop(timeout=timeout)
            if result is None:
                return None
            try:
                if (
                    "message" in result
                    and isinstance(result["message"], dict)
                    and result["message"]["event"] == "result"
                ):
                    event_node_id = result["message"]["data"]["node"]
                    if event_node_id == node_id:
                        return result["data"]["payload"]
            except Exception as e:
                print(f"Error processing message for {self.name}: {e}")
                return None


class Publisher:
    def __init__(self, mediator):
        self.mediator = mediator

    def send(self, message):
        self.mediator.publish(message)


# class SSEClient:
#     def __init__(self, url, mediator, subscriber, headers=None, **kwargs):
#         self.url = url
#         self.mediator = mediator
#         self.subscriber = subscriber
#         self.headers = headers if headers else {}
#         self.kwargs = kwargs  # 其他可能的 requests 参数，如 auth, cookies 等

#     def connect(self):
#         """连接到 SSE 并接收消息"""
#         print(f"Connecting to {self.url}")
#         response = requests.get(self.url, stream=True, headers=self.headers, **self.kwargs)
#         for line in response.iter_lines():
#             if line:
#                 decoded_line = line.decode('utf-8')
#                 if decoded_line.startswith('data:'):
#                     message = decoded_line.replace('data: ', '').strip()
#                     self.mediator.publish(message, subscriber=self.subscriber)
#                 print(f"Received message: {decoded_line}")
#         self.mediator.publish(self.mediator.STOP_SIGNAL, subscriber=self.subscriber)


if __name__ == "__main__":
    # 示例使用
    mediator = Mediator()
    subscriber1 = Subscriber("Subscriber 1", mediator)
    subscriber2 = Subscriber("Subscriber 2", mediator)

    mediator.subscribe(subscriber1)
    mediator.subscribe(subscriber2)
    mediator.publish("hello", subscriber=subscriber1)
    mediator.publish("helo", subscriber=subscriber1)

    # 启动 SSE 客户端，包括自定义 headers 和其他参数
    sse_url = "http://example.com/sse"
    custom_headers = {"Authorization": "Bearer your_token_here"}
    mediator.start_sse_client(sse_url, subscriber=subscriber1, headers=custom_headers)

    # 等待并获取第一个处理过的消息，等待最多10秒
    first_message = subscriber1.get_first_message(timeout=2)
    if first_message:
        print(f"First processed message for Subscriber 1: {first_message}")

    # 发送 STOP 消息来停止所有订阅者
    mediator.publish(mediator.STOP_SIGNAL)

    print("end")
