# -*- coding: utf-8 -*-
import threading, time
from collections import deque

class EventBus:
    def __init__(self, max_history=500):
        self._lock = threading.Lock()
        self._subs = {}
        self._history = deque(maxlen=max_history)
    def subscribe(self, topic, cb):
        with self._lock:
            self._subs.setdefault(topic, []).append(cb)
    def publish(self, topic, payload):
        ev = {"t": time.time(), "topic": topic, "payload": payload}
        with self._lock:
            self._history.append(ev)
            subs = list(self._subs.get(topic, []))
        for cb in subs:
            try: cb(ev)
            except Exception as e: print(f"[BUS] {e}")
        return ev
    def history(self, n=50):
        with self._lock:
            return list(self._history)[-n:]