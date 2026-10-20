import json, os
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
# Cria um dicionário vazio (apaga todas as chaves)
with open(db_path, "w", encoding="utf-8") as f:
    json.dump({}, f, ensure_ascii=False, indent=2)
print("[OK] Cache totalmente destruido. O motor vai ao GitHub.")