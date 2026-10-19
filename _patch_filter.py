import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_filter_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui a logica de aprendizado para exigir o Scaffold
old_save = '''                        cerebro.aprender_da_nuvem(prompt, res_text)
                        self._send_json({"status": "success", "html": res_text, "fonte": f"Nuvem ({provider}) + Scaffold", "elapsed_ms": elapsed})'''

new_save = '''                        # FILTRO DE SCAFFOLD: So guarda se o layout base foi respeitado
                        tem_display = 'class="display"' in res_text or "class='display'" in res_text
                        tem_grid = 'class="grid"' in res_text or "class='grid'" in res_text
                        
                        if tem_display and tem_grid:
                            cerebro.aprender_da_nuvem(prompt, res_text)
                            print("[FUSAO ACEITA] Layout do Scaffold respeitado. Guardado na memoria.")
                            self._send_json({"status": "success", "html": res_text, "fonte": f"Nuvem ({provider}) + Scaffold", "elapsed_ms": elapsed})
                        else:
                            print("[FUSAO REJEITADA] A nuvem fugiu do Scaffold. Nao sera guardado.")
                            self._send_json({"status": "error", "message": "A nuvem gerou um layout invalido (fora do Scaffold). Tente novamente."})'''

if old_save in code:
    code = code.replace(old_save, new_save)
    print("[OK] Filtro de Scaffold aplicado.")
else:
    print("[AVISO] Padrao antigo de save nao encontrado. Tentando regex...")
    # Fallback mais flexivel
    code = re.sub(r'cerebro\.aprender_da_nuvem\(prompt, res_text\)\s*self\._send_json\(\{"status": "success", "html": res_text, "fonte": f"Nuvem \(\{provider\}\) \+ Scaffold", "elapsed_ms": elapsed\}\)', new_save, code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)