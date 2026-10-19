import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_boot_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

if "if __name__ == '__main__':" not in code and 'if __name__ == "__main__":' not in code:
    print("[AVISO] Bloco __main__ NAO encontrado. Injetando novamente...")
    main_block = '''
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PORT = 8080
    socketserver.TCPServer.allow_reuse_address = True
    print(f"[LUMA_CORE] Servidor v63.0 ativo em http://127.0.0.1:{PORT}")
    try:
        with ThreadingHTTPServer(("127.0.0.1", PORT), LumaCoreHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
'''
    code += main_block
    
    if "from http.server import ThreadingHTTPServer" not in code:
        code = "from http.server import ThreadingHTTPServer\n" + code
    if "import socketserver" not in code:
        code = "import socketserver\n" + code

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("[OK] Bloco __main__ injetado com sucesso.")
else:
    print("[OK] Bloco __main__ ja existe. Nada a fazer.")

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Pronto para ligar.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)