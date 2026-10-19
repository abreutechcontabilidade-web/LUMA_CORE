import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\feature_engine.py"
bak = path + ".bak_synonyms_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Adiciona sinonimos de posicao
old_pos = '''    if any(k in p for k in ["debaixo", "baixo", "fundo", "inferior"]): tags.append("baixo")
    if any(k in p for k in ["topo", "cima", "superior"]): tags.append("topo")'''

new_pos = '''    if any(k in p for k in ["debaixo", "baixo", "fundo", "inferior", "base", "parte de baixo"]): tags.append("baixo")
    if any(k in p for k in ["topo", "cima", "superior", "parte de cima"]): tags.append("topo")'''

if old_pos in code:
    code = code.replace(old_pos, new_pos)
    print("[OK] Sinonimos de posicao adicionados.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    code = re.sub(r'    if any\(k in p for k in \["debaixo", "baixo", "fundo", "inferior"\]\): tags\.append\("baixo"\)[\s\S]*?tags\.append\("topo"\)', new_pos, code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. feature_engine.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)