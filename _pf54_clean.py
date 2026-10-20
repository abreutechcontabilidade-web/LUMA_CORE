import json, os, shutil, sys, time
DB = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
BAK = DB + ".bak_pf54_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(DB, BAK)
with open(DB, "r", encoding="utf-8") as f:
    mem = json.load(f)
kill = [k for k in list(mem.keys()) if "cobr" in k.lower()]
for k in kill:
    del mem[k]
    print("[OK] Cache removida: " + k)
tmp = DB + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, DB)
print("[OK] Cache limpa com backup: " + os.path.basename(BAK))