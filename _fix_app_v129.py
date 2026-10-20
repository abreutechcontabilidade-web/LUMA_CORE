import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# Força a chamada ao learner a usar uma string limpa
code = re.sub(r'aprender_do_github\([^)]*\)', 'aprender_do_github("snake game")', code)

# Garante que o mutador está a ser usado no ponto de entrega
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto|html_evoluido),', r'"html": _stilb_mutar_seguro(\1, prompt),', code)

# Garante o import correto
IMPORT_LINE = "from intelligence.mutador_stilb_v1 import _stilb_mutar_seguro"
if IMPORT_LINE not in code:
    code = code.replace("import json", "import json\n" + IMPORT_LINE, 1)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(tmp, doraise=True)
    bak = APP + ".bak_v129_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(APP, bak)
    os.replace(tmp, APP)
    print("[OK] app.py forçado a 'snake game' e _stilb_mutar_seguro.")
except Exception as e:
    if os.path.exists(tmp): os.remove(tmp)
    print(f"[CRITICO] Compilacao falhou: {e}")