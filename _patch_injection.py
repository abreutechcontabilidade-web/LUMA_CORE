import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_injection_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Nova funcao de injecao (antes da classe LumaCoreHandler)
injection_code = '''
def inject_feature(local_html, llm_json):
    """Injeta HTML e JS gerados pela LLM nos ganchos do codigo Local."""
    try:
        import json
        data = json.loads(llm_json)
        html_insert = data.get("html_insert", "")
        js_insert = data.get("js_insert", "")
        
        # Injeta HTML no gancho [HOOK_EXTRA_PANELS]
        if "[HOOK_EXTRA_PANELS]" in local_html:
            local_html = local_html.replace("[HOOK_EXTRA_PANELS]", html_insert)
        else:
            # Se nao houver gancho, adiciona antes do fecho do app-container
            local_html = local_html.replace("</div>\\n            <script>", html_insert + "\\n</div>\\n            <script>", 1)
        
        # Injeta JS no gancho [HOOK_AFTER_PLAY]
        if "[HOOK_AFTER_PLAY]" in local_html:
            local_html = local_html.replace("[HOOK_AFTER_PLAY]", js_insert)
        else:
            # Se nao houver gancho, adiciona antes do fecho da funcao play
            local_html = local_html.replace("                    }\\n                }\\n                function checkWin()", js_insert + "\\n                    }\\n                }\\n                function checkWin()", 1)
            
        return local_html
    except Exception as e:
        print(f"[INJECTION] Erro ao injetar: {e}")
        return None

'''

if "def inject_feature" not in code:
    code = code.replace("class LumaCoreHandler", injection_code + "\nclass LumaCoreHandler")

# 2. Substitui o bloco /api/generate_cloud pela nova logica
start_marker = 'elif self.path == "/api/generate_cloud":'
end_marker = 'else:\n            self.send_response(404)'
start = code.find(start_marker)
end = code.find(end_marker, start)

if start == -1 or end == -1:
    print("[ERRO] Nao foi possivel localizar /api/generate_cloud.")
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
                    # Se o Local nao tiver, usa um template generico vazio
                    local_html = SCAFFOLD_TEMPLATE.replace("{INNER}", "<div class='display'></div><div class='grid'></div>")

                # 2. Pede a LLM APENAS a feature nova, em JSON
                sys_prompt = (
                    f"Codigo base existente:\\n{local_html}\\n\\n"
                    f"Tarefa: Adicione a funcionalidade: {prompt}.\\n"
                    "Retorne APENAS um JSON valido com dois campos:\\n"
                    "{\\"html_insert\\": \\"HTML a ser inserido no gancho [HOOK_EXTRA_PANELS]\\", "
                    "\\"js_insert\\": \\"Codigo JS a ser inserido no gancho [HOOK_AFTER_PLAY]\\"}\\n"
                    "O HTML e JS devem integrar-se com as variaveis existentes (board, current, etc.).\\n"
                    "Nao inclua explicacoes ou markdown. Apenas o JSON."
                )
                
                res, provider, _ = gerar_com_fallback(sys_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                res_text = str(res).strip()
                res_text = re.sub(r"```[a-z]*\\n?|```", "", res_text, flags=re.IGNORECASE).strip()
                
                # 3. Injeta a feature no codigo base
                final_html = inject_feature(local_html, res_text)
                if not final_html:
                    self._send_json({"status": "error", "message": "A LLM nao devolveu um JSON valido."})
                    return

                # 4. Valida o resultado final
                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                # 5. Guarda na memoria apenas se o codigo base for novo
                if fonte_local == "NUVEM_NECESSARIA":
                    cerebro.aprender_da_nuvem(prompt, final_html)
                    print("[MEMORIA] Novo padrao hibrido guardado.")
                
                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + Injecao Local", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

code = code[:start] + novo_bloco + code[end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Injecao por Ganchos instalada.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)