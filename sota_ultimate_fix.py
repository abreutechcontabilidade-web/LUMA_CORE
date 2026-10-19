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
# PASSO 1: CURAR O FEATURE_ENGINE.PY
# =========================================================================
if os.path.exists(FE_PATH):
    with open(FE_PATH, "r", encoding="utf-8") as f:
        fe_code = f.read()
    
    changed = False
    if "def extrair_intencao" not in fe_code:
        fe_code += (
            "\n\ndef extrair_intencao(prompt: str) -> str:\n"
            "    p = prompt.lower()\n"
            "    tags = []\n"
            "    if any(k in p for k in ['velha', 'tic tac toe']): tags.append('velha')\n"
            "    if any(k in p for k in ['placar', 'placa']): tags.append('placar')\n"
            "    if any(k in p for k in ['empate']): tags.append('empate')\n"
            "    if any(k in p for k in ['cor', 'cores']): tags.append('cores')\n"
            "    return '_'.join(sorted(tags)) if tags else p.strip()\n"
        )
        changed = True
    if "def extrair_features" not in fe_code:
        fe_code += "\n\ndef extrair_features(prompt: str) -> list:\n    return []\n"
        changed = True
        
    if changed:
        with open(FE_PATH, "w", encoding="utf-8") as f:
            f.write(fe_code)
        print("[OK] feature_engine.py atualizado.")
    else:
        print("[OK] feature_engine.py ja contem funcoes base.")

# =========================================================================
# PASSO 2: CURA DE INDENTAÇÃO E INJEÇÃO DE MÉTODOS NO VIRTUAL_ONNX.PY
# =========================================================================
if os.path.exists(ONNX_PATH):
    bak_onnx = ONNX_PATH + ".bak_master_" + time.strftime("%H%M%S")
    shutil.copy2(ONNX_PATH, bak_onnx)
    
    with open(ONNX_PATH, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        
    novas_linhas = []
    pulando = False
    for i, linha in enumerate(linhas):
        stripped = linha.strip()
        if stripped == "try:" and (i + 1 < len(linhas) and "from intelligence.feature_engine" in linhas[i + 1]):
            pulando = True
            continue
        if pulando:
            if "def extrair_features(p): return []" in linha:
                pulando = False
            continue
        if "from intelligence.feature_engine import extrair_intencao" in linha:
            continue
        novas_linhas.append(linha)
        
    bloco_perfeito = [
        "try:\n",
        "    from intelligence.feature_engine import extrair_intencao, extrair_features\n",
        "except ImportError:\n",
        "    def extrair_intencao(p): return p.lower().strip()\n",
        "    def extrair_features(p): return []\n\n"
    ]
    
    if "from intelligence.feature_engine import extrair_intencao" not in "".join(novas_linhas):
        novas_linhas = bloco_perfeito + novas_linhas

    # INJEÇÃO CIRÚRGICA DOS MÉTODOS EM FALTA NA CLASSE
    code_str = "".join(novas_linhas)
    if "class VirtualONNX:" in code_str:
        # Verifica se os métodos existem
        metodos_injetar = ""
        if "def __init__" not in code_str:
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
        if "def processar" not in code_str:
            metodos_injetar += """
    def processar(self, prompt):
        intent = prompt.lower().strip()
        if intent in self.dynamic_tools:
            entry = self.dynamic_tools[intent]
            return entry.get('html', '') if isinstance(entry, dict) else entry, 'APRENDIDO_LOCAL'
        return '<div>Jogo da Velha Básico (Local)</div>', 'LOCAL_BASIC'
"""
        if "def aprender_da_nuvem" not in code_str:
            metodos_injetar += """
    def aprender_da_nuvem(self, prompt, html):
        intent = prompt.lower().strip()
        self.dynamic_tools[intent] = {'html': html, 'features': []}
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.dynamic_tools, f, ensure_ascii=False, indent=2)
"""
        if metodos_injetar:
            # Encontra a linha da classe e insere os métodos
            idx_classe = code_str.find("class VirtualONNX:")
            fim_linha = code_str.find("\n", idx_classe)
            code_str = code_str[:fim_linha+1] + metodos_injetar + code_str[fim_linha+1:]

    if "import json" not in code_str: code_str = "import json\n" + code_str
    if "import os" not in code_str: code_str = "import os\n" + code_str

    with open(ONNX_PATH, "w", encoding="utf-8") as f:
        f.write(code_str)
        
    try:
        py_compile.compile(ONNX_PATH, doraise=True)
        print("[OK] virtual_onnx.py compilado com sucesso (métodos restaurados).")
    except Exception as e:
        print(f"[FALHA] virtual_onnx.py: {e}")
        shutil.copy2(bak_onnx, ONNX_PATH)

# =========================================================================
# PASSO 3: INTEGRAR PATCH ENGINE NO APP.PY (Script do CTO)
# =========================================================================
if os.path.exists(APP_PATH):
    bak_app = APP_PATH + ".bak_master_" + time.strftime("%H%M%S")
    shutil.copy2(APP_PATH, bak_app)
    
    with open(APP_PATH, "r", encoding="utf-8") as f:
        app_code = f.read()
        
    if r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json" in app_code:
        app_code = app_code.replace(r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json", VAULT_CORRETO)
        print("[OK] Vault path corrigido no app.py.")

    imports_necessarios = [
        "import json",
        "import os",
        "import tempfile",
        "from patch_engine import apply_patch_transaction, calculate_sha256, BaseConflictError, PatchValidationError",
        "from backup_manager import create_timestamped_backup"
    ]
    for imp in imports_necessarios:
        if imp not in app_code:
            app_code = imp + "\n" + app_code

    pattern = re.compile(r'(elif self\.path == "/api/generate_cloud":[\s\S]*?)(?=elif self\.path ==|def do_POST|\Z)')
    
    new_block = '''        elif self.path == "/api/generate_cloud":
            import time
            start_time = time.perf_counter()
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON inválido"}, 400)
                return

            try:
                from intelligence.virtual_onnx import VirtualONNX
                cerebro = VirtualONNX()
                db_path = getattr(cerebro, 'db_path', None)
                
                intent = prompt.lower().strip()
                memoria = getattr(cerebro, 'dynamic_tools', {})
                
                if intent in memoria:
                    entry = memoria[intent]
                    base_html = entry.get("html", "") if isinstance(entry, dict) else entry
                else:
                    base_html = "<!DOCTYPE html><html><body><div id=\'slot-main\'><p>Original</p></div></body></html>"
                
                base_sha = calculate_sha256(base_html)
                
                patch_payload = {
                    "schema_version": "1.0",
                    "base_sha256": base_sha,
                    "mutations": [{
                        "target_slot": "slot-main",
                        "op": "replace_inner",
                        "html": f"<div><p>Patch Engine SOTA Ativo. Prompt: {prompt}</p></div>"
                    }]
                }
                
                manifest = {"slots": {"slot-main": ["div", "p", "span"]}, "data_roles": [], "actions": []}
                temp_fd, temp_path = tempfile.mkstemp(suffix=".html", text=True)
                with os.fdopen(temp_fd, "w", encoding="utf-8") as tmp:
                    tmp.write(base_html)
                
                try:
                    novo_sha = apply_patch_transaction(temp_path, patch_payload, manifest)
                    with open(temp_path, "r", encoding="utf-8") as tmp:
                        novo_html = tmp.read()
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                if db_path and hasattr(cerebro, 'dynamic_tools'):
                    create_timestamped_backup(db_path)
                    cerebro.dynamic_tools[intent] = {"html": novo_html, "features": ["patch_applied"]}
                    with open(db_path, "w", encoding="utf-8") as f_db:
                        json.dump(cerebro.dynamic_tools, f_db, ensure_ascii=False, indent=2)

                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({
                    "status": "success",
                    "html": novo_html,
                    "fonte": "Patch Engine SOTA",
                    "elapsed_ms": elapsed
                })
            except Exception as e:
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                print(f"[ERRO PATCH ENGINE] {e}")
                self._send_json({
                    "status": "error",
                    "message": str(e),
                    "fonte": "Patch Engine (Falha)",
                    "elapsed_ms": elapsed
                }, 500)
'''

    new_code = pattern.sub(new_block, app_code)
    if new_code != app_code:
        with open(APP_PATH, "w", encoding="utf-8") as f:
            f.write(new_code)
        print("[OK] Rota /api/generate_cloud integrada.")
        try:
            py_compile.compile(APP_PATH, doraise=True)
            print("[OK] app.py compilado com sucesso.")
        except Exception as e:
            print(f"[FALHA] app.py: {e}")
            shutil.copy2(bak_app, APP_PATH)
    else:
        print("[AVISO] Bloco /api/generate_cloud nao encontrado ou ja modificado.")