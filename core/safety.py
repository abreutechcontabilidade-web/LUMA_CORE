# -*- coding: utf-8 -*-
class SafetySupervisor:
    LIMITS = {"cpu": 90, "memory": 85, "disk": 90}
    def check(self, snap):
        res = {"ok": True, "warnings": []}
        for field, key in (("cpu","cpu"),("memory","memory"),("disk","disk")):
            if field == "cpu":
                val = snap.get("cpu", {}).get("value")
            else:
                val = snap.get(field, {}).get("percent")
            if val is not None and val > self.LIMITS[field]:
                res["ok"] = False
                res["warnings"].append(f"{field}={val} excede {self.LIMITS[field]}")
        return res