import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Se encontrar o if problemático, injeta a definição antes
    if re.match(r'^\s*if\s+mutacoes\s*:', line):
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(f"{indent}mutacoes = []  # Bypass STILB v119\n")
    new_lines.append(line)

code = "".join(new_lines)

# Garante o import do mutador
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("import json", "import json\nfrom intelligence.mutador_stilb_v1 import aplicar_mutacoes", 1)

# Injeção Inline Final (A que funciona)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto|html_evoluido),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(tmp, doraise=True)
    bak = APP + ".bak_v119_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(APP, bak)
    os.replace(tmp, APP)
    print("[OK] app.py blindado com sucesso. O mutacoes morreu.")
except Exception as e:
    if os.path.exists(tmp): os.remove(tmp)
    print(f"[CRITICO] Compilacao falhou: {e}")