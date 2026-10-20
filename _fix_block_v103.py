import os, re, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v103_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Encontrar o bloco do WEB LEARNER e forçar a indentação correta (12 espaços)
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'print("[WEB LEARNER] Enxame falhou.' in line or \
       'chave_limpa = extrair_chave(prompt)' in line or \
       'print(f"[WEB LEARNER] A procurar no GitHub por' in line:
        lines[i] = '            ' + line.lstrip() # Força 12 espaços (padrão de blocos try/if no Python)

code = '\n'.join(lines)

# 2. Remover QUALQUER injeção antiga que tenha sobrado
code = re.sub(r'\n\s*html_mutado, _muts = aplicar_mutacoes\(.*?\)', '', code)
code = re.sub(r'\n\s*html_atual, _muts = aplicar_mutacoes\(.*?\)', '', code)

# 3. Injeção Inline Segura (Sem novas linhas, zero risco de indentação)
# Substitui "html": html_atual, por "html": aplicar_mutacoes(html_atual, prompt)[0],
code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

# 4. Garantir o import no topo (remover antigos e adicionar limpo)
code = re.sub(r'from intelligence\.mutador_stilb_v1 import.*\n', '', code)
code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

# 5. Gravar e Validar
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] app.py reescrito, mutacao inline e syntax check PASSOU.")