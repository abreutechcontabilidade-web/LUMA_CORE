import os, json, time

db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"

if not os.path.exists(db_path):
    print("[ERRO] dynamic_tools.json nao existe.")
    exit(1)

with open(db_path, "r", encoding="utf-8") as f:
    memoria = json.load(f)

entry = memoria.get("jogo_da_velha", {})
html_atual = entry.get("html", "") if isinstance(entry, dict) else entry

if not html_atual or len(str(html_atual).strip()) < 10:
    print("[AVISO] HTML vazio detetado! A injetar HTML Base Local...")
    
    html_base = """<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; }
</style>
</head>
<body>
<h1>Jogo da Velha Base</h1>
<div id="board" style="display: grid; grid-template-columns: repeat(3, 50px); gap: 5px;">
    <div class="cell"></div><div class="cell"></div><div class="cell"></div>
</div>
<script>
// Logica basica aqui
</script>
</body>
</html>"""
    
    if isinstance(entry, dict):
        memoria["jogo_da_velha"]["html"] = html_base
    else:
        memoria["jogo_da_velha"] = {"html": html_base, "features": []}
        
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)
    print("[OK] HTML Base injetado no dicionario com sucesso.")
else:
    print("[OK] O HTML existe no JSON, o problema pode ser outro.")

# Agora testa o motor de sintese novamente
import sys
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from intelligence.local_synthesis import processar_sintese

print("\n=== TESTANDO A EVOLUCAO LOCAL ===")
html_evoluido, status = processar_sintese("criar jogo da velha com som e cor vermelha")
print(f"Status: {status}")
if html_evoluido and len(str(html_evoluido)) > 10:
    print(f"[SUCESSO] Tamanho do HTML evoluido: {len(html_evoluido)} caracteres.")
    print(f"Tem botao de som? {'Tocar Som' in html_evoluido}")
    print(f"Tem fundo vermelho? {'background-color: #8b0000' in html_evoluido}")
else:
    print("[ERRO] Ainda retornou vazio.")