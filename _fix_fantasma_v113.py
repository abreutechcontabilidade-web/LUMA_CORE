import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. Mata o processo do servidor
os.system("taskkill /F /IM python.exe /T >nul 2>&1")

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Remove a chamada inferir_mutacao (substitui por lista vazia)
code = re.sub(r'mutacoes_auto = inferir_mutacao\(.*?\)', 'mutacoes_auto = []', code)
code = re.sub(r'mutacoes = inferir_mutacao\(.*?\)', 'mutacoes = []', code)

# 3. Remove o import do bridge que falhou
code = re.sub(r'from intelligence\.onnx_bridge import.*\n', '', code)

# 4. Garante o import do mutador
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("import json", "import json\nfrom intelligence.mutador_stilb_v1 import aplicar_mutacoes", 1)

# 5. Injeção Inline (a que funciona)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto|html_evoluido),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 6. Remove variáveis fantasmas que sobraram
code = re.sub(r'^[ \t]*html_evoluido = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*html_auto = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*if _muts.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*\w+ = _stilb_mutar_seguro\(.*\n', '', code, flags=re.M)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if os.path.exists(tmp):
    try:
        py_compile.compile(tmp, doraise=True)
        bak = APP + ".bak_v113_" + time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(APP, bak)
        os.replace(tmp, APP)
        print("[OK] app.py limpo e injetado com sucesso.")
    except Exception as e:
        os.remove(tmp)
        print(f"[CRITICO] Compilacao falhou: {e}")