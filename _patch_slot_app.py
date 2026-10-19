import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_slot_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

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

                from intelligence.onnx_sota import compor_chave
                from intelligence.slot_engine import SCAFFOLD_SLOTS, aplicar_delta

                info = compor_chave(prompt)
                chave = info["chave"]
                features_pedidas = set(info["features"])
                posicoes_pedidas = set(info["posicoes"])
                print(f"[SOTA] Chave: {chave} | Features: {info['features']} | Posicoes: {info['posicoes']}")

                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base, fonte = SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"

                if "APRENDIDO_" in fonte and "LOCAL_BASIC" not in fonte:
                    self._send_json({"status": "success", "html": local_base, "fonte": fonte, "elapsed_ms": 0.01})
                    return

                intencao_base = info["intencao"]
                entry = cerebro.memoria.get(intencao_base, {})
                features_salvas = set()
                posicoes_salvas = set()
                if entry and "versoes" in entry and entry["versoes"]:
                    melhor = max(entry["versoes"], key=lambda v: len(v.get("features", [])))
                    features_salvas = set(melhor.get("features", []))
                    posicoes_salvas = set(melhor.get("posicoes", []))
                
                features_em_falta = features_pedidas - features_salvas
                posicoes_em_falta = posicoes_pedidas - posicoes_salvas

                if not features_em_falta and not posicoes_em_falta:
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return

                target_slot = "slot-main"
                if features_em_falta & {"placar", "historico", "empate"}:
                    target_slot = "slot-header" if "topo" in posicoes_pedidas else "slot-controls"
                if features_em_falta & {"proxima_rodada", "zerar"}:
                    target_slot = "slot-controls"

                partes = []
                if features_em_falta: partes.append("Adicionar: " + ", ".join(features_em_falta))
                if posicoes_em_falta: partes.append("Posicao: " + ", ".join(posicoes_em_falta))

                delta_prompt = f"""Voce e um Engenheiro de Software Senior.
TAREFA: Gerar um DELTA JSON para adicionar as funcionalidades em falta.
CODIGO BASE ATUAL:
{local_base}
FUNCIONALIDADES: {', '.join(features_em_falta) if features_em_falta else 'nenhuma'}
SLOT ALVO: {target_slot}
REGRAS:
1. NAO devolva o app inteiro. Devolva APENAS o JSON de mutacao.
2. Estrutura EXATA:
{{
  "target_slot": "{target_slot}",
  "action": "replace_inner" ou "append_inner",
  "html": "<div>...</div>",
  "css_delta": ".minha-classe {{ color: red; }}",
  "js_hooks": {{ "minha_funcao": "function() {{ ... }}" }}
}}
3. Nao use markdown. Retorne APENAS o JSON puro.
4. HTML deve ser fragmento (nao inclua DOCTYPE).
"""
                print(f"[NUVEM] Pedindo DELTA para slot '{target_slot}': {partes}")
                res, provider, _ = gerar_com_fallback(delta_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                delta_str = str(res).strip()
                delta_str = re.sub(r'```[a-z]*\\n?', '', delta_str, flags=re.IGNORECASE).strip()

                novo_html, motivo_delta = aplicar_delta(local_base, delta_str)
                if not novo_html:
                    self._send_json({"status": "error", "message": f"Delta invalido: {motivo_delta}"})
                    return

                ok, motivo = WebCISOGate.validar_html(novo_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                cerebro.aprender(prompt, novo_html)

                self._send_json({"status": "success", "html": novo_html, "fonte": f"Nuvem ({provider}) + Slot", "elapsed_ms": elapsed})

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
    print("[OK] py_compile PASSOU. app.py atualizado com Slot Engine.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)