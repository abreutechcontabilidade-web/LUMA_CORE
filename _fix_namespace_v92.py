import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v92_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. G-144: Alinhar a chave de escrita (Web Learner) com a chave de leitura (ONNX)
old_write = '''            if codigo_web:
                intent_web = prompt.lower().replace(" ", "_")[:20]'''
new_write = '''            if codigo_web:
                # G-144 FIX: Usar a mesma chave que o ONNX vai procurar
                intent_web = chave_limpa.replace(" ", "_")'''
code = code.replace(old_write, new_write)

# 2. G-148: Devolver a proveniencia na resposta da API
old_response = '''                self._send_json({"status": "success", "html": codigo_web, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed})'''
new_response = '''                self._send_json({"status": "success", "html": codigo_web, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed, "proveniencia": proveniencia})'''
code = code.replace(old_response, new_response)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] app.py atualizado. Namespace unificado e proveniencia no contrato.")