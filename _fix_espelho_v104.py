import os, shutil, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v104"
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Encontrar a indentação exata da linha do "Enxame falhou"
target_indent = ""
for line in lines:
    if 'Enxame falhou' in line:
        target_indent = line[:len(line) - len(line.lstrip())]
        break

if not target_indent:
    target_indent = "            " # Fallback de segurança (12 espaços)

# 2. Alinhar TODAS as linhas do bloco com o mesmo número de espaços
new_lines = []
for line in lines:
    stripped = line.lstrip()
    if stripped.startswith('chave_limpa = extrair_chave(prompt)'):
        new_lines.append(target_indent + stripped)
    elif stripped.startswith('print(f"[WEB LEARNER] A procurar no GitHub'):
        new_lines.append(target_indent + stripped)
    elif stripped.startswith('codigo_web, proveniencia = aprender_do_github'):
        new_lines.append(target_indent + stripped)
    elif 'html_mutado, _muts = aplicar_mutacoes' in line or 'html_atual, _muts = aplicar_mutacoes' in line:
        continue # Remove lixo antigo
    else:
        new_lines.append(line)

code = ''.join(new_lines)

# 3. Injeção Inline Segura (Mutação dentro do JSON)
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 4. Garantir o import
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] app.py corrigido com espelho de indentacao. Syntax check PASSOU.")