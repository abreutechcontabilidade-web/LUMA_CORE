# -*- coding: utf-8 -*-
class EMA:
    def __init__(self, alpha=0.3, v=None):
        self.alpha = alpha
        self.v = v
    def update(self, x):
        if x is None: return self.v
        self.v = x if self.v is None else self.alpha * x + (1 - self.alpha) * self.v
        return self.v

class StateEstimator:
    def __init__(self):
        self.cpu = EMA(0.3); self.mem = EMA(0.3); self.disk = EMA(0.3)
    def update(self, snap):
        c = snap.get("cpu", {}).get("value")
        m = snap.get("memory", {}).get("percent")
        d = snap.get("disk", {}).get("percent")
        if c is not None: self.cpu.update(c)
        if m is not None: self.mem.update(m)
        if d is not None: self.disk.update(d)
        return {
            "cpu_ema": round(self.cpu.v,1) if self.cpu.v is not None else None,
            "mem_ema": round(self.mem.v,1) if self.mem.v is not None else None,
            "disk_ema": round(self.disk.v,1) if self.disk.v is not None else None,
        }