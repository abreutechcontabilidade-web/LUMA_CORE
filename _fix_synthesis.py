import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_synth_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui a logica de cache antiga pela chamada ao Motor de Sintese
old_cache = '''                if matched_key:
                    entry = cerebro.dynamic_tools[matched_key]
                    local_html = entry["html"] if isinstance(entry, dict) and "html" in entry else entry
                    elapsed_local = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache hit! Chave '{matched_key}' respondida em {elapsed_local}ms.")
                    self._send_json({"status": "success", "html": local_html, "fonte": "APRENDIDO_LOCAL", "elapsed_ms": elapsed_local})
                    return'''

new_cache = '''                if matched_key:
                    from intelligence.local_synthesis import processar_sintese
                    local_html, status_synth = processar_sintese(prompt)
                    if local_html:
                        elapsed_local = round((time.perf_counter() - start_time) * 1000, 2)
                        print(f"[LOCAL] Motor de Sintese: '{status_synth}' em {elapsed_local}ms.")
                        self._send_json({"status": "success", "html": local_html, "fonte": status_synth, "elapsed_ms": elapsed_local})
                        return'''
                        
if old_cache in code:
    code = code.replace(old_cache, new_cache)
    print("[OK] Motor de Sintese (Miolo Vivo) injetado no app.py.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)
    
py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")