import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v95_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remove qualquer injeção antiga (para evitar duplicados)
code = re.sub(r"\n\s*# --- NIVEL 0\.5 STILB.*?\n\s*print\(f\"\[AVISO\] Erro no mutador STILB.*?\)", "", code, flags=re.S)
code = re.sub(r"\n\s*# --- STILB MUTATOR NO CACHE.*?\n\s*print\(f\"\[AVISO\] Erro no mutador STILB.*?\)", "", code, flags=re.S)

# 2. Injeta o STILB no Nivel 1 (Cache ONNX)
pattern = r"(if intent_onnx and score > 0\.4:[\s\S]*?html_atual = entry\.get\(\"html\", \"\"\) if isinstance\(entry, dict\) else entry)"
match = re.search(pattern, code)
if match:
    block = match.group(1)
    indent = re.search(r"\n(\s+)html_atual", block).group(1)
    inject = (
        f"\n{indent}# --- NIVEL 0.5 STILB (CACHE) ---"
        f"\n{indent}try:\n"
        f"{indent}    from intelligence.mutador_local_v1 import aplicar_mutacoes\n"
        f"{indent}    html_atual, _muts = aplicar_mutacoes(html_atual, prompt)\n"
        f"{indent}    if _muts:\n"
        f"{indent}        print(f\"[NIVEL 1 STILB] Mutacoes aplicadas no cache: {{_muts}}\")\n"
        f"{indent}except Exception as e:\n"
        f"{indent}    print(f\"[AVISO] Erro STILB Cache: {{e}}\")"
    )
    code = code.replace(block, block + inject)
    print("[OK] Injetado no Cache (Nivel 1).")
else:
    print("[ERRO] Cache block nao encontrado.")

# 3. Injeta o STILB no Nivel 3 (Web Learner)
pattern_web = r"(if codigo_web:[\s\S]*?intent_web = chave_limpa\.replace\(\" \", \"_\"\))"
match_web = re.search(pattern_web, code)
if match_web:
    block = match_web.group(1)
    indent = re.search(r"\n(\s+)intent_web", block).group(1)
    inject = (
        f"\n{indent}# --- NIVEL 0.5 STILB (WEB) ---"
        f"\n{indent}try:\n"
        f"{indent}    from intelligence.mutador_local_v1 import aplicar_mutacoes\n"
        f"{indent}    codigo_web, _muts = aplicar_mutacoes(codigo_web, prompt)\n"
        f"{indent}    if _muts:\n"
        f"{indent}        print(f\"[NIVEL 1 STILB] Mutacoes Web: {{_muts}}\")\n"
        f"{indent}except Exception as e:\n"
        f"{indent}    print(f\"[AVISO] Erro STILB Web: {{e}}\")"
    )
    code = code.replace(block, block + inject)
    print("[OK] Injetado no Web Learner (Nivel 3).")
else:
    print("[ERRO] Web block nao encontrado.")

# 4. Desativa a injeção do fundo vermelho antigo (para o STILB brilhar)
code = code.replace(
    "mutacoes = inferir_mutacao(prompt, miolo)",
    "mutacoes = [] # Desativado para nao sobrepor o STILB"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")