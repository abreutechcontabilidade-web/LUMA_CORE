import json
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json", "w", encoding="utf-8") as f:
    json.dump({}, f, ensure_ascii=False, indent=2)
print("[OK] Cache limpo. O motor vai ao GitHub.")