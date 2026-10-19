import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v55_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = 'elif self.path == "/api/generate_cloud":'
end_marker = 'else:\n            self.send_response(404)'
start = code.find(start_marker)
end = code.find(end_marker, start)

if start == -1 or end == -1:
    print("[ERRO] Bloco /api/generate_cloud nao encontrado.")
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
                from intelligence.patch_engine import (
                    compute_sha256, validate_patch, apply_patch,
                    parse_llm_patch_response, MANIFEST, SCHEMA_VERSION,
                )

                info = compor_chave(prompt)
                chave = info["chave"]
                intencao = info["intencao"]
                features_pedidas = set(info["features"])
                posicoes_pedidas = set(info["posicoes"])

                if not intencao:
                    self._send_json({"status": "error", "message": "Intencao nao detetada."})
                    return

                print(f"[SOTA] Chave: {chave} | Features: {info['features']}")

                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base, fonte = SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"

                # Verifica o que falta
                entry = cerebro.memoria.get(intencao, {})
                features_salvas = set()
                posicoes_salvas = set()
                if isinstance(entry, dict) and "versoes" in entry and entry["versoes"]:
                    melhor = max(entry["versoes"], key=lambda v: len(v.get("features", [])))
                    features_salvas = set(melhor.get("features", []))
                    posicoes_salvas = set(melhor.get("posicoes", []))
                features_em_falta = features_pedidas - features_salvas
                posicoes_em_falta = posicoes_pedidas - posicoes_salvas

                if not features_em_falta and not posicoes_em_falta:
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return

                # Slot sugerido
                slot_alvo = "slot-main"
                if features_em_falta & {"placar", "historico", "empate", "timer"}:
                    slot_alvo = "slot-header"
                if features_em_falta & {"proxima_rodada", "zerar"}:
                    slot_alvo = "slot-controls"

                base_hash = compute_sha256(local_base)
                features_str = ", ".join(sorted(features_em_falta)) if features_em_falta else "nenhuma"
                posicoes_str = ", ".join(sorted(posicoes_em_falta)) if posicoes_em_falta else "nenhuma"

                patch_prompt = f"""Voce e um Engenheiro Senior. Gere APENAS um PATCH JSON para o HTML base.

HTML BASE:
{local_base}

INTENT_KEY: {intencao}
SLOT SUGERIDO: {slot_alvo}
FEATURES A ADICIONAR: {features_str}
POSICOES: {posicoes_str}

FORMATO OBRIGATORIO:
{{
  "schema_version": "{SCHEMA_VERSION}",
  "base_sha256": "{base_hash}",
  "intent_key": "{intencao}",
  "mutations": [
    {{"target_slot": "{slot_alvo}", "op": "replace_inner", "html": "<div>...</div>"}}
  ]
}}

REGRAS RIGIDAS:
1. NAO devolva o app inteiro. Devolva APENAS o JSON.
2. NUNCA inclua <script>, <style>, <iframe>, <object>, <link>, <form>.
3. NUNCA use atributos onclick, onload, onmouseover, etc.
4. Use data-role: {MANIFEST['data_roles']} para elementos que o JS procura.
5. Use data-action: {MANIFEST['actions']} para botoes.
6. Use id permitido: {MANIFEST['allowed_ids']}.
7. Use APENAS tags: {MANIFEST['slots']['slot-header'] + MANIFEST['slots']['slot-main'] + MANIFEST['slots']['slot-controls']}.
8. O fragmento deve ser o mais pequeno possivel.
9. Nao inclua markdown. Retorne APENAS o JSON.
"""

                print(f"[NUVEM] A pedir patch JSON (slot={slot_alvo}, features={features_em_falta})")
                res, provider, _ = gerar_com_fallback(patch_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                patch_obj, motivo_parse = parse_llm_patch_response(str(res))
                if not patch_obj:
                    self._send_json({"status": "error", "message": f"Patch invalido: {motivo_parse}", "raw": str(res)[:500]})
                    return

                ok, motivo = validate_patch(patch_obj, local_base)
                if not ok:
                    self._send_json({"status": "error", "message": f"Patch rejeitado: {motivo}", "patch": patch_obj})
                    return

                novo_html, motivo_apply = apply_patch(local_base, patch_obj)
                if not novo_html:
                    self._send_json({"status": "error", "message": f"Falha ao aplicar: {motivo_apply}"})
                    return

                ok, motivo = WebCISOGate.validar_html(novo_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                cerebro.aprender(prompt, novo_html)
                print(f"[MEMORIA] Patch aplicado e guardado: {chave}")

                self._send_json({"status": "success", "html": novo_html, "fonte": f"Nuvem ({provider}) + Patch", "elapsed_ms": elapsed})

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
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)