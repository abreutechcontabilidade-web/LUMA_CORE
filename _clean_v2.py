import json, os
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

# A chave gerada pelo app.py e prompt.lower().replace(" ", "_")[:20]
key_to_remove = "criar_jogo_da_cobrin"
if key_to_remove in mem:
    del mem[key_to_remove]
    print(f"[OK] Removido do genoma: {key_to_remove}")

tmp = db_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, db_path)
print("[OK] Genoma limpo.")