import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_pos_app_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Atualiza o delta_prompt para incluir a posicao
old_prompt = '''                    delta_prompt = (
                        f"Voce e um Engenheiro de Software Sênior.\\n"
                        f"CODIGO BASE:\\n{local_base}\\n\\n"
                        f"TAREFA: Adicione APENAS as seguintes funcionalidades: {', '.join(features_em_falta)}.\\n"
                        "REGRAS:\\n"
                        "1. NAO altere o que ja existe.\\n"
                        "2. Adicione o HTML da nova funcionalidade dentro do container principal.\\n"
                        "3. Adicione o JavaScript necessario.\\n"
                        "4. Retorne o codigo HTML COMPLETO e MODIFICADO.\\n"
                        "5. Nao inclua explicacoes ou markdown."
                    )'''

new_prompt = '''                    posicao = ""
                    if "topo" in features_em_falta:
                        posicao = " na parte SUPERIOR (topo) do app"
                    elif "baixo" in features_em_falta:
                        posicao = " na parte INFERIOR (fundo) do app"

                    delta_prompt = (
                        f"Voce e um Engenheiro de Software Sênior.\\n"
                        f"CODIGO BASE:\\n{local_base}\\n\\n"
                        f"TAREFA: Adicione APENAS as seguintes funcionalidades: {', '.join(features_em_falta)}{posicao}.\\n"
                        "REGRAS:\\n"
                        "1. NAO altere o que ja existe.\\n"
                        "2. Adicione o HTML da nova funcionalidade dentro do container principal.\\n"
                        "3. Adicione o JavaScript necessario.\\n"
                        "4. Retorne o codigo HTML COMPLETO e MODIFICADO.\\n"
                        "5. Nao inclua explicacoes ou markdown."
                    )'''

if old_prompt in code:
    code = code.replace(old_prompt, new_prompt)
    print("[OK] Delta prompt atualizado com posicao.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    code = re.sub(r'                    delta_prompt = \([\s\S]*?5\. Nao inclua explicacoes ou markdown\."\n                    \)', new_prompt, code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)