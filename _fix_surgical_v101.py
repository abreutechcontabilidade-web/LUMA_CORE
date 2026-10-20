import os, re, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v101_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remove injeções antigas corrompidas
code = re.sub(r'\n\s*html_mutado, _muts = aplicar_mutacoes\(.*?\)', '', code)

# 2. Corrige o IndentationError da linha 188 (chave_limpa)
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'chave_limpa = extrair_chave(prompt)' in line:
        if i + 1 < len(lines):
            next_line = lines[i+1]
            next_indent = len(next_line) - len(next_line.lstrip())
            lines[i] = ' ' * next_indent + 'chave_limpa = extrair_chave(prompt)'
        break
code = '\n'.join(lines)

# 3. Injeta o Mutador antes de QUALQUER _send_json de sucesso
out_lines = []
for line in code.split('\n'):
    if 'self._send_json({"status": "success", "html":' in line:
        match = re.search(r'"html":\s*(\w+)', line)
        if match:
            var_name = match.group(1)
            indent = line[:len(line) - len(line.lstrip())]
            out_lines.append(f"{indent}{var_name}, _muts = aplicar_mutacoes({var_name}, prompt)")
    out_lines.append(line)
code = '\n'.join(out_lines)

# 4. Garante o import no topo
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

# 5. Validação final
py_compile.compile(path, doraise=True)
print("[OK] app.py corrigido e validado. O IndentationError morreu.")