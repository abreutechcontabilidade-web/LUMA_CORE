import os, re, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v102_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Reparar o IndentationError (Alinha com a linha ACIMA)
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'chave_limpa = extrair_chave(prompt)' in line:
        if i - 1 >= 0:
            prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
            lines[i] = ' ' * prev_indent + 'chave_limpa = extrair_chave(prompt)'
        break
code = '\n'.join(lines)

# 2. Remover QUALQUER injeção antiga que tenha sobrado (linhas inteiras)
code = re.sub(r'\n\s*html_mutado, _muts = aplicar_mutacoes\(.*?\)', '', code)
code = re.sub(r'\n\s*html_atual, _muts = aplicar_mutacoes\(.*?\)', '', code)
code = re.sub(r'\n\s*codigo_web, _muts = aplicar_mutacoes\(.*?\)', '', code)
code = re.sub(r'\n\s*fallback_html, _muts = aplicar_mutacoes\(.*?\)', '', code)

# 3. Injeção Inline (Sem adicionar novas linhas, zero risco de indentação)
# Substitui "html": html_atual, por "html": aplicar_mutacoes(html_atual, prompt)[0],
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 4. Garantir o import no topo
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

# 5. Gravar e Validar
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] app.py curado, mutacao inline e syntax check PASSOU.")