import os, shutil, time, py_compile, re, glob

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. Restaurar do último backup válido
backups = glob.glob(path + ".bak_*")
if backups:
    latest_bak = max(backups, key=os.path.getctime)
    shutil.copy2(latest_bak, path)
    print(f"[OK] app.py restaurado do backup: {latest_bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Remover injeções antigas corrompidas
code = re.sub(r'\s*html_mutado, _muts = aplicar_mutacoes\(.*?\)\n', '\n', code)

# 3. Injeção Segura com Regex (Captura e preserva a indentação)
def inject_mutator(match):
    indent = match.group('indent')
    html_var = match.group('html_var')
    # Injeta a mutação ANTES do _send_json, com os mesmos espaços
    return f"{indent}{html_var}, _muts = aplicar_mutacoes({html_var}, prompt)\n" + match.group(0)

# Procura qualquer chamada _send_json que contenha a variável 'html'
pattern = r'(?P<indent>[ \t]+)self\._send_json\(\{"status": "success", "html": (?P<html_var>\w+),'
code = re.sub(pattern, inject_mutator, code)

# 4. Alinhamento de Namespace (G-144)
code = code.replace('intent_web = prompt.lower().replace(" ", "_")[:20]', 'intent_web = chave_limpa.replace(" ", "_")')

# 5. Garantir o import
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

# 6. Validar a sintaxe (se falhar, não envia)
py_compile.compile(path, doraise=True)
print("[OK] app.py corrigido, namespace alinhado e syntax check PASSOU.")