import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_mutator_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Substitui o prompt no generate_cloud para ser um Mutador
old_prompt = '''                # 1. Obtem o codigo base (com a melhor correspondencia)
                local_base, fonte = cerebro.processar(prompt)
                if not local_base:
                    local_base = SCAFFOLD_TEMPLATE.replace("{INNER}", "")

                # 2. O Prompt pede para ADICIONAR a feature nova ao base existente
                sys_prompt = (
                    f"Voce e um Engenheiro de Software Sênior.\\n"
                    f"TAREFA: Adicione a nova funcionalidade pedida ao codigo base existente.\\n"
                    f"PEDIDO NOVO: {prompt}\\n\\n"
                    "REGRAS CRITICAS:\\n"
                    "1. NAO devolva o codigo base inteiro sem modificacoes.\\n"
                    "2. PRESERVE tudo o que ja existe (placar, historico, etc) e ADICIONE o novo (cronometro).\\n"
                    "3. NAO RETORNE a div <div class='app-container'>. Retorne APENAS o conteudo interno.\\n"
                    "4. Retorne APENAS o codigo HTML/JS, sem explicacoes ou markdown.\\n\\n"
                    f"CODIGO BASE (mantenha e expanda):\\n{local_base}"
                )'''

new_prompt = '''                # 1. Obtem o codigo base (com a melhor correspondencia)
                local_base, fonte = cerebro.processar(prompt)
                if not local_base:
                    local_base = SCAFFOLD_TEMPLATE.replace("{INNER}", "")

                # 2. O Prompt é um MUTADOR (altera o que já existe)
                sys_prompt = (
                    f"Voce e um Engenheiro de Software Sênior.\\n"
                    f"TAREFA: Modifique o codigo base existente de acordo com o pedido do utilizador.\\n"
                    f"PEDIDO DO UTILIZADOR: {prompt}\\n\\n"
                    "REGRAS CRITICAS:\\n"
                    "1. MANTENHA ABSOLUTAMENTE TUDO o que ja funciona (placar, historico, logica do jogo).\\n"
                    "2. APLIQUE APENAS a mudanca pedida (ex: se pediu para mover o cronometro para baixo, mova o HTML dele para o fundo).\\n"
                    "3. NAO RETORNE a div <div class='app-container'>. Retorne APENAS o conteudo interno.\\n"
                    "4. Retorne APENAS o codigo HTML/JS completo e modificado, sem explicacoes.\\n\\n"
                    f"CODIGO BASE (mantenha e altere):\\n{local_base}"
                )'''

if old_prompt in code:
    code = code.replace(old_prompt, new_prompt)
    print("[OK] Prompt do generate_cloud atualizado para MUTADOR.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    pattern = r'                # 1\. Obtem o codigo base[\s\S]*?f"CODIGO BASE \(mantenha e expanda\):\\n\{local_base\}"\n                \)'
    code = re.sub(pattern, new_prompt, code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado com Mutador.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)