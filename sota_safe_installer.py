import os
import re
import shutil
import time
import py_compile

ROOT = r"C:\Users\user\Desktop\LUMA_CORE"
ONNX_PATH = os.path.join(ROOT, "intelligence", "virtual_onnx.py")
FE_PATH = os.path.join(ROOT, "intelligence", "feature_engine.py")
APP_PATH = os.path.join(ROOT, "server", "app.py")
VAULT_CORRETO = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"

# =========================================================================
# 1. CURA DO FEATURE_ENGINE.PY
# =========================================================================
if os.path.exists(FE_PATH):
    with open(FE_PATH, "r", encoding="utf-8") as f:
        fe_code = f.read()
    if "def extrair_intencao" not in fe_code:
        fe_code += "\n\ndef extrair_intencao(prompt: str) -> str:\n    p = prompt.lower()\n    tags = []\n    if any(k in p for k in ['velha', 'tic tac toe']): tags.append('velha')\n    if any(k in p for k in ['placar', 'placa']): tags.append('placar')\n    if any(k in p for k in ['empate']): tags.append('empate')\n    return '_'.join(sorted(tags)) if tags else p.strip()\n"
    if "def extrair_features" not in fe_code:
        fe_code += "\n\ndef extrair_features(prompt: str) -> list:\n    return []\n"
    with open(FE_PATH, "w", encoding="utf-8") as f:
        f.write(fe_code)

# =========================================================================
# 2. CURA DO VIRTUAL_ONNX.PY (Preserva a Lógica)
# =========================================================================
if os.path.exists(ONNX_PATH):
    bak_onnx = ONNX_PATH + ".bak_safe_" + time.strftime("%H%M%S")
    shutil.copy2(ONNX_PATH, bak_onnx)
    
    with open(ONNX_PATH, "r", encoding="utf-8") as f:
        onnx_code = f.read()

    # Remove blocos try/except quebrados do feature_engine
    onnx_code = re.sub(r"try:\s*\n\s*from intelligence\.feature_engine import.*?def extrair_features\(p\): return \[\]\s*\n", "", onnx_code, flags=re.DOTALL)
    
    # Injeta o bloco perfeito de import no topo
    bloco_perfeito = "try:\n    from intelligence.feature_engine import extrair_intencao, extrair_features\nexcept ImportError:\n    def extrair_intencao(p): return p.lower().strip()\n    def extrair_features(p): return []\n\n"
    if "from intelligence.feature_engine import extrair_intencao" not in onnx_code:
        onnx_code = bloco_perfeito + onnx_code

    # Verifica se a classe VirtualONNX precisa de métodos
    if "class VirtualONNX:" in onnx_code:
        metodos_injetar = ""
        if "def __init__" not in onnx_code:
            metodos_injetar += """
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'dynamic_tools.json')
        self.dynamic_tools = {}
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.dynamic_tools = json.load(f)
            except: pass
"""
        if "def processar" not in onnx_code:
            metodos_injetar += """
    def processar(self, prompt):
        intent = extrair_intencao(prompt) if 'extrair_intencao' in globals() else prompt.lower().strip()
        if intent in self.dynamic_tools:
            entry = self.dynamic_tools[intent]
            return entry.get('html', '') if isinstance(entry, dict) else entry, 'APRENDIDO_LOCAL'
        return '<div>Jogo da Velha Básico (Local)</div>', 'LOCAL_BASIC'
"""
        if "def aprender_da_nuvem" not in onnx_code:
            metodos_injetar += """
    def aprender_da_nuvem(self, prompt, html):
        intent = extrair_intencao(prompt) if 'extrair_intencao' in globals() else prompt.lower().strip()
        self.dynamic_tools[intent] = {'html': html, 'features': []}
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.dynamic_tools, f, ensure_ascii=False, indent=2)
"""
        if metodos_injetar:
            idx_classe = onnx_code.find("class VirtualONNX:")
            fim_linha = onnx_code.find("\n", idx_classe)
            onnx_code = onnx_code[:fim_linha+1] + metodos_injetar + onnx_code[fim_linha+1:]

    if "import json" not in onnx_code: onnx_code = "import json\n" + onnx_code
    if "import os" not in onnx_code: onnx_code = "import os\n" + onnx_code

    with open(ONNX_PATH, "w", encoding="utf-8") as f:
        f.write(onnx_code)
        
    try:
        py_compile.compile(ONNX_PATH, doraise=True)
        print("[OK] virtual_onnx.py curado e compilado.")
    except Exception as e:
        print(f"[FALHA] virtual_onnx.py: {e}")
        shutil.copy2(bak_onnx, ONNX_PATH)

# =========================================================================
# 3. CURA DO APP.PY (Apenas Imports e Vault)
# =========================================================================
if os.path.exists(APP_PATH):
    bak_app = APP_PATH + ".bak_safe_" + time.strftime("%H%M%S")
    shutil.copy2(APP_PATH, bak_app)
    
    with open(APP_PATH, "r", encoding="utf-8") as f:
        app_code = f.read()

    # Corrige o Vault
    if r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json" in app_code:
        app_code = app_code.replace(r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json", VAULT_CORRETO)

    # Garante os imports necessários no topo
    imports = [
        "import json",
        "import os",
        "import tempfile",
        "from patch_engine import apply_patch_transaction, calculate_sha256",
        "from backup_manager import create_timestamped_backup"
    ]
    for imp in imports:
        if imp not in app_code:
            app_code = imp + "\n" + app_code

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(app_code)

    try:
        py_compile.compile(APP_PATH, doraise=True)
        print("[OK] app.py compilado com sucesso (Imports e Vault corrigidos).")
    except Exception as e:
        print(f"[FALHA] app.py: {e}")
        shutil.copy2(bak_app, APP_PATH)