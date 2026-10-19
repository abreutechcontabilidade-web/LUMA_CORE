import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_sota_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Atualiza o bloco /api/generate_cloud
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

                from onnx_sota import compor_chave
                info = compor_chave(prompt)
                chave = info["chave"]
                features_pedidas = set(info["features"])
                posicoes_pedidas = set(info["posicoes"])
                
                print(f"[SOTA] Chave: {chave} | Features: {info['features']} | Posicoes: {info['posicoes']}")

                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base = SCAFFOLD_TEMPLATE.replace("{INNER}", "")

                # Verifica o que falta
                entry_atual = cerebro.memoria.get(chave, {})
                features_salvas = set(entry_atual.get("features", []))
                posicoes_salvas = set(entry_atual.get("posicoes", []))
                features_em_falta = features_pedidas - features_salvas
                posicoes_em_falta = posicoes_pedidas - posicoes_salvas

                if not features_em_falta and not posicoes_em_falta:
                    print(f"[LOCAL] Tudo ja existe na chave '{chave}'.")
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return

                # Constroi o prompt delta
                partes_pedido = []
                if features_em_falta: partes_pedido.append(f"Adicionar funcionalidades: {', '.join(features_em_falta)}")
                if posicoes_em_falta: partes_pedido.append(f"Colocar na posicao: {', '.join(posicoes_em_falta)}")

                delta_prompt = (
                    f"Voce e um Engenheiro de Software Senior.\\n"
                    f"CODIGO BASE:\\n{local_base}\\n\\n"
                    f"TAREFA: {' E '.join(partes_pedido)}.\\n"
                    "REGRAS:\\n"
                    "1. NAO altere o que ja existe.\\n"
                    "2. Adicione o HTML/JS das novas funcionalidades.\\n"
                    "3. Retorne o codigo HTML COMPLETO e MODIFICADO.\\n"
                    "4. Nao use markdown."
                )
                print(f"[NUVEM] Pedindo: {partes_pedido}")

                res, provider, _ = gerar_com_fallback(delta_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                miolo = str(res).strip()
                miolo = re.sub(r'```[a-z]*\\n?', '', miolo, flags=re.IGNORECASE)
                miolo = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', miolo, flags=re.IGNORECASE)
                miolo = re.sub(r'<div[^>]*class=["\\']app-container["\\'][^>]*>', '', miolo, flags=re.IGNORECASE)

                final_html = SCAFFOLD_TEMPLATE.replace("{INNER}", miolo)

                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)

                # Guarda na memoria com a chave composta
                cerebro.memoria[chave] = {
                    "html": final_html,
                    "features": info["features"],
                    "posicoes": info["posicoes"],
                    "intencao": info["intencao"],
                    "categoria": info["categoria"],
                }
                cerebro._guardar()
                print(f"[MEMORIA] Chave '{chave}' guardada.")

                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + SOTA", "elapsed_ms": elapsed})

            except Exception as e:
                import traceback
                traceback.print_exc()
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

code = code[:start] + novo_bloco + code[end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado com ONNX-SOTA.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)