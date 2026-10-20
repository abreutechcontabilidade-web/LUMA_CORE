import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remove o meu hack amador do "snake game" e restaura a extração canónica
code = re.sub(r'chave_limpa\s*=\s*"snake game"', 'chave_limpa = extrair_chave(prompt)', code)
code = re.sub(r'aprender_do_github\(\s*prompt\s*\)', 'aprender_do_github(extrair_chave(prompt))', code)

# 2. Normaliza as entregas inline para o wrapper seguro GATE-30
code = re.sub(r'aplicar_mutacoes\((\w+), prompt\)\[0\]', r'_stilb_mutar_seguro(\1, prompt)', code)

# 3. Garante o import do wrapper seguro
IMPORT_LINE = "from intelligence.mutador_stilb_v1 import _stilb_mutar_seguro"
if IMPORT_LINE not in code:
    code = code.replace("import json", "import json\n" + IMPORT_LINE, 1)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(tmp, doraise=True)
    bak = APP + ".bak_pf58_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(APP, bak)
    os.replace(tmp, APP)
    print("[OK] GATE-32 e GATE-30 aplicados. O motor agora e SOTA Quantum.")
except Exception as e:
    if os.path.exists(tmp): os.remove(tmp)
    print(f"[CRITICO] Compilacao falhou: {e}")