# -*- coding: utf-8 -*-
import os, sys, time, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.telemetry import coletar
from core.event_bus import EventBus
from core.state import StateEstimator
from core.safety import SafetySupervisor
from core.audit import ZBITLedger

class Vigia:
    def __init__(self, ledger_path):
        self.bus = EventBus()
        self.estimator = StateEstimator()
        self.safety = SafetySupervisor()
        self.ledger = ZBITLedger(ledger_path)
        self._running = False
        self._thread = None
        self._last = None
    def _loop(self, interval=2.0):
        while self._running:
            try:
                snap = coletar()
                state = self.estimator.update(snap)
                check = self.safety.check(snap)
                payload = {"snapshot": snap, "state": state, "safety": check}
                self.bus.publish("telemetry", payload)
                self.ledger.commit("cycle", {"snapshot": snap, "safety": check})
                self._last = payload
            except Exception as e:
                print(f"[VIGIA] {e}")
            time.sleep(interval)
    def start(self, interval=2.0):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, args=(interval,), daemon=True)
        self._thread.start()
    def stop(self):
        self._running = False
    def last(self):
        return self._last