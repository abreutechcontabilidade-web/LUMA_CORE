import os
import re
import shutil
import time
import py_compile

# =========================================================================
# PASSO 1: CURA DO VIRTUAL_ONNX.PY (Remover lixo e injetar bloco perfeito)
# =========================================================================
onnx_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak_onnx = onnx_path + ".bak_absolute_" + time.strftime("%H%M%S")
shutil.copy2(onnx_path, bak_onnx)

with open(onnx_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove QUALQUER bloco try/except relacionado ao feature_engine que esteja quebrado
content = re.sub(r"try:\s*\n\s*from intelligence\.feature_engine import.*?def extrair_features\(p\): return \[\]\s*\n", "", content, flags=re.DOTALL)
content = re.sub(r"try:\s*\n\s*from intelligence\.feature_engine import.*?def extrair_intencao\(p\): return p\.lower\(\)\.strip\(\)\s*\n", "", content, flags=re.DOTALL)

# Injeta o bloco perfeito no topo do arquivo
clean_block = """try:
    from intelligence.feature_engine import extrair_intencao, extrair_features
except ImportError:
    def extrair_intencao(p): return p.lower().strip()
    def extrair_features(p): return []

"""
if "from intelligence.feature_engine import extrair_intencao" not in content:
    content = clean_block + content

with open(onnx_path, "w", encoding="utf-8") as f:
    f.write(content)

try:
    py_compile.compile(onnx_path, doraise=True)
    print("[SUCESSO] virtual_onnx.py limpo e compilado.")
except Exception as e:
    print(f"[FALHA] virtual_onnx.py: {e}")
    shutil.copy2(bak_onnx, onnx_path)

# =========================================================================
# PASSO 2: CURA DO FEATURE_ENGINE.PY (Garantir que as funções existem)
# =========================================================================
fe_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\feature_engine.py"
bak_fe = fe_path + ".bak_absolute_" + time.strftime("%H%M%S")

if os.path.exists(fe_path):
    shutil.copy2(fe_path, bak_fe)
    with open(fe_path, "r", encoding="utf-8") as f:
        fe_code = f.read()
        
    if "def extrair_intencao" not in fe_code:
        fe_code += "\n\ndef extrair_intencao(prompt: str) -> str:\n    p = prompt.lower()\n    tags = []\n    if any(k in p for k in ['velha', 'tic tac toe']): tags.append('velha')\n    if any(k in p for k in ['placar', 'placa']): tags.append('placar')\n    if any(k in p for k in ['empate']): tags.append('empate')\n    if any(k in p for k in ['cor', 'cores']): tags.append('cores')\n    return '_'.join(sorted(tags)) if tags else p.strip()\n"
        
    if "def extrair_features" not in fe_code:
        fe_code += "\n\ndef extrair_features(prompt: str) -> list:\n    return []\n"
        
    with open(fe_path, "w", encoding="utf-8") as f:
        f.write(fe_code)
        
    try:
        py_compile.compile(fe_path, doraise=True)
        print("[SUCESSO] feature_engine.py atualizado com as funcoes.")
    except Exception as e:
        print(f"[FALHA] feature_engine.py: {e}")
        shutil.copy2(bak_fe, fe_path)

# =========================================================================
# PASSO 3: AJUSTAR O VAULT NO APP.PY (Se necessário)
# =========================================================================
app_path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
vault_errado = r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json"
vault_correto = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"

if os.path.exists(app_path):
    bak_app = app_path + ".bak_absolute_" + time.strftime("%H%M%S")
    shutil.copy2(app_path, bak_app)
    with open(app_path, "r", encoding="utf-8") as f:
        app_code = f.read()
    if vault_errado in app_code:
        app_code = app_code.replace(vault_errado, vault_correto)
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(app_code)
        print("[OK] Vault path corrigido no app.py.")