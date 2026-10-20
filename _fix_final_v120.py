import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v120_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove qualquer injeção antiga
code = re.sub(r"\n\s*# --- NIVEL 0\.5 STILB.*?\n\s*print\(f\"\[AVISO\] Erro STILB.*?\)", "", code, flags=re.S)

# Injeta o mutador no Nível 1 (Cache)
target = r"(html_atual = entry\.get\(\"html\", \"\"\) if isinstance\(entry, dict\) else entry)"
match = re.search(target, code)
if match:
    linha_inteira = code[code.rfind("\n", 0, match.start())+1 : code.find("\n", match.end())]
    indent = re.match(r"(\s+)", linha_inteira).group(1)
    
    inject = (
        f"\n{indent}# --- STILB MUTATOR v120.0 (CTO DEFINITIVO) ---"
        f"\n{indent}try:\n"
        f"{indent}    from intelligence.mutador_local_v1 import aplicar_mutacoes\n"
        f"{indent}    html_atual, _muts = aplicar_mutacoes(html_atual, prompt)\n"
        f"{indent}    if _muts:\n"
        f"{indent}        print(f\"[STILB] Mutacao aplicada no cache: {{_muts}}\")\n"
        f"{indent}        if isinstance(entry, dict):\n"
        f"{indent}            entry['html'] = html_atual\n"
        f"{indent}            with open(DB_PATH, 'w', encoding='utf-8') as f:\n"
        f"{indent}                json.dump(memoria, f, ensure_ascii=False, indent=2)\n"
        f"{indent}except Exception as e:\n"
        f"{indent}    print(f\"[AVISO] Erro STILB Cache: {{e}}\")"
    )
    code = code.replace(match.group(0), match.group(0) + inject)
    print("[OK] Mutador injetado no Cache (Nivel 1).")
else:
    print("[ERRO] Alvo do cache nao encontrado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")