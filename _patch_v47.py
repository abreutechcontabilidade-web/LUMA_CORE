import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v47_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o bloco do /api/generate_cloud inteiro
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

                # 1. Obtem a chave estavel e as features pedidas
                from intelligence.feature_engine import extrair_chave_estavel, extrair_features
                chave = extrair_chave_estavel(prompt)
                features_pedidas = extrair_features(prompt)

                # 2. Obtem o HTML base (com features incompletas, se existir)
                local_base, fonte = cerebro.processar(prompt)
                if not local_base:
                    local_base = SCAFFOLD_TEMPLATE.replace("{INNER}", "")

                # 3. Calcula o delta de features
                entry_atual = cerebro.dynamic_tools.get(chave, {})
                features_salvas = set(entry_atual.get("features", []))
                features_em_falta = set(features_pedidas) - features_salvas

                # 4. Pede a Nuvem para ADICIONAR apenas as features em falta
                if features_em_falta:
                    delta_prompt = (
                        f"Voce e um Engenheiro de Software Sênior.\\n"
                        f"CODIGO BASE:\\n{local_base}\\n\\n"
                        f"TAREFA: Adicione APENAS as seguintes funcionalidades: {', '.join(features_em_falta)}.\\n"
                        "REGRAS:\\n"
                        "1. NAO altere o que ja existe. Mantenha o HTML/CSS/JS atual.\\n"
                        "2. Adicione o HTML da nova funcionalidade dentro do container principal.\\n"
                        "3. Adicione o JavaScript necessario.\\n"
                        "4. Retorne o codigo HTML COMPLETO e MODIFICADO.\\n"
                        "5. Nao inclua explicacoes ou markdown."
                    )
                    print(f"[NUVEM] A pedir features em falta: {features_em_falta}")
                else:
                    print(f"[LOCAL] Todas as features ja existem. A devolver cache.")
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return

                res, provider, _ = gerar_com_fallback(delta_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                res_text = str(res).strip()
                res_text = re.sub(r'```[a-z]*\\n?', '', res_text, flags=re.IGNORECASE)
                res_text = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', res_text, flags=re.IGNORECASE)
                res_text = re.sub(r'<div class=["\']app-container["\'][^>]*>', '', res_text, flags=re.IGNORECASE)

                # 5. ORDEM DA CURADORIA: Scaffold -> Inject -> CISO -> Testes -> Guardar
                final_html = SCAFFOLD_TEMPLATE.replace("{INNER}", res_text)
                
                # 5.1. CISO (valida o codigo completo)
                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                # 5.2. Testes funcionais (verifica se as features estao presentes)
                # (Implementacao simplificada)
                for f in features_em_falta:
                    if f not in final_html.lower():
                        print(f"[TESTE] Feature '{f}' nao encontrada no HTML final.")
                        self._send_json({"status": "error", "message": f"A Nuvem nao gerou a feature '{f}'."})
                        return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                # 6. GUARDA A NOVA VERSAO (com features atualizadas)
                cerebro.dynamic_tools[chave] = {"html": final_html, "features": list(features_pedidas)}
                from intelligence.feature_engine import guardar_memoria
                guardar_memoria(cerebro.db_path, cerebro.dynamic_tools)
                print(f"[MEMORIA] Versao '{chave}' guardada com features: {features_pedidas}")
                
                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + Delta", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

code = code[:start] + novo_bloco + code[end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado (Delta Prompt).")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)