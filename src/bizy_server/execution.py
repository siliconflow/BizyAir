import asyncio
import copy
import heapq
import logging
import threading


class UploadQueue:
    def __init__(self):
        self.mutex = threading.RLock()
        self.not_empty = threading.Condition(self.mutex)
        self.task_counter = 0
        self.queue = []
        self.currently_running = {}

    def put(self, item):
        with self.mutex:
            heapq.heappush(self.queue, item)
            self.not_empty.notify()

    def get(self, timeout=None):
        with self.not_empty:
            while len(self.queue) == 0:
                self.not_empty.wait(timeout=timeout)
                if timeout is not None and len(self.queue) == 0:
                    return None
            item = heapq.heappop(self.queue)
            i = self.task_counter
            self.currently_running[i] = copy.deepcopy(item)
            self.task_counter += 1
            return (item, i)

    def task_done(self, item_id):
        with self.mutex:
            self.currently_running.pop(item_id)


def upload_worker(server, q):
    timeout = 1000.0
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            queue_item = q.get(timeout=timeout)
            if queue_item is not None:
                item, item_id = queue_item
                loop = asyncio.get_event_loop()
                loop.run_until_complete(server.do_upload(item))
                q.task_done(item_id)
            else:
                continue
        except Exception as e:
            logging.error(f"Failed to upload file: {e}")
