import re, sys, shutil, time, py_compile, os

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_integrate_engine_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Adiciona os imports do motor no topo (se não existirem)
if "from patch_engine import apply_patch_transaction, calculate_sha256, BaseConflictError, PatchValidationError" not in code:
    code = code.replace("import time", "import time\nfrom patch_engine import apply_patch_transaction, calculate_sha256, BaseConflictError, PatchValidationError")
    print("[OK] Imports do patch_engine adicionados.")

# 2. Substitui a lógica da rota /api/generate_cloud
# Encontra o bloco da rota e substitui até a próxima definição de rota (ou função)
pattern = r'(elif self\.path == "/api/generate_cloud":[\s\S]*?)(?=elif self\.path ==|def do_POST|\Z)'

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
                
                # Carrega a memória (HTML atual)
                # Para o teste, usamos um HTML base fixo se não houver nada salvo
                intent = prompt.lower().strip()
                memoria = cerebro.dynamic_tools if hasattr(cerebro, 'dynamic_tools') else {}
                
                if intent in memoria:
                    entry = memoria[intent]
                    base_html = entry.get("html", "") if isinstance(entry, dict) else entry
                else:
                    base_html = "<!DOCTYPE html><html><body><div id='slot-main'><p>Original</p></div></body></html>"

                base_sha = calculate_sha256(base_html)
                
                # --- MOCK DA NUVEM ---
                # Simulamos a resposta do LLM com o Contrato JSON
                patch_payload = {
                    "schema_version": "1.0",
                    "base_sha256": base_sha,
                    "mutations": [{
                        "target_slot": "slot-main",
                        "op": "replace_inner",
                        "html": f"<div><p>Processado pela Nuvem (Mock). Prompt: {prompt}</p></div>"
                    }]
                }
                
                manifest = {
                    "slots": {"slot-main": ["div", "p", "span"]},
                    "data_roles": [],
                    "actions": []
                }

                # --- APLICANDO O PATCH ENGINE ---
                # Gravamos um arquivo temporário com o HTML base
                import tempfile, os
                temp_fd, temp_path = tempfile.mkstemp(suffix=".html", text=True)
                with os.fdopen(temp_fd, "w", encoding="utf-8") as tmp:
                    tmp.write(base_html)
                
                try:
                    # O motor faz a mágica e garante o rollback
                    novo_sha = apply_patch_transaction(temp_path, patch_payload, manifest)
                    with open(temp_path, "r", encoding="utf-8") as tmp:
                        novo_html = tmp.read()
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                # Salva a nova versão no cérebro local
                if hasattr(cerebro, 'dynamic_tools'):
                    cerebro.dynamic_tools[intent] = {"html": novo_html, "features": ["patch_applied"]}
                    if hasattr(cerebro, '_save_dynamic_tools'):
                        cerebro._save_dynamic_tools() # Ou usar o guardar_memoria
                    else:
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

if re.search(pattern, code):
    code = re.sub(pattern, new_block, code)
    print("[OK] Rota /api/generate_cloud reescrita com o motor de patches.")
else:
    print("[AVISO] Não foi possível encontrar o bloco exato. Verifique o app.py manualmente.")
    sys.exit(1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py integrado.")
except Exception as e:
    print(f"[FALHA CRÍTICA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)