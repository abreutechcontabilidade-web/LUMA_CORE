# -*- coding: utf-8 -*-
import os, shutil, subprocess, time, platform
from datetime import datetime, timezone

def _cpu():
    try:
        import psutil
        return {"value": psutil.cpu_percent(interval=0.1), "quality": "measured"}
    except ImportError:
        pass
    try:
        out = subprocess.check_output(["wmic", "cpu", "get", "loadpercentage"], text=True, timeout=3)
        nums = [l.strip() for l in out.splitlines() if l.strip().isdigit()]
        if nums:
            return {"value": int(nums[0]), "quality": "measured"}
    except Exception:
        pass
    return {"value": None, "quality": "unavailable"}

def _memory():
    try:
        import psutil
        m = psutil.virtual_memory()
        return {"total_mb": round(m.total/1e6), "used_mb": round(m.used/1e6), "percent": m.percent, "quality": "measured"}
    except ImportError:
        pass
    try:
        out = subprocess.check_output(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/format:list"], text=True, timeout=3)
        free = total = None
        for line in out.splitlines():
            if line.startswith("FreePhysicalMemory="):
                v = line.split("=")[1].strip()
                if v: free = int(v)/1024
            elif line.startswith("TotalVisibleMemorySize="):
                v = line.split("=")[1].strip()
                if v: total = int(v)/1024
        if free is not None and total:
            used = total - free
            return {"total_mb": round(total), "used_mb": round(used), "percent": round(used/total*100,1), "quality": "measured"}
    except Exception:
        pass
    return {"total_mb": None, "used_mb": None, "percent": None, "quality": "unavailable"}

def _disk():
    try:
        import psutil
        d = psutil.disk_usage(os.path.abspath(os.sep))
        return {"total_gb": round(d.total/1e9,1), "used_gb": round(d.used/1e9,1), "percent": d.percent, "quality": "measured"}
    except ImportError:
        pass
    try:
        total, used, _ = shutil.disk_usage(os.path.abspath(os.sep))
        return {"total_gb": round(total/1e9,1), "used_gb": round(used/1e9,1), "percent": round(used/total*100,1), "quality": "measured"}
    except Exception:
        pass
    return {"total_gb": None, "used_gb": None, "percent": None, "quality": "unavailable"}

def _uptime():
    try:
        import psutil
        return {"seconds": round(time.time() - psutil.boot_time()), "quality": "measured"}
    except ImportError:
        pass
    try:
        out = subprocess.check_output(["wmic", "OS", "get", "LastBootUpTime"], text=True, timeout=3)
        for line in out.splitlines():
            s = line.strip()
            if len(s) >= 14 and s[:14].isdigit():
                boot = datetime.strptime(s[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
                return {"seconds": round((datetime.now(timezone.utc) - boot).total_seconds()), "quality": "measured"}
    except Exception:
        pass
    return {"seconds": None, "quality": "unavailable"}

def coletar():
    t0 = time.perf_counter()
    snap = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": platform.node(),
        "os": platform.system() + " " + platform.release(),
        "cpu": _cpu(),
        "memory": _memory(),
        "disk": _disk(),
        "uptime": _uptime(),
    }
    snap["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return snap