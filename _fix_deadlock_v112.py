import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. Mata o processo do servidor para parar o loop
os.system("taskkill /F /IM python.exe /T >nul 2>&1")

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Remove QUALQUER vestígio do patch da Bancada
code = re.sub(r'^[ \t]*\w+ = _stilb_mutar_seguro\(.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*if _muts.*\n', '', code, flags=re.M)

# 3. Injeção Inline Segura (A que sabemos que funciona)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto|html_evoluido),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 4. Garante que o import é do mutador e não do bridge
code = re.sub(r'from intelligence\.onnx_bridge import.*\n', '', code)
code = re.sub(r'from intelligence\.mutador_stilb_v1 import.*\n', '', code)
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("import json", "import json\nfrom intelligence.mutador_stilb_v1 import aplicar_mutacoes", 1)

# 5. Remove as variáveis fantasma
code = re.sub(r'^[ \t]*html_evoluido = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*html_auto = .*\n', '', code, flags=re.M)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if os.path.exists(tmp):
    try:
        py_compile.compile(tmp, doraise=True)
        bak = APP + ".bak_v112_" + time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(APP, bak)
        os.replace(tmp, APP)
        print("[OK] app.py limpo e injetado inline com sucesso.")
    except Exception as e:
        os.remove(tmp)
        print(f"[CRITICO] Compilacao falhou: {e}")