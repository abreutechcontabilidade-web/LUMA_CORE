import json, os
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)
keys_to_remove = [k for k in mem.keys() if "cobra" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")
tmp_path = db_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp_path, db_path)
print("[OK] Genoma limpo (escrita atomica).")