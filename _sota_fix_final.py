import os
import shutil
import time
import py_compile

ROOT = r"C:\Users\user\Desktop\LUMA_CORE"
ONNX_PATH = os.path.join(ROOT, "intelligence", "virtual_onnx.py")
APP_PATH = os.path.join(ROOT, "server", "app.py")
VAULT_CORRETO = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"

# =========================================================================
# PASSO 1: Curar virtual_onnx.py (Indentação exata de 4 espaços)
# =========================================================================
if os.path.exists(ONNX_PATH):
    bak_onnx = f"{ONNX_PATH}.bak_sota_{time.strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(ONNX_PATH, bak_onnx)
    
    with open(ONNX_PATH, "r", encoding="utf-8") as f:
        linhas = f.readlines()
    
    # Bloco sintaticamente perfeito
    bloco_correto = [
        "try:\n",
        "    from intelligence.feature_engine import extrair_intencao, extrair_features\n",
        "except ImportError:\n",
        "    def extrair_intencao(p): return p.lower().strip()\n",
        "    def extrair_features(p): return []\n"
    ]
    
    # Localiza onde está o try/from quebrado
    idx_inicio = -1
    for i, linha in enumerate(linhas):
        if "from intelligence.feature_engine import extrair_intencao" in linha:
            idx_inicio = i - 1 if i > 0 and linhas[i - 1].strip() == "try:" else i
            break
            
    if idx_inicio != -1:
        # Encontra o final do bloco defeituoso
        idx_fim = idx_inicio + 1
        while idx_fim < len(linhas) and (
            linhas[idx_fim].strip() == "" or
            "import" in linhas[idx_fim] or
            "def extrair" in linhas[idx_fim] or
            "except" in linhas[idx_fim]
        ):
            idx_fim += 1
        
        linhas[idx_inicio:idx_fim] = bloco_correto
    else:
        # Se não achou o ponto exato, insere de forma segura no início
        linhas.insert(0, "".join(bloco_correto) + "\n")
        
    with open(ONNX_PATH, "w", encoding="utf-8") as f:
        f.writelines(linhas)
        
    try:
        py_compile.compile(ONNX_PATH, doraise=True)
        print("[SOTA-ONNX] virtual_onnx.py curado e compilado com sucesso (AST valida).")
    except Exception as e:
        print(f"[ERRO-ONNX] Falha na compilacao: {e}")
        shutil.copy2(bak_onnx, ONNX_PATH)

# =========================================================================
# PASSO 2: Ajustar caminho do Vault no app.py
# =========================================================================
if os.path.exists(APP_PATH):
    bak_app = f"{APP_PATH}.bak_sota_{time.strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(APP_PATH, bak_app)
    
    with open(APP_PATH, "r", encoding="utf-8") as f:
        conteudo_app = f.read()
        
    vault_errado = r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json"
    if vault_errado in conteudo_app:
        conteudo_app = conteudo_app.replace(vault_errado, VAULT_CORRETO)
        with open(APP_PATH, "w", encoding="utf-8") as f:
            f.write(conteudo_app)
        print("[SOTA-APP] Caminho do vault.json atualizado para o repositorio principal.")
    else:
        print("[SOTA-APP] Caminho do vault.json ja estava correto ou nao encontrado.")
        
    try:
        py_compile.compile(APP_PATH, doraise=True)
        print("[SOTA-APP] app.py compilado com sucesso.")
    except Exception as e:
        print(f"[ERRO-APP] Falha no app.py: {e}")
        shutil.copy2(bak_app, APP_PATH)