import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
ONNX = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_bridge.py"

# 1. Reparar o onnx_bridge.py (Prevenção)
with open(ONNX, "w", encoding="utf-8") as f:
    f.write("def inferir_mutacao(*args, **kwargs): return []\n")
    f.write("from intelligence.mutador_stilb_v1 import aplicar_mutacoes\n")

# 2. Ler o app.py
with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 3. APAGAR a linha inteira que contém 'inferir_mutacao'
lines = code.split('\n')
new_lines = []
for line in lines:
    if "inferir_mutacao" in line:
        # Substitui a linha por um comentário seguro
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(f"{indent}pass # inferir_mutacao removido pelo CTO")
    else:
        new_lines.append(line)
code = '\n'.join(new_lines)

# 4. Remover o import do bridge (se existir)
code = re.sub(r'from intelligence\.onnx_bridge import.*\n', '', code)

# 5. Garantir o import do mutador
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("import json", "import json\nfrom intelligence.mutador_stilb_v1 import aplicar_mutacoes", 1)

# 6. Injeção Inline (a que funciona)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 7. Limpar vestígios de patches anteriores
code = re.sub(r'^[ \t]*html_evoluido = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*html_auto = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*if _muts.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*\w+ = _stilb_mutar_seguro\(.*\n', '', code, flags=re.M)

# 8. Gravar e Compilar
tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(tmp, doraise=True)
    bak = APP + ".bak_v115_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(APP, bak)
    os.replace(tmp, APP)
    print("[OK] app.py limpo e injetado com sucesso.")
except Exception as e:
    if os.path.exists(tmp): os.remove(tmp)
    print(f"[CRITICO] Compilacao falhou: {e}")