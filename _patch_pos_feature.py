import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\feature_engine.py"
bak = path + ".bak_pos_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Adiciona "topo" e "baixo" as features
old_features = '''    if any(k in p for k in ["proxima", "próxima", "rodada"]): features.append("proxima_rodada")
    if any(k in p for k in ["reiniciar", "zerar"]): features.append("reiniciar")
    return features'''

new_features = '''    if any(k in p for k in ["proxima", "próxima", "rodada"]): features.append("proxima_rodada")
    if any(k in p for k in ["reiniciar", "zerar"]): features.append("reiniciar")
    if any(k in p for k in ["topo", "superior", "cima"]): features.append("topo")
    if any(k in p for k in ["baixo", "inferior", "fundo", "base"]): features.append("baixo")
    return features'''

if old_features in code:
    code = code.replace(old_features, new_features)
    print("[OK] Features de posicao adicionadas.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    code = re.sub(r'    if any\(k in p for k in \["proxima", "próxima", "rodada"\]\): features\.append\("proxima_rodada"\)[\s\S]*?return features', new_features, code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. feature_engine.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)