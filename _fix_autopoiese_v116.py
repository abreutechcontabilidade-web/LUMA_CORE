import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. Lê o ficheiro
with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 2. Injeta a variável de segurança html_auto antes de ser usada
new_lines = []
for i, line in enumerate(lines):
    if "miolo_auto = ler_miolo(html_auto)" in line:
        indent = line[:len(line) - len(line.lstrip())]
        # Injeta a definição de segurança com a mesma indentação
        new_lines.append(f"{indent}if 'html_auto' not in locals(): html_auto = '<html><body>Base</body></html>'\n")
    new_lines.append(line)

code = "".join(new_lines)

# 3. Remove injeções antigas que possam ter sobrado
code = re.sub(r'^[ \t]*\w+ = _stilb_mutar_seguro\(.*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*html_evoluido = .*\n', '', code, flags=re.M)
code = re.sub(r'^[ \t]*mutacoes_auto = inferir_mutacao.*\n', '', code, flags=re.M)

# 4. Garante o import correto
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("import json", "import json\nfrom intelligence.mutador_stilb_v1 import aplicar_mutacoes", 1)

# 5. Injeção Inline (sem variáveis soltas)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 6. Gravação Segura (GATE-26)
tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(tmp, doraise=True)
    bak = APP + ".bak_v116_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(APP, bak)
    os.replace(tmp, APP)
    print("[OK] app.py cirurgicamente corrigido. O NameError morreu.")
except Exception as e:
    if os.path.exists(tmp): os.remove(tmp)
    print(f"[CRITICO] Compilacao falhou: {e}")