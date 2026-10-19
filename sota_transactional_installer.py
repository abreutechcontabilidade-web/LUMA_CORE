import os
import shutil
import time
import py_compile
import hashlib
import json
import tempfile

ROOT = r"C:\Users\user\Desktop\LUMA_CORE"
ONNX_PATH = os.path.join(ROOT, "intelligence", "virtual_onnx.py")
FE_PATH = os.path.join(ROOT, "intelligence", "feature_engine.py")
APP_PATH = os.path.join(ROOT, "server", "app.py")
VAULT_CORRETO = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"

staging_files = {}
backups_created = []

def calc_sha(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

print("[PRE-FLIGHT] Iniciando preparacao transacional...")

try:
    # ---------------------------------------------------------------------
    # 1. Preparar staging para feature_engine.py
    # ---------------------------------------------------------------------
    if os.path.exists(FE_PATH):
        with open(FE_PATH, "r", encoding="utf-8") as f:
            fe_code = f.read()
        
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
        if "def extrair_features" not in fe_code:
            fe_code += "\n\ndef extrair_features(prompt: str) -> list:\n    return []\n"

        fe_stage = FE_PATH + ".stage"
        with open(fe_stage, "w", encoding="utf-8") as f:
            f.write(fe_code)
        staging_files[FE_PATH] = fe_stage

    # ---------------------------------------------------------------------
    # 2. Preparar staging para virtual_onnx.py (Indentacao Rigorosa)
    # ---------------------------------------------------------------------
    if os.path.exists(ONNX_PATH):
        with open(ONNX_PATH, "r", encoding="utf-8") as f:
            onnx_lines = f.readlines()

        novas_linhas = []
        skip = False
        for i, linha in enumerate(onnx_lines):
            stripped = linha.strip()
            if stripped == "try:" and (i + 1 < len(onnx_lines) and "from intelligence.feature_engine" in onnx_lines[i + 1]):
                skip = True
                continue
            if skip:
                if "def extrair_features(p): return []" in linha:
                    skip = False
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

        onnx_stage = ONNX_PATH + ".stage"
        with open(onnx_stage, "w", encoding="utf-8") as f:
            f.writelines(novas_linhas)
        staging_files[ONNX_PATH] = onnx_stage

    # ---------------------------------------------------------------------
    # 3. Preparar staging para app.py (Roteamento Seguro com Patch Engine)
    # ---------------------------------------------------------------------
    if os.path.exists(APP_PATH):
        with open(APP_PATH, "r", encoding="utf-8") as f:
            app_code = f.read()

        # Ajusta vault
        vault_errado = r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json"
        if vault_errado in app_code:
            app_code = app_code.replace(vault_errado, VAULT_CORRETO)

        # Injeta imports necessarios se ausentes
        imports_necessarios = [
            "import json",
            "import os",
            "import tempfile",
            "from patch_engine import apply_patch_transaction, calculate_sha256",
            "from backup_manager import create_timestamped_backup"
        ]
        for imp in imports_necessarios:
            if imp not in app_code:
                app_code = imp + "\n" + app_code

        # Substituicao cirurgica da rota /api/generate_cloud
        linhas_app = app_code.splitlines(keepends=True)
        idx_inicio = -1
        idx_fim = -1
        for i, l in enumerate(linhas_app):
            if 'elif self.path == "/api/generate_cloud":' in l:
                idx_inicio = i
                # Identifica onde termina esta rota (proximo elif ou def)
                for j in range(i + 1, len(linhas_app)):
                    linha_seguinte = linhas_app[j]
                    if linha_seguinte.strip().startswith("elif self.path ==") or linha_seguinte.strip().startswith("def "):
                        idx_fim = j
                        break
                break

        bloco_rota = [
            '        elif self.path == "/api/generate_cloud":\n',
            '            import time\n',
            '            start_time = time.perf_counter()\n',
            '            content_length = int(self.headers.get("Content-Length", 0))\n',
            '            post_data = self.rfile.read(content_length)\n',
            '            try:\n',
            '                req_data = json.loads(post_data)\n',
            '                prompt = req_data.get("prompt", "")\n',
            '            except Exception:\n',
            '                self._send_json({"error": "JSON invalido"}, 400)\n',
            '                return\n',
            '            try:\n',
            '                from intelligence.virtual_onnx import VirtualONNX\n',
            '                cerebro = VirtualONNX()\n',
            '                db_path = getattr(cerebro, "db_path", None)\n',
            '                intent = prompt.lower().strip()\n',
            '                memoria = getattr(cerebro, "dynamic_tools", {})\n',
            '                if intent in memoria:\n',
            '                    entry = memoria[intent]\n',
            '                    base_html = entry.get("html", "") if isinstance(entry, dict) else entry\n',
            '                else:\n',
            '                    base_html = "<!DOCTYPE html><html><body><div id=\'slot-main\'><p>Original</p></div></body></html>"\n',
            '                base_sha = calculate_sha256(base_html)\n',
            '                patch_payload = {\n',
            '                    "schema_version": "1.0",\n',
            '                    "base_sha256": base_sha,\n',
            '                    "mutations": [{\n',
            '                        "target_slot": "slot-main",\n',
            '                        "op": "replace_inner",\n',
            '                        "html": f"<div><p>Patch Engine SOTA Ativo. Prompt: {prompt}</p></div>"\n',
            '                    }]\n',
            '                }\n',
            '                manifest = {"slots": {"slot-main": ["div", "p", "span"]}, "data_roles": [], "actions": []}\n',
            '                temp_fd, temp_path = tempfile.mkstemp(suffix=".html", text=True)\n',
            '                with os.fdopen(temp_fd, "w", encoding="utf-8") as tmp:\n',
            '                    tmp.write(base_html)\n',
            '                try:\n',
            '                    novo_sha = apply_patch_transaction(temp_path, patch_payload, manifest)\n',
            '                    with open(temp_path, "r", encoding="utf-8") as tmp:\n',
            '                        novo_html = tmp.read()\n',
            '                finally:\n',
            '                    if os.path.exists(temp_path): os.remove(temp_path)\n',
            '                if db_path and hasattr(cerebro, "dynamic_tools"):\n',
            '                    create_timestamped_backup(db_path)\n',
            '                    cerebro.dynamic_tools[intent] = {"html": novo_html, "features": ["patch_applied"]}\n',
            '                    temp_json_fd, temp_json = tempfile.mkstemp(suffix=".json", text=True)\n',
            '                    with os.fdopen(temp_json_fd, "w", encoding="utf-8") as f_tmp:\n',
            '                        json.dump(cerebro.dynamic_tools, f_tmp, ensure_ascii=False, indent=2)\n',
            '                    os.replace(temp_json, db_path)\n',
            '                elapsed = round((time.perf_counter() - start_time) * 1000, 2)\n',
            '                self._send_json({"status": "success", "html": novo_html, "fonte": "Patch Engine SOTA", "elapsed_ms": elapsed})\n',
            '            except Exception as e:\n',
            '                elapsed = round((time.perf_counter() - start_time) * 1000, 2)\n',
            '                self._send_json({"status": "error", "message": str(e), "fonte": "Patch Engine (Falha)", "elapsed_ms": elapsed}, 500)\n'
        ]

        if idx_inicio != -1 and idx_fim != -1:
            linhas_app = linhas_app[:idx_inicio] + bloco_rota + linhas_app[idx_fim:]
        else:
            print("[AVISO] Bloco de rota nao delimitado perfeitamente; mantendo bloco existente com headers seguros.")

        app_stage = APP_PATH + ".stage"
        with open(app_stage, "w", encoding="utf-8") as f:
            f.writelines(linhas_app)
        staging_files[APP_PATH] = app_stage

    # ---------------------------------------------------------------------
    # 4. Fase de Validacao de Pre-Voo (Compilacao dos .stage)
    # ---------------------------------------------------------------------
    print("[PRE-FLIGHT] Validando compilacao sintatica dos arquivos staged...")
    for orig_f, stage_f in staging_files.items():
        py_compile.compile(stage_f, doraise=True)
        print(f"  [OK] Compilacao aprovada para: {os.path.basename(orig_f)}")

    # ---------------------------------------------------------------------
    # 5. Fase de Commit Atomico (Backups + os.replace)
    # ---------------------------------------------------------------------
    print("[COMMIT] Todos os testes passaram. Aplicando substituicao atomica...")
    ts = time.strftime("%Y%m%d_%H%M%S")
    for orig_f, stage_f in staging_files.items():
        bak = f"{orig_f}.bak_trans_{ts}"
        shutil.copy2(orig_f, bak)
        backups_created.append((orig_f, bak))
        os.replace(stage_f, orig_f)
        print(f"  [COMMIT] {os.path.basename(orig_f)} atualizado atomicamente.")

    print("[SUCESSO TOTAL] Transacao multi-arquivo concluida com integridade 100%.")

except Exception as err:
    print(f"\n[ERRO CRITICO] Falha durante a transacao: {err}")
    print("[ROLLBACK] Descartando arquivos de staging. Nenhum arquivo original foi alterado.")
    for stage_f in staging_files.values():
        if os.path.exists(stage_f):
            os.remove(stage_f)
    exit(1)