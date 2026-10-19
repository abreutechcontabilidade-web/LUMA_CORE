# -*- coding: utf-8 -*-
import os, sys, shutil, time, py_compile, re

APP_PATH = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = APP_PATH + ".bak_modifier_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(APP_PATH, bak)
print(f"[OK] Backup: {bak}")

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = 'elif self.path == "/api/generate_cloud":'
end_marker = 'else:\n            self.send_response(404)'

start = code.find(start_marker)
end = code.find(end_marker, start)

if start == -1 or end == -1:
    print("[ERRO] Nao foi possivel localizar o bloco /api/generate_cloud.")
    sys.exit(1)

novo_bloco = '''elif self.path == "/api/generate_cloud":
            if not INTELIGENCIA_OK:
                self._send_json({"status": "error", "message": "Nuvem offline."})
                return
            try:
                length = int(self.headers['Content-Length'])
                payload = json.loads(self.rfile.read(length))
                prompt = payload.get("prompt", "")
                t0 = time.perf_counter()

                # 1. Pega no codigo base do Motor Local (com ganchos)
                local_html, fonte_local = cerebro.processar(prompt)
                if not local_html:
                    local_html = SCAFFOLD_TEMPLATE.replace("{INNER}", "<div class='display'></div><div class='grid'></div>")

                # 2. PROMPT DE MODIFICACAO FORCADA
                sys_prompt = (
                    f"Voce e um Engenheiro de Software Sênior. Abaixo esta o codigo base de uma aplicacao funcional.\\n"
                    f"SUA TAREFA E OBRIGATORIA: Modificar o codigo base para atender EXATAMENTE ao pedido do usuario.\\n"
                    f"PEDIDO DO USUARIO: {prompt}\\n\\n"
                    "REGRAS CRITICAS:\\n"
                    "1. NAO devolva o codigo original sem modificacoes. Voce DEVE aplicar as mudancas pedidas (ex: cores, placar de empate, etc).\\n"
                    "2. PRESERVE a estrutura existente (IDs, classes, funcoes play/checkWin).\\n"
                    "3. Retorne o codigo HTML/JS COMPLETO e MODIFICADO dentro do <div class='app-container'>.\\n"
                    "4. NAO inclua <!DOCTYPE html>, <html>, <head> ou <body>.\\n"
                    "5. Retorne APENAS o codigo puro, sem explicacoes ou markdown.\\n\\n"
                    f"CODIGO BASE (REGRAS A SEREM MODIFICADAS):\\n{local_html}"
                )
                
                res, provider, _ = gerar_com_fallback(sys_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                res_text = str(res).strip()
                # Limpeza profunda
                res_text = re.sub(r'```[a-z]*\\n?', '', res_text, flags=re.IGNORECASE)
                res_text = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', res_text, flags=re.IGNORECASE)
                res_text = re.sub(r'<style[^>]*>.*?</style>', '', res_text, flags=re.IGNORECASE | re.DOTALL)
                
                # 3. Envolve no Scaffold
                final_html = SCAFFOLD_TEMPLATE.replace("{INNER}", res_text)

                # 4. Validacao
                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                # 5. GUARDA O OURO NA MEMORIA
                cerebro.aprender_da_nuvem(prompt, final_html)
                print(f"[MEMORIA] Ouro modificado guardado para: '{prompt[:30]}...'")
                
                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + Modificador", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

code = code[:start] + novo_bloco + code[end:]

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(APP_PATH, doraise=True)
    print("[OK] py_compile PASSOU. Modificador Forcado instalado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, APP_PATH)
    sys.exit(1)