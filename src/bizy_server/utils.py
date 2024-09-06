import time
from threading import Timer


class DebounceTimer:
    def __init__(self, interval):
        self.interval = interval
        self.timer = None

    def debounce(self, func, *args, **kwargs):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(self.interval, func, args, kwargs)
        self.timer.start()
