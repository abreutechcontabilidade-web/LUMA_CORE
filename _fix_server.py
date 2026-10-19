import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_server_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Corrige o nome da classe
if "ThreadingServer" in code:
    code = code.replace("ThreadingServer", "ThreadingHTTPServer")
    print("[OK] 'ThreadingServer' substituido por 'ThreadingHTTPServer'.")

# 2. Garante o import da classe
if "from http.server import ThreadingHTTPServer" not in code and "ThreadingHTTPServer" in code:
    code = "from http.server import ThreadingHTTPServer\n" + code
    print("[OK] Import 'ThreadingHTTPServer' adicionado no topo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Pronto para arrancar de vez.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)