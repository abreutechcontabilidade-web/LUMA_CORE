import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_json_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui a definição da função inteira
padrao = r"def _send_json\(self,.*?\):[\s\S]*?(?=\n    def )"
nova_funcao = '''def _send_json(self, data, status=200):
        try:
            import json
            response = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar JSON: {e}")'''

if re.search(padrao, code):
    code = re.sub(padrao, nova_funcao, code)
    print("[OK] Funcao _send_json reescrita para aceitar status code.")
else:
    if "def _send_json(self, data):" in code:
        code = code.replace("def _send_json(self, data):", nova_funcao)
        print("[OK] Assinatura de _send_json substituida.")
    else:
        print("[AVISO] Nao achei a funcao _send_json. Verifique manualmente.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Pronto para o teste final.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)