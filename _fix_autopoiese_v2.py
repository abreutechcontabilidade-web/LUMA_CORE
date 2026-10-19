import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_autov2_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Encontra o bloco da Autopoiese e injeta a mutação ONNX
old_auto = '''                # 3. AUTOPOIESE (GATE-19: Criacao via Servidor)
                print("[AUTOPOIESE] Nuvem falhou. Criando esqueleto local via API...")
                html_auto = gerar_esqueleto_local(prompt)
                
                # Salva no genoma
                intent_local = prompt.lower().replace(" ", "_")[:20]
                cerebro.dynamic_tools[intent_local] = {"html": html_auto, "features": ["autopoiese"]}'''

new_auto = '''                # 3. AUTOPOIESE (GATE-19: Criacao via Servidor)
                print("[AUTOPOIESE] Nuvem falhou. Criando esqueleto local via API...")
                html_auto = gerar_esqueleto_local(prompt)
                
                # A MUTACAO ONNX DEVE OCORRER NO ESQUELETO RECEM-CRIADO
                miolo_auto = ler_miolo(html_auto)
                mutacoes_auto = inferir_mutacao(prompt, miolo_auto)
                if mutacoes_auto:
                    print(f"[AUTOPOIESE] Aplicando {len(mutacoes_auto)} mutacoes ONNX no esqueleto...")
                    html_auto = aplicar_mutacoes(html_auto, mutacoes_auto)
                
                # Salva no genoma
                intent_local = prompt.lower().replace(" ", "_")[:20]
                cerebro.dynamic_tools[intent_local] = {"html": html_auto, "features": ["autopoiese_evoluida"]}'''

if old_auto in code:
    code = code.replace(old_auto, new_auto)
    print("[OK] Rota da Autopoiese corrigida para injetar mutacoes ONNX.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Verificando se ja foi corrigido...")
    if "mutacoes_auto = inferir_mutacao(prompt, miolo_auto)" in code:
        print("[OK] O codigo ja contem a correcao.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O motor esta blindado.")