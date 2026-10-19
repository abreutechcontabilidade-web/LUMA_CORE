# -*- coding: utf-8 -*-
import os, sys, shutil, time, py_compile, re

APP_PATH = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = APP_PATH + ".bak_iterative_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(APP_PATH, bak)
print(f"[OK] Backup: {bak}")

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Encontra o bloco do /api/generate_cloud
start_marker = 'elif self.path == "/api/generate_cloud":'
end_marker = 'else:\n            self.send_response(404)'

start = code.find(start_marker)
end = code.find(end_marker, start)

if start == -1 or end == -1:
    print("[ERRO] Nao foi possivel localizar o bloco /api/generate_cloud.")
    sys.exit(1)

# O novo bloco com o Loop Iterativo
novo_bloco = '''elif self.path == "/api/generate_cloud":
            if not INTELIGENCIA_OK:
                self._send_json({"status": "error", "message": "Nuvem offline."})
                return
            try:
                length = int(self.headers['Content-Length'])
                payload = json.loads(self.rfile.read(length))
                prompt = payload.get("prompt", "")
                t0 = time.perf_counter()
                
                # --- LOOP DE FEEDBACK ITERATIVO ---
                inner = ""
                provider_nome = "Nuvem"
                
                for tentativa in range(1, 4):
                    print(f"[NUVEM] Tentativa {tentativa}...")
                    
                    if tentativa == 1:
                        sys_prompt = (
                            f"Gere APENAS o codigo HTML interno e a tag <script> para: {prompt}.\\n"
                            "NAO inclua <!DOCTYPE html>, <html>, <head>, <style> ou <body>.\\n"
                            "O codigo sera injetado dentro de: <div class='app-container'>.\\n"
                            "Use botoes, inputs e o JavaScript necessario. Seja conciso.\\n"
                            "Retorne APENAS o codigo puro (sem markdown)."
                        )
                    else:
                        # Prompt de correcao preciso
                        sys_prompt = (
                            f"O codigo anterior falhou na validacao com o erro: {erro_anterior}.\\n"
                            "Corrija o problema e DEVOLVA APENAS O MIOLO DO CODIGO CORRIGIDO.\\n"
                            "Nao use markdown. Nao adicione explicacoes.\\n"
                            f"Codigo anterior:\\n{inner}"
                        )
                    
                    res, provider, _ = gerar_com_fallback(sys_prompt)
                    if not res:
                        continue
                        
                    inner = str(res).strip()
                    inner = re.sub(r'```[a-z]*\\n?', '', inner, flags=re.IGNORECASE)
                    inner = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', inner, flags=re.IGNORECASE)
                    inner = re.sub(r'<style[^>]*>.*?</style>', '', inner, flags=re.IGNORECASE | re.DOTALL)
                    
                    res_text = SCAFFOLD_TEMPLATE.replace("{INNER}", inner)
                    
                    # Validacao 1: CISO
                    ok_ciso, motivo_ciso = WebCISOGate.validar_html(res_text)
                    if not ok_ciso:
                        erro_anterior = f"Bloqueio CISO: {motivo_ciso}"
                        print(f"[NUVEM] Falhou no CISO. A tentar novamente...")
                        continue
                    
                    # Validacao 2: Scaffold (classes obrigatorias)
                    if 'class="display"' not in res_text and "class='display'" not in res_text:
                        erro_anterior = "O codigo nao tem <div class='display'> para o visor."
                        print(f"[NUVEM] Falhou no Scaffold (falta display). A tentar novamente...")
                        continue
                    if 'class="grid"' not in res_text and "class='grid'" not in res_text:
                        erro_anterior = "O codigo nao tem <div class='grid'> para os botoes."
                        print(f"[NUVEM] Falhou no Scaffold (falta grid). A tentar novamente...")
                        continue
                        
                    # Validacao 3: Funcoes JS
                    onclick_funcs = re.findall(r'onclick="([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(', res_text)
                    funcoes_ok = True
                    for func in set(onclick_funcs):
                        if f"function {func}" not in res_text and f"{func} =" not in res_text and f"{func}=" not in res_text:
                            erro_anterior = f"A funcao '{func}' nao foi definida."
                            print(f"[NUVEM] Falhou na logica (falta {func}). A tentar novamente...")
                            funcoes_ok = False
                            break
                    if not funcoes_ok:
                        continue
                        
                    # Se chegou aqui, passou em tudo
                    print(f"[NUVEM] Sucesso na tentativa {tentativa}!")
                    provider_nome = provider
                    break
                else:
                    # Loop esgotou as tentativas
                    self._send_json({"status": "error", "message": "A nuvem nao conseguiu gerar um codigo valido apos 3 tentativas."})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                # Guarda na memoria (apenas se passou no loop)
                cerebro.aprender_da_nuvem(prompt, res_text)
                print("[MEMORIA] Codigo da nuvem guardado (passou no loop).")
                self._send_json({"status": "success", "html": res_text, "fonte": f"Nuvem ({provider_nome}) + Scaffold", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

# Substitui o bloco
code = code[:start] + novo_bloco + code[end:]

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(APP_PATH, doraise=True)
    print("[OK] py_compile PASSOU. Loop de Feedback Iterativo instalado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, APP_PATH)
    sys.exit(1)