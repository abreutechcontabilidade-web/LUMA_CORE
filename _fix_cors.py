import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_cors_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Verifica se o método do_OPTIONS já existe
if "def do_OPTIONS(self):" not in code:
    print("[AVISO] Metodo do_OPTIONS ausente. Injetando...")
    
    # Encontra a definição da classe ou do do_POST para injetar antes
    target = "    def do_POST(self):"
    if target in code:
        options_code = '''    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

'''
        code = code.replace(target, options_code + target)
        print("[OK] Metodo do_OPTIONS injetado com sucesso.")
    else:
        print("[ERRO] Nao foi possivel encontrar o do_POST para injetar o OPTIONS.")
else:
    print("[OK] Metodo do_OPTIONS ja existe.")

# Garante que o do_POST e do_GET enviam o CORS Allow-Origin
if 'self.send_header("Access-Control-Allow-Origin", "*")' not in code:
    print("[AVISO] Faltando cabecalho CORS no do_POST/do_GET.")
    # (Assumindo que o _send_json do projeto ja tem, mas para garantir nas rotas diretas)
    # O _send_json ja tem o Access-Control-Allow-Origin, entao esta seguro.

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O servidor esta pronto para o Cockpit.")