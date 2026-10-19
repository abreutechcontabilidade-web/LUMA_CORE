import os, re, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_safe_integration_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup criado: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Adiciona os imports (se não existirem)
if "from patch_engine import apply_patch_transaction" not in code:
    code = code.replace("import time", "import time\nfrom patch_engine import apply_patch_transaction, calculate_sha256, BaseConflictError, PatchValidationError")
    print("[OK] Imports do motor adicionados.")

# 2. Substitui a rota da nuvem
marker = 'elif self.path == "/api/generate_cloud":'
if marker not in code:
    print("[ERRO] Marcador da rota '/api/generate_cloud' não encontrado. O arquivo pode estar diferente. Abortando sem salvar.")
else:
    # Encontra o bloco da rota e substitui
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
                
                # MOCK DA NUVEM
                patch_payload = {
                    "schema_version": "1.0",
                    "base_sha256": base_sha,
                    "mutations": [{
                        "target_slot": "slot-main",
                        "op": "replace_inner",
                        "html": f"<div><p>Processado pelo Motor SOTA (Mock). Prompt: {prompt}</p></div>"
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
                    cerebro.dynamic_tools[intent] = {"html": novo_html, "features": ["patch_applied"]}
                    import json
                    with open(db_path, "w", encoding="utf-8") as f_db:
                        json.dump(cerebro.dynamic_tools, f_db, ensure_ascii=False, indent=2)

                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({
                    "status": "success",
                    "html": novo_html,
                    "fonte": "Patch Engine (Mock LLM)",
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

    new_code = pattern.sub(new_block, code)
    
    if new_code == code:
        print("[ERRO] O bloco da rota não foi alterado. Padrão diferente no arquivo. Abortando.")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_code)
        print("[OK] Rota /api/generate_cloud reescrita.")

        # Validação da sintaxe
        try:
            py_compile.compile(path, doraise=True)
            print("[OK] Sintaxe validada com sucesso.")
        except Exception as e:
            print(f"[ERRO CRÍTICO] Erro de sintaxe: {e}")
            shutil.copy2(bak, path)
            print("[OK] Backup restaurado. O arquivo original foi preservado.")
