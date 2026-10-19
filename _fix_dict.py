import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\feature_engine.py"
if not os.path.exists(path):
    print("[ERRO] feature_engine.py nao encontrado.")
    exit(1)

bak = path + ".bak_dict_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui a tag "velha" por "jogo_da_velha"
if 'tags.append("velha")' in code:
    code = code.replace('tags.append("velha")', 'tags.append("jogo_da_velha")')
    print("[OK] Dicionario corrigido: agora extrai 'jogo_da_velha'.")
else:
    print("[AVISO] Padrao 'tags.append(\"velha\")' nao encontrado. Verificando outras formas...")
    code = code.replace('"velha",', '"jogo_da_velha",').replace("'velha',", "'jogo_da_velha',")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Dicionario atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)