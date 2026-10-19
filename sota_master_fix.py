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
# PASSO 1: CURAR O FEATURE_ENGINE.PY (Garantir funções base)
# =========================================================================
if os.path.exists(FE_PATH):
    with open(FE_PATH, "r", encoding="utf-8") as f:
        fe_code = f.read()
    
    changed = False
    if "def extrair_intencao" not in fe_code:
        fe_code += "\n\ndef extrair_intencao(prompt: str) -> str:\n    p = prompt.lower()\n    tags = []\n    if any(k in p for k in ['velha', 'tic tac toe']): tags.append('velha')\n    if any(k in p for k in ['placar', 'placa']): tags.append('placar')\n    if any(k in p for k in ['empate']): tags.append('empate')\n    if any(k in p for k in ['cor', 'cores']): tags.append('cores')\n    return '_'.join(sorted(tags)) if tags else p.strip()\n"
        changed = True
    if "def extrair_features" not in fe_code:
        fe_code += "\n\ndef extrair_features(prompt: str) -> list:\n    return []\n"
        changed = True
        
    if changed:
        with open(FE_PATH, "w", encoding="utf-8") as f:
            f.write(fe_code)
        print("[OK] feature_engine.py atualizado com as funções.")
    else:
        print("[OK] feature_engine.py já estava completo.")

# =========================================================================
# PASSO 2: CURA CIRÚRGICA NO VIRTUAL_ONNX.PY
# =========================================================================
if os.path.exists(ONNX_PATH):
    bak_onnx = ONNX_PATH + ".bak_master_" + time.strftime("%H%M%S")
    shutil.copy2(ONNX_PATH, bak_onnx)
    
    with open(ONNX_PATH, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        
    # Remove qualquer bloco quebrado do try/except
    novas_linhas = []
    skip = False
    for linha in linhas:
        if linha.strip() == "try:" and any("from intelligence.feature_engine" in l for l in linhas[linhas.index(linha):linhas.index(linha)+3]):
            skip = True
            continue
        if skip:
            if "def extrair_features(p): return []" in linha:
                skip = False
            continue
        if "from intelligence.feature_engine import extrair_intencao" in linha:
            continue
        novas_linhas.append(linha)
        
    # Injeta o bloco perfeito no topo
    bloco_perfeito = [
        "try:\n",
        "    from intelligence.feature_engine import extrair_intencao, extrair_features\n",
        "except ImportError:\n",
        "    def extrair_intencao(p): return p.lower().strip()\n",
        "    def extrair_features(p): return []\n",
        "\n"
    ]
    # Garante que o bloco não seja duplicado se já existir corretamente
    if "from intelligence.feature_engine import extrair_intencao" not in "".join(novas_linhas):
        novas_linhas = bloco_perfeito + novas_linhas

    with open(ONNX_PATH, "w", encoding="utf-8") as f:
        f.writelines(novas_linhas)
        
    try:
        py_compile.compile(ONNX_PATH, doraise=True)
        print("[OK] virtual_onnx.py compilado com sucesso.")
    except Exception as e:
        print(f"[FALHA] virtual_onnx.py: {e}")
        shutil.copy2(bak_onnx, ONNX_PATH)

# =========================================================================
# PASSO 3: INTEGRAR PATCH ENGINE NO APP.PY
# =========================================================================
if os.path.exists(APP_PATH):
    bak_app = APP_PATH + ".bak_master_" + time.strftime("%H%M%S")
    shutil.copy2(APP_PATH, bak_app)
    
    with open(APP_PATH, "r", encoding="utf-8") as f:
        app_code = f.read()
        
    # Corrige o vault path
    if r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json" in app_code:
        app_code = app_code.replace(r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json", VAULT_CORRETO)
        print("[OK] Vault path corrigido.")

    # Adiciona imports do motor e backup
    if "from patch_engine import apply_patch_transaction" not in app_code:
        app_code = app_code.replace("import time", "import time\nfrom patch_engine import apply_patch_transaction, calculate_sha256, BaseConflictError, PatchValidationError\nfrom backup_manager import create_timestamped_backup")

    # Substitui a rota /api/generate_cloud pelo Mock do Motor
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
                db_path = cerebro.db_path
                
                intent = prompt.lower().strip()
                memoria = cerebro.dynamic_tools if hasattr(cerebro, 'dynamic_tools') else {}
                
                if intent in memoria:
                    entry = memoria[intent]
                    base_html = entry.get("html", "") if isinstance(entry, dict) else entry
                else:
                    base_html = "<!DOCTYPE html><html><body><div id='slot-main'><p>Original</p></div></body></html>"

                base_sha = calculate_sha256(base_html)
                
                # MOCK DA NUVEM: Simula o Contrato JSON
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

                import tempfile
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

                if hasattr(cerebro, 'dynamic_tools'):
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
        print("[OK] Rota /api/generate_cloud integrada com o Patch Engine.")
        try:
            py_compile.compile(APP_PATH, doraise=True)
            print("[OK] app.py compilado com sucesso.")
        except Exception as e:
            print(f"[FALHA] app.py: {e}")
            shutil.copy2(bak_app, APP_PATH)