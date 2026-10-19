import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_fix_v47_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Corrigir os imports no topo
# Remove a importacao errada de 'extrair_intencao' do feature_engine
if "from intelligence.feature_engine import extrair_intencao" in code:
    code = code.replace("from intelligence.feature_engine import extrair_intencao", "")
    print("[OK] Import de 'extrair_intencao' removido.")

# Garante que os imports corretos existem
if "from intelligence.feature_engine import" not in code:
    code = code.replace(
        "from intelligence.injector_engine import",
        "from intelligence.feature_engine import extrair_chave_estavel, extrair_features, carregar_memoria, guardar_memoria\nfrom intelligence.injector_engine import"
    )
else:
    # Substitui qualquer import antigo do feature_engine pelo novo
    code = re.sub(
        r"from intelligence\.feature_engine import [^\n]+",
        "from intelligence.feature_engine import extrair_chave_estavel, extrair_features, carregar_memoria, guardar_memoria",
        code
    )

# 2. Corrigir o regex que causou SyntaxError
# A linha problematica era algo como: res_text = re.sub(r'<div class=["\']app-container["\'][^>]*>', '', res_text, flags=re.IGNORECASE)
# Vamos substituir por uma versao segura
old_regex = r"res_text = re\.sub\(r'<div class=\[\"\\'\]app-container\[\"\\'\]\[\^>\]\*>', '', res_text, flags=re\.IGNORECASE\)"
new_regex = "res_text = re.sub(r'<div class=[\"\\']app-container[\"\\'][^>]*>', '', res_text, flags=re.IGNORECASE)"

# Tenta encontrar e substituir a linha do regex
if re.search(old_regex, code):
    code = re.sub(old_regex, new_regex, code)
    print("[OK] Regex corrigido.")
else:
    # Fallback: procura a linha exata no codigo e substitui manualmente
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if "app-container" in line and "re.sub" in line:
            lines[i] = new_regex
            print("[OK] Regex corrigido (via linha).")
            break
    code = "\n".join(lines)

# 3. Garantir que o generate_cloud tem a logica correta (sem crashes)
# Substitui o bloco inteiro do generate_cloud novamente, mas com o regex corrigido
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

                from intelligence.feature_engine import extrair_chave_estavel, extrair_features
                chave = extrair_chave_estavel(prompt)
                features_pedidas = extrair_features(prompt)

                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base = SCAFFOLD_TEMPLATE.replace("{INNER}", "")

                entry_atual = cerebro.dynamic_tools.get(chave, {})
                features_salvas = set(entry_atual.get("features", []))
                features_em_falta = set(features_pedidas) - features_salvas

                if features_em_falta:
                    delta_prompt = (
                        f"Voce e um Engenheiro de Software Sênior.\\n"
                        f"CODIGO BASE:\\n{local_base}\\n\\n"
                        f"TAREFA: Adicione APENAS as seguintes funcionalidades: {', '.join(features_em_falta)}.\\n"
                        "REGRAS:\\n"
                        "1. NAO altere o que ja existe.\\n"
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
                # Regex seguro para remover app-container
                res_text = re.sub(r'<div class=["\\']app-container["\\'][^>]*>', '', res_text, flags=re.IGNORECASE)

                final_html = SCAFFOLD_TEMPLATE.replace("{INNER}", res_text)

                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                for f in features_em_falta:
                    if f not in final_html.lower():
                        print(f"[TESTE] Feature '{f}' nao encontrada no HTML final.")
                        self._send_json({"status": "error", "message": f"A Nuvem nao gerou a feature '{f}'."})
                        return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
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
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)