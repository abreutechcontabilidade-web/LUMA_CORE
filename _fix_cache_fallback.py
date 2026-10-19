import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_cache_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Onde inserir o cache? Logo após ler o prompt
alvo = '''            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return
'''

adicao = alvo + '''
            # --- VERIFICACAO DE MEMORIA LOCAL (Ouro) ---
            try:
                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_html, fonte = res_base
                    if fonte and isinstance(fonte, str) and fonte.startswith("APRENDIDO_"):
                        elapsed_local = round((time.perf_counter() - start_time) * 1000, 2)
                        print(f"[LOCAL] Cache hit para '{prompt[:20]}...' em {elapsed_local}ms.")
                        self._send_json({"status": "success", "html": local_html, "fonte": fonte, "elapsed_ms": elapsed_local})
                        return
            except Exception as e:
                print(f"[AVISO] Erro ao buscar no cache local: {e}")
            # --- FIM DA VERIFICACAO LOCAL ---
'''

if alvo in code:
    code = code.replace(alvo, adicao)
    print("[OK] Verificacao de memoria local injetada antes da Nuvem.")
else:
    print("[AVISO] Trecho original nao encontrado. Tentando substituicao parcial...")
    if "prompt = req_data.get" in code:
        # Fallback caso o try/except esteja diferente
        code = code.replace("prompt = req_data.get(\"prompt\", \"\")", "prompt = req_data.get(\"prompt\", \"\")\n            res_base = cerebro.processar(prompt)\n            if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:\n                local_html, fonte = res_base\n                if fonte and fonte.startswith(\"APRENDIDO_\"):\n                    self._send_json({\"status\": \"success\", \"html\": local_html, \"fonte\": fonte, \"elapsed_ms\": round((time.perf_counter() - start_time) * 1000, 2)})\n                    return")
        print("[OK] Injetado via fallback.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. O sistema agora checa o Local primeiro.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)