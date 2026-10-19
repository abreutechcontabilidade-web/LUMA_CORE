import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_injector_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Importar o injector_engine
if "from intelligence.injector_engine import detectar_posicao, injetar_feature" not in code:
    code = code.replace(
        "from intelligence.feature_engine import extrair_features, carregar_memoria, guardar_memoria, extrair_intencao",
        "from intelligence.feature_engine import extrair_features, carregar_memoria, guardar_memoria, extrair_intencao\nfrom intelligence.injector_engine import detectar_posicao, injetar_feature"
    )
    print("[OK] Import do injector_engine adicionado.")

# 2. Atualizar o bloco /api/generate_cloud para usar a injecao
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

                # 1. Deteta a posicao pedida pelo utilizador
                posicao = detectar_posicao(prompt)
                print(f"[INJECTOR] Posicao detetada: {posicao}")

                # 2. Obtem o codigo base do Local (a fonte da verdade)
                local_html, fonte_local = cerebro.processar(prompt)
                if not local_html:
                    local_html = SCAFFOLD_TEMPLATE.replace("{INNER}", "<div class='display'></div><div class='grid'></div>")

                # 3. Pede a LLM APENAS a feature nova (em JSON)
                sys_prompt = (
                    f"Voce e um Engenheiro de Software Sênior. Abaixo esta o codigo base do Local.\\n"
                    f"PEDIDO DO USUARIO: {prompt}\\n\\n"
                    "INSTRUCOES:\\n"
                    "1. NAO devolva o codigo base inteiro. Gere APENAS o HTML/CSS/JS da NOVA funcionalidade pedida.\\n"
                    "2. Retorne um JSON valido com a chave 'feature': {\\"feature\\": \\"<html/css/js da nova funcionalidade>\\"}.\\n"
                    "3. Nao inclua <!DOCTYPE html>, <html>, <head> ou <body>.\\n"
                    "4. Retorne APENAS o JSON, sem explicacoes ou markdown.\\n\\n"
                    f"CODIGO BASE (para referencia):\\n{local_html}"
                )
                
                res, provider, _ = gerar_com_fallback(sys_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                res_text = str(res).strip()
                res_text = re.sub(r'```[a-z]*\\n?', '', res_text, flags=re.IGNORECASE)

                # 4. Extrai a feature do JSON
                feature_html = ""
                try:
                    import json as _json
                    data = _json.loads(res_text)
                    feature_html = data.get("feature", "")
                except Exception:
                    # Fallback: usa o HTML inteiro (mas nao ideal)
                    feature_html = res_text

                # 5. Injeta a feature no codigo do Local, na posicao correta
                if feature_html:
                    final_html = injetar_feature(local_html, feature_html, posicao)
                    print(f"[INJECTOR] Feature injetada na posicao '{posicao}'.")
                else:
                    final_html = local_html
                    print("[INJECTOR] Nenhuma feature valida recebida. A usar o codigo Local.")

                # 6. Validacao CISO
                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                # 7. Guarda na memoria (a versao final, com a feature injetada)
                cerebro.aprender_da_nuvem(prompt, final_html)
                print(f"[MEMORIA] Ouro guardado para: '{prompt[:30]}...'")
                
                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + Injecao", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

code = code[:start] + novo_bloco + code[end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado com Injecao Determinista.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)