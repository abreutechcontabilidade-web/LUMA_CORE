import os, shutil, time, py_compile, re, glob

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. Restaurar do último backup válido (antes do crash)
backups = glob.glob(path + ".bak_v94_*")
if backups:
    latest_bak = max(backups, key=os.path.getctime)
    shutil.copy2(latest_bak, path)
    print(f"[OK] app.py restaurado do backup: {latest_bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Limpar injeções antigas que causaram o erro
code = re.sub(r'\s*html_mutado, _muts = aplicar_mutacoes\(.*?\)\n', '\n', code)

# 3. Injeção Segura (Preserva a indentação exata)
# Procura a linha do _send_json e adiciona o mutador na linha anterior com os mesmos espaços
pattern = r'(?P<indent>\s+)self\._send_json\(\{"status": "success", "html": (?P<var>\w+),'

def replacer(match):
    indent = match.group('indent')
    var = match.group('var')
    # Injeta a mutação usando a mesma indentação do _send_json
    new_code = f"{indent}{var}, _muts = aplicar_mutacoes({var}, prompt)\n"
    return new_code + match.group(0)

if "aplicar_mutacoes" not in code:
    code = re.sub(pattern, replacer, code)
    print("[OK] Mutador injetado cirurgicamente.")

# 4. Garantir o import no topo
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

# 5. Validar a sintaxe (se falhar, não envia)
py_compile.compile(path, doraise=True)
print("[OK] app.py corrigido e validado. O IndentationError morreu.")