import sys

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

cors_headers = """        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
"""

# 1. Injeta CORS no _send_json existente (preservando rotas)
if "Access-Control-Allow-Origin" not in code:
    alvo = "        self.send_response(200)\n        self.send_header('Content-type', 'application/json; charset=utf-8')"
    if alvo in code:
        code = code.replace(alvo, alvo + "\n" + cors_headers)
    else:
        alvo2 = "        self.send_response(200)\n        self.send_header('Content-type', 'application/json')"
        if alvo2 in code:
            code = code.replace(alvo2, alvo2 + "\n" + cors_headers)
        else:
            code = code.replace("        self.send_response(200)\n        self.end_headers()", "        self.send_response(200)\n" + cors_headers + "        self.end_headers()")

# 2. Injeta do_OPTIONS (preflight CORS)
if "def do_OPTIONS" not in code:
    options_method = """    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

"""
    code = code.replace("    def do_POST(self):", options_method + "    def do_POST(self):")

with open(APP, "w", encoding="utf-8") as f:
    f.write(code)
print("[OK] CORS injetado com sucesso no motor.")
