import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_fix_intencao_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui a linha de import antiga pela correta
# O import atual deve ser algo como:
# from intelligence.feature_engine import extrair_intencao, extrair_features, carregar_memoria, guardar_memoria, extrair_chave_estavel
# (ou variacoes)
nova_linha = "from intelligence.feature_engine import extrair_chave_estavel, extrair_features, carregar_memoria, guardar_memoria"

# Encontra a linha atual do import do feature_engine
padrao = r"from intelligence\.feature_engine import [^\n]+"
if re.search(padrao, code):
    code = re.sub(padrao, nova_linha, code)
    print("[OK] Linha de import do feature_engine substituida.")
else:
    print("[AVISO] Linha de import nao encontrada. Vou tentar inserir.")
    # Se nao encontrou, insere antes do import do injector_engine ou do virtual_onnx
    if "from intelligence.injector_engine import" in code:
        code = code.replace("from intelligence.injector_engine import", nova_linha + "\nfrom intelligence.injector_engine import")
    else:
        code = nova_linha + "\n" + code

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)