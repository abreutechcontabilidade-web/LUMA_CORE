# -*- coding: utf-8 -*-
import os, json, hashlib, time
from threading import Lock

class ZBITLedger:
    def __init__(self, path):
        self.path = path
        self._lock = Lock()
        self._prev = "0"*64
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                if lines:
                    self._prev = json.loads(lines[-1]).get("hash", self._prev)
            except Exception: pass
    def commit(self, event, payload):
        with self._lock:
            entry = {"ts": time.time(), "event": event, "payload": payload, "prev": self._prev}
            raw = json.dumps(entry, sort_keys=True)
            entry["hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self._prev = entry["hash"]
            return entry["hash"]
    def read_last(self, n=20):
        if not os.path.exists(self.path): return []
        with open(self.path, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        return [json.loads(l) for l in lines[-n:]]