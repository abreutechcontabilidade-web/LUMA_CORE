import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_smart_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

old_cache = '''                if intent in cerebro.dynamic_tools:
                    entry = cerebro.dynamic_tools[intent]
                    local_html = entry["html"] if isinstance(entry, dict) and "html" in entry else entry
                    elapsed_local = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache hit! Respondendo em {elapsed_local}ms.")
                    self._send_json({"status": "success", "html": local_html, "fonte": "APRENDIDO_LOCAL", "elapsed_ms": elapsed_local})
                    return'''

new_cache = '''                # BUSCA INTELIGENTE: Tenta a intencao exata, ou tenta achar uma chave parecida
                matched_key = None
                if intent in cerebro.dynamic_tools:
                    matched_key = intent
                else:
                    for k in cerebro.dynamic_tools.keys():
                        if k in prompt.lower() or prompt.lower() in k or k == "jogo_da_velha" and "velha" in prompt.lower():
                            matched_key = k
                            break
                            
                if matched_key:
                    entry = cerebro.dynamic_tools[matched_key]
                    local_html = entry["html"] if isinstance(entry, dict) and "html" in entry else entry
                    elapsed_local = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache hit! Chave '{matched_key}' respondida em {elapsed_local}ms.")
                    self._send_json({"status": "success", "html": local_html, "fonte": "APRENDIDO_LOCAL", "elapsed_ms": elapsed_local})
                    return'''

if old_cache in code:
    code = code.replace(old_cache, new_cache)
    print("[OK] Logica de busca inteligente injetada no cache.")
else:
    print("[AVISO] Bloco de cache antigo nao encontrado. O patch pode ter falhado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)