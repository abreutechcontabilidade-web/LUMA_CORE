import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_frame_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Atualizar o prompt e a limpeza no generate_cloud
old_cloud_logic = '''                # 1. O Prompt pede o HTML COMPLETO dentro do Scaffold
                sys_prompt = (
                    f"Voce e um Engenheiro de Software Sênior. Gere o codigo HTML/CSS/JS COMPLETO para: {prompt}.\\n"
                    "REGRAS:\\n"
                    "1. Use o seguinte esqueleto (Scaffold) e preencha o {INNER}:\\n"
                    f"{SCAFFOLD_TEMPLATE}\\n\\n"
                    "2. Inclua todo o JavaScript necessario para a logica funcionar.\\n"
                    "3. Retorne APENAS o codigo HTML final, sem explicacoes ou markdown."
                )'''

new_cloud_logic = '''                # 1. Obtem o codigo base (com a melhor correspondencia)
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

if old_cloud_logic in code:
    code = code.replace(old_cloud_logic, new_cloud_logic)
    print("[OK] Prompt e logica do generate_cloud atualizados.")
else:
    print("[AVISO] Padrao antigo do generate_cloud nao encontrado.")

# 2. Adicionar a limpeza da div app-container na resposta
old_clean = '''                res_text = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', res_text, flags=re.IGNORECASE)'''

new_clean = '''                res_text = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', res_text, flags=re.IGNORECASE)
                # Remove a div app-container externa (para nao criar moldura)
                res_text = re.sub(r'<div class=["\']app-container["\'][^>]*>', '', res_text, flags=re.IGNORECASE)
                res_text = re.sub(r'</div>\s*$', '', res_text, flags=re.IGNORECASE)'''

if old_clean in code:
    code = code.replace(old_clean, new_clean)
    print("[OK] Limpeza da div app-container adicionada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)