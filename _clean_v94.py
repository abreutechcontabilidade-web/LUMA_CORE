import json, os
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)
# Remove todas as variações de chaves da cobra
keys_to_remove = [k for k in mem.keys() if "cobr" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido: {k}")
tmp = db_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, db_path)