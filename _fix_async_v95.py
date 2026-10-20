import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v95_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Move a chamada do background para DEPOIS do envio da resposta
old_block = '''                    # Dispara background learning
                aprender_em_segundo_plano(prompt, intent_onnx, anel, DB_PATH)'''

# A indentação pode variar, então vamos ser flexíveis
if old_block not in code:
    # Tentar com espaços diferentes
    old_block = '''                aprender_em_segundo_plano(prompt, intent_onnx, anel, DB_PATH)'''

new_block = '''                # Background learning movido para o final do bloco'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("[OK] Background learning removido do caminho crítico.")
else:
    print("[AVISO] Nao encontrei a linha do background. Tentando regex...")
    import re
    code = re.sub(r'\n\s*aprender_em_segundo_plano\(prompt, intent_onnx, anel, DB_PATH\)', '', code)

# Agora injeta a chamada no final do bloco de cache (antes do return)
old_return = '''                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Evolucao aplicada via ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_evoluido, "fonte": "ONNX_MUTACAO_LOCAL", "elapsed_ms": elapsed})
                    return'''

new_return = '''                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Evolucao aplicada via ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_evoluido, "fonte": "ONNX_MUTACAO_LOCAL", "elapsed_ms": elapsed})
                    
                    # Inicia o background APOS enviar a resposta
                    aprender_em_segundo_plano(prompt, intent_onnx, anel, DB_PATH)
                    return'''

if old_return in code:
    code = code.replace(old_return, new_return)
    print("[OK] Background movido para depois do envio da resposta (Nao-bloqueante).")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")