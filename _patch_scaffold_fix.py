import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_scaffold_fix_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Garantir que o SCAFFOLD_TEMPLATE existe no topo
scaffold_code = '''
SCAFFOLD_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .app-container { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 12px; }
    .display { background: #0f172a; color: #38bdf8; font-size: 24px; padding: 10px; border-radius: 6px; text-align: right; min-height: 40px; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    button { padding: 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; background: #38bdf8; color: #0f172a; font-size: 16px; }
    button:hover { opacity: 0.8; }
</style>
</head>
<body>
    <div class="app-container">
        {INNER}
    </div>
</body>
</html>"""
'''
if "SCAFFOLD_TEMPLATE" not in code:
    # Insere antes da primeira classe
    code = code.replace("class LumaCoreHandler", scaffold_code + "\nclass LumaCoreHandler")
    print("[OK] SCAFFOLD_TEMPLATE injetado.")
else:
    print("[OK] SCAFFOLD_TEMPLATE ja existia.")

# 2. Garantir que a função extrair_intencao está no escopo
if "from intelligence.virtual_onnx import VirtualONNX, extrair_intencao" not in code:
    code = code.replace("from intelligence.virtual_onnx import VirtualONNX", "from intelligence.virtual_onnx import VirtualONNX, extrair_intencao")
elif "extrair_intencao" not in code:
    # Fallback: define a função localmente
    extrair_func = '''
def extrair_intencao(prompt: str) -> str:
    p = prompt.lower()
    tags = []
    if any(k in p for k in ["velha", "tic tac toe"]): tags.append("velha")
    if any(k in p for k in ["placar", "placa", "pontuacao"]): tags.append("placar")
    if any(k in p for k in ["empate"]): tags.append("empate")
    if any(k in p for k in ["cor", "cores", "vermelho", "azul"]): tags.append("cores")
    if any(k in p for k in ["historico", "histórico"]): tags.append("historico")
    if any(k in p for k in ["calculadora"]): tags.append("calculadora")
    return "_".join(sorted(tags)) if tags else p.strip()

'''
    code = code.replace("class LumaCoreHandler", extrair_func + "\nclass LumaCoreHandler")

# 3. Substituir a rota generate_cloud
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

                # 1. Pega no codigo base do Motor Local
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
                # Limpeza profunda (mas PRESERVANDO o CSS!)
                res_text = re.sub(r'```[a-z]*\\n?', '', res_text, flags=re.IGNORECASE)
                res_text = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', res_text, flags=re.IGNORECASE)
                # NAO REMOVEMOS O <style>! (a linha re.sub do style foi DELETADA)
                
                # 3. Envolve no Scaffold
                final_html = SCAFFOLD_TEMPLATE.replace("{INNER}", res_text)

                # 4. Validacao
                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                # 5. GUARDA O OURO NA MEMORIA (por intencao)
                cerebro.aprender_da_nuvem(prompt, final_html)
                print(f"[MEMORIA] Ouro modificado guardado para: '{prompt[:30]}...'")
                
                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + Modificador", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

code = code[:start] + novo_bloco + code[end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido (Scaffold + CSS preservado).")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)