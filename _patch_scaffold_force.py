import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_scaffold_force_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove qualquer tentativa falhada anterior do SCAFFOLD_TEMPLATE
code = re.sub(r'SCAFFOLD_TEMPLATE\s*=\s*"""[\s\S]*?"""', '', code, flags=re.IGNORECASE)

# Define o template de forma limpa
scaffold_def = '''SCAFFOLD_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .app-container { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 12px; }
    .display { background: #0f172a; color: #38bdf8; font-size: 24px; padding: 10px; border-radius: 6px; text-align: right; min-height: 40px; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    button { padding: 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; background: #38bdf8; color: #0f172a; font-size: 16px; }
    button:hover { opacity: 0.8; }
</style>
</head>
<body>
    <div class="app-container">
        {INNER}
    </div>
</body>
</html>"""

'''

# Insere antes da classe principal
if "class LumaCoreHandler" in code:
    code = code.replace("class LumaCoreHandler", scaffold_def + "\nclass LumaCoreHandler")
    print("[OK] SCAFFOLD_TEMPLATE injetado no topo (antes da classe).")
else:
    print("[ERRO] Nao foi possivel localizar 'class LumaCoreHandler' para injetar o template.")
    sys.exit(1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)