import os, json, py_compile

# ==========================================
# 1. O KNOWLEDGE MAPPER (Crawler Diário)
# ==========================================
mapper_code = r'''
import urllib.request
import urllib.parse
import json
import os
import time
import sys

sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from intelligence.github_learner import aprender_do_github

DB_PATH = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"

# Lista de intenções base para abastecer o cérebro
INTENCOES_ALVO = [
    "jogo da cobra",
    "jogo da velha",
    "calculadora",
    "cronometro",
    "lista de tarefas",
    "quiz"
]

def abastecer_genoma():
    print("[KNOWLEDGE MAPPER] Iniciando mapeamento profundo da web...")
    
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            memoria = json.load(f)
    else:
        memoria = {}

    for intencao in INTENCOES_ALVO:
        chave = intencao.replace(" ", "_")
        if chave in memoria:
            print(f"[SKIP] '{intencao}' ja esta no genoma.")
            continue
            
        print(f"\n[MAPPER] A procurar codigo para: '{intencao}'...")
        html, proveniencia = aprender_do_github(intencao)
        
        if html:
            memoria[chave] = {
                "html": html,
                "features": ["mapeado_web"],
                "proveniencia": proveniencia,
                "timestamp": time.time()
            }
            print(f"[OK] '{intencao}' aprendido e guardado! (Fonte: {proveniencia.get('repo', 'unknown')})")
            
            # GATE-19: Escrita atomica a cada novo item
            tmp = DB_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(memoria, f, ensure_ascii=False, indent=2)
            os.replace(tmp, DB_PATH)
        else:
            print(f"[FALHA] Nao foi possivel encontrar '{intencao}'.")

    print("\n[KNOWLEDGE MAPPER] Mapeamento concluido. O ONNX Local esta abastecido.")

if __name__ == "__main__":
    abastecer_genoma()
'''

mapper_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\knowledge_mapper.py"
with open(mapper_path, "w", encoding="utf-8") as f:
    f.write(mapper_code)
print("[OK] knowledge_mapper.py criado (O Abastecedor Diário).")

# ==========================================
# 2. ATUALIZANDO A ROTA PARA LER O MAPPER
# ==========================================
# O ONNX já lê o dynamic_tools.json. Se o Mapper encher o JSON, o ONNX
# vai automaticamente encontrar a resposta em 5ms.

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU.")