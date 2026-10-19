import json
import os

vault_path = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"
if os.path.exists(vault_path):
    with open(vault_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[INFO] Tipo do objeto raiz: {type(data).__name__}")
    if isinstance(data, dict):
        print(f"[INFO] Chaves no topo: {list(data.keys())}")
        # Mostra o primeiro item de cada chave para entender o formato
        for k, v in data.items():
            print(f" -> Chave '{k}' contém: {type(v).__name__} (ex: {str(v)[:80]}...)")
    elif isinstance(data, list):
        print(f"[INFO] Lista com {len(data)} itens. Primeiro item: {str(data[0])[:100]}...")
else:
    print(f"[ERRO] Vault não encontrado em: {vault_path}")