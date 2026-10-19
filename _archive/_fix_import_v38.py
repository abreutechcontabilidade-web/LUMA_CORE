import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_fix_import_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remove a linha de import errada
erro_import = "from intelligence.injector_engine import detectar_posicao, injetar_feature, extrair_intencao"
certo_import = "from intelligence.injector_engine import detectar_posicao, injetar_feature"

if erro_import in code:
    code = code.replace(erro_import, certo_import)
    print("[OK] Import do injector_engine corrigido (removido 'extrair_intencao').")
else:
    print("[AVISO] Linha de import errada nao encontrada. Tentando regex...")
    code = re.sub(r"from intelligence\.injector_engine import [^\n]+", certo_import, code)

# 2. Garante que extrair_intencao vem do feature_engine
if "from intelligence.feature_engine import extrair_intencao" not in code:
    # Tenta adicionar ao import existente do feature_engine
    if "from intelligence.feature_engine import" in code:
        code = code.replace("from intelligence.feature_engine import", "from intelligence.feature_engine import extrair_intencao,")
    else:
        # Se nao houver nenhum import do feature_engine, cria um
        code = code.replace("from intelligence.injector_engine import", "from intelligence.feature_engine import extrair_intencao\nfrom intelligence.injector_engine import")
    print("[OK] Import de 'extrair_intencao' garantido (via feature_engine).")

# 3. Limpa imports duplicados ou mal formatados que possam ter ficado
code = re.sub(r"from intelligence\.feature_engine import extrair_intencao, carregar_memoria, guardar_memoria, extrair_intencao", "from intelligence.feature_engine import carregar_memoria, guardar_memoria, extrair_intencao", code)
code = re.sub(r"from intelligence\.feature_engine import extrair_intencao, extrair_features", "from intelligence.feature_engine import extrair_intencao, extrair_features", code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)