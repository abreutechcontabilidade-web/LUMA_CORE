import json, os
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
# Cria um ficheiro JSON vazio (destrói a cache antiga)
with open(db_path, "w", encoding="utf-8") as f:
    json.dump({}, f, ensure_ascii=False, indent=2)
print("[OK] Genoma limpo. A cache 'ONNX_CACHE_PURO' foi destruida.")