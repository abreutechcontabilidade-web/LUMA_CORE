import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_filter_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Procura o bloco onde o Web Learner é chamado
old_block = '''            print("[WEB LEARNER] Enxame falhou. A procurar código real no GitHub...")
            codigo_web, proveniencia = aprender_do_github(prompt)'''

new_block = '''            print("[WEB LEARNER] Enxame falhou. A procurar código real no GitHub...")
            from intelligence.onnx_sovereign import extrair_chave
            chave_limpa = extrair_chave(prompt)
            print(f"[WEB LEARNER] A procurar no GitHub por: '{chave_limpa}'...")
            codigo_web, proveniencia = aprender_do_github(chave_limpa)'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("[OK] app.py atualizado para extrair a chave antes de chamar o GitHub.")
else:
    print("[AVISO] Bloco antigo nao encontrado. Tentando substituicao parcial...")
    code = code.replace("aprender_do_github(prompt)", "aprender_do_github(extrair_chave(prompt))")
    print("[OK] Substituicao via regex realizada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")