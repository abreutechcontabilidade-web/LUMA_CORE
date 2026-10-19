import os, shutil, time, py_compile, re

# 1. LIMPEZA DO LOCAL SYNTHESIS
synth_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\local_synthesis.py"
synth_code = '''
import json, re, os

def analisar_e_evoluir(html_atual, prompt_novo):
    html_novo = str(html_atual)
    features_adicionadas = []
    prompt_lower = prompt_novo.lower()
    
    if "cor" in prompt_lower or "vermelho" in prompt_lower:
        if "background-color: #8b0000" not in html_novo:
            html_novo = html_novo.replace("</style>", "body { background-color: #8b0000 !important; color: white; }</style>")
            features_adicionadas.append("cor_vermelha")
            
    if "som" in prompt_lower or "audio" in prompt_lower:
        if "function tocarSom()" not in html_novo:
            js_som = "\\nfunction tocarSom() { var audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg'); audio.play(); }\\n"
            if "</script>" in html_novo:
                html_novo = html_novo.replace("</script>", js_som + "</script>")
            html_novo = html_novo.replace("</body>", "<button onclick='tocarSom()' style='position:fixed; bottom:10px; right:10px;'>Tocar Som</button></body>")
            features_adicionadas.append("som")

    return html_novo, features_adicionadas

def processar_sintese(prompt_usuario):
    db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
    if not os.path.exists(db_path): return None, "Sem memoria"
        
    with open(db_path, "r", encoding="utf-8") as f:
        memoria = json.load(f)
        
    chave_alvo = None
    for k in memoria.keys():
        if "velha" in prompt_usuario.lower() and "velha" in k.lower():
            chave_alvo = k
            break
            
    if not chave_alvo:
        return None, "Nao encontrado no cache."
        
    entry = memoria[chave_alvo]
    # TRATAMENTO ROBUSTO
    if isinstance(entry, dict):
        html_atual = entry.get("html", "")
        features_antigas = entry.get("features", [])
    else:
        html_atual = entry
        features_antigas = []
        
    html_evoluido, novas_features = analisar_e_evoluir(html_atual, prompt_usuario)
    
    if novas_features:
        features_todas = list(set(features_antigas + novas_features))
        memoria[chave_alvo] = {"html": html_evoluido, "features": features_todas}
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
        return html_evoluido, f"EVOLUIDO_LOCAL_{novas_features}"
        
    return html_atual, "CACHE_LOCAL_PURO"
'''
with open(synth_path, "w", encoding="utf-8") as f:
    f.write(synth_code)
print("[OK] local_synthesis.py reescrito e à prova de falhas.")

# 2. LIMPEZA E REESCRITA DO APP.PY
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_final65_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove instâncias antigas e erradas do KeyRing
code = re.sub(r"vault_path = r'.*?'\nif not os.path.exists\(vault_path\).*?\n", "", code)
code = re.sub(r"anel = KeyRing\(vault_path\)\n", "", code)

# Injeta o KeyRing (Singleton) no TOPO absoluto
header = '''
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intelligence.key_ring import KeyRing

vault_path = r"C:\\Users\\user\\Desktop\\cpf_arboreo_repo\\_bancada\\motor\\lib\\vault.json"
if not os.path.exists(vault_path): vault_path = r"C:\\Users\\user\\Desktop\\lumazbit\\vault.json"
anel = KeyRing(vault_path)
'''
if "anel = KeyRing(vault_path)" not in code[:500]:
    code = header + code
    print("[OK] KeyRing (anel) instanciado no topo absoluto do app.py.")

# Reconstrói a rota
start_marker = 'elif self.path == "/api/generate_cloud":'
start_idx = code.find(start_marker)

if start_idx != -1:
    match_end = re.search(r'\n    def |\nif __name__', code[start_idx:])
    end_idx = start_idx + match_end.start() if match_end else len(code)

    rota_nova = '''elif self.path == "/api/generate_cloud":
            import time, urllib.request, urllib.error, json
            
            start_time = time.perf_counter()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return

            # CACHE E SINTESE LOCAL
            try:
                from intelligence.feature_engine import extrair_intencao
                from intelligence.local_synthesis import processar_sintese
                intent = extrair_intencao(prompt)
                print(f"[DEBUG] Intent: '{intent}' | Memoria: {list(cerebro.dynamic_tools.keys())}")
                
                local_html, status_synth = processar_sintese(prompt)
                if local_html:
                    elapsed_local = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache/Sintese: '{status_synth}' em {elapsed_local}ms.")
                    self._send_json({"status": "success", "html": local_html, "fonte": status_synth, "elapsed_ms": elapsed_local})
                    return
            except Exception as e:
                print(f"[AVISO] Erro no cache local: {e}")

            # NUVEM
            tentativas = 0
            max_tentativas = len(anel.keys) if anel.keys else 1
            resposta_final = None
            fonte = "Falha Total"
            
            while tentativas < max_tentativas:
                chave = anel.get_key()
                if not chave: break
                
                if chave.startswith("sk-or-v1"):
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
                    payload = {"model": "deepseek/deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
                    provider_name = "OpenRouter"
                elif chave.startswith("gsk_"):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
                    payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]}
                    provider_name = "Groq"
                elif chave.startswith("sk-") and not chave.startswith("sk-or-v1"):
                    url = "https://api.deepseek.com/chat/completions"
                    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
                    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
                    provider_name = "DeepSeek"
                elif chave.startswith("AIza") or chave.startswith("AQ."):
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chave}"
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    provider_name = "Gemini"
                else:
                    tentativas += 1
                    continue
                
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                
                try:
                    print(f"[NUVEM] Tentando {provider_name}...")
                    with urllib.request.urlopen(req, timeout=30) as response:
                        res_body = response.read().decode("utf-8", errors="replace")
                        res_json = json.loads(res_body)
                        if provider_name == "Gemini":
                            resposta_final = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                            resposta_final = res_json["choices"][0]["message"]["content"]
                        fonte = f"{provider_name} Nuvem"
                        break
                except urllib.error.HTTPError as e:
                    print(f"[ERRO] {provider_name} {e.code}")
                    if e.code in [402, 429, 401]:
                        anel.mark_dead(chave, cooldown_hours=1)
                    tentativas += 1
                except Exception as e:
                    print(f"[ERRO] {provider_name}: {e}")
                    tentativas += 1
            
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                    print(f"[MEMORIA] Ouro salvo para: {prompt[:30]}...")
                except Exception as e:
                    print(f"[ERRO] Falha ao salvar: {e}")
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                self._send_json({"status": "error", "message": "Chaves esgotadas.", "fonte": "KeyRing Esgotado", "elapsed_ms": elapsed}, 500)

    '''
    code = code[:start_idx] + rota_nova + code[end_idx:]
    print("[OK] Rota reconstruida com tratamento de dict e anel global.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")