import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_main_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Arranca fora o bloco __main__ podre
clean_lines = []
for line in lines:
    if 'if __name__ == "__main__":' in line:
        break
    clean_lines.append(line)

# Adiciona os imports vitais no topo se não existirem
header = []
if not any("from http.server import ThreadingHTTPServer" in l for l in clean_lines):
    header.append("from http.server import ThreadingHTTPServer\n")
if not any("import socketserver" in l for l in clean_lines):
    header.append("import socketserver\n")

final_code = "".join(header + clean_lines) + '''
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PORT = 8080
    socketserver.TCPServer.allow_reuse_address = True
    print(f"[LUMA_CORE] Servidor v61.0 ativo em http://127.0.0.1:{PORT}")
    try:
        with ThreadingHTTPServer(("127.0.0.1", PORT), LumaCoreHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(final_code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] Bloco __main__ reescrito com ThreadingHTTPServer. py_compile PASSOU.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)