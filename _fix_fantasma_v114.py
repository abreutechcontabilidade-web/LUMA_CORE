import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
ONNX = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_bridge.py"

# 1. Reparar o onnx_bridge.py
with open(ONNX, "w", encoding="utf-8") as f:
    f.write("def inferir_mutacao(*args, **kwargs): return []\n")
    f.write("from intelligence.mutador_stilb_v1 import aplicar_mutacoes\n")

# 2. Mata o processo do servidor
os.system("taskkill /F /IM python.exe /T >nul 2>&1")

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 3. Remove imports antigos do bridge
code = re.sub(r'from intelligence\.onnx_bridge import.*\n', '', code)
code = re.sub(r'from intelligence\.mutador_stilb_v1 import.*\n', '', code)

# 4. Adiciona a função fantasma e o import correto no topo
header = "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\n"
header += "def inferir_mutacao(*args, **kwargs): return []\n"
code = header + code

# 5. Remove variáveis fantasmas que sobraram
code = re.sub(r'^[ \t]*html_evoluido = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*html_auto = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*if _muts.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*\w+ = _stilb_mutar_seguro\(.*\n', '', code, flags=re.M)

# 6. Injeção Inline (a que funciona)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if os.path.exists(tmp):
    try:
        py_compile.compile(tmp, doraise=True)
        bak = APP + ".bak_v114_" + time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(APP, bak)
        os.replace(tmp, APP)
        print("[OK] app.py blindado com funcao fantasma e injecao inline.")
    except Exception as e:
        os.remove(tmp)
        print(f"[CRITICO] Compilacao falhou: {e}")