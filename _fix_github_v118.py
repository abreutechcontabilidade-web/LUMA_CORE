import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Força a chave de busca a ser "snake game" (ou "jogo da cobra")
code = re.sub(r'chave_limpa\s*=\s*extrair_chave\(prompt\)', 'chave_limpa = "snake game"', code)

# 2. Garante que o import do mutador está lá
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("import json", "import json\nfrom intelligence.mutador_stilb_v1 import aplicar_mutacoes", 1)

# 3. Garante que a injeção inline está aplicada
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html|html_auto|html_evoluido),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 4. Remove o `if mutacoes_auto:` para segurança
code = re.sub(r'^[ \t]*if mutacoes_auto:.*\n', '', code, flags=re.M)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(tmp, doraise=True)
    bak = APP + ".bak_v118_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(APP, bak)
    os.replace(tmp, APP)
    print("[OK] app.py focado no GitHub. A busca agora e 'snake game'.")
except Exception as e:
    if os.path.exists(tmp): os.remove(tmp)
    print(f"[CRITICO] Compilacao falhou: {e}")