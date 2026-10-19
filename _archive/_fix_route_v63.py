import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v63_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if 'elif self.path == "/api/generate_cloud":' in line:
        start_idx = i
        break

if start_idx != -1:
    lines = lines[:start_idx]
    
    rota = '''        elif self.path == "/api/generate_cloud":
            import time
            import urllib.request
            import urllib.error
            import json
            
            start_time = time.perf_counter()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return

            # --- 1. CACHE LOCAL PRIMEIRO ---
            try:
                from intelligence.feature_engine import extrair_intencao
                intent = extrair_intencao(prompt)
                print(f"[DEBUG] Intent: '{intent}' | Memoria: {list(cerebro.dynamic_tools.keys())}")
                
                if intent in cerebro.dynamic_tools:
                    entry = cerebro.dynamic_tools[intent]
                    local_html = entry["html"] if isinstance(entry, dict) and "html" in entry else entry
                    elapsed_local = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache hit! Respondendo em {elapsed_local}ms.")
                    self._send_json({"status": "success", "html": local_html, "fonte": "APRENDIDO_LOCAL", "elapsed_ms": elapsed_local})
                    return
            except Exception as e:
                print(f"[AVISO] Erro no cache local: {e}")

            # --- 2. KEYRING E PROVEDORES ---
            from intelligence.key_ring import KeyRing
            vault_path = r"C:\\Users\\user\\Desktop\\cpf_arboreo_repo\\_bancada\\motor\\lib\\vault.json"
            if not os.path.exists(vault_path):
                vault_path = r"C:\\Users\\user\\Desktop\\lumazbit\\vault.json"
            
            anel = KeyRing(vault_path)
            
            tentativas = 0
            max_tentativas = len(anel.keys) if anel.keys else 1
            resposta_final = None
            fonte = "Falha Total"
            
            while tentativas < max_tentativas:
                chave = anel.get_key()
                if not chave:
                    break
                
                # Roteamento por Provedor
                if chave.startswith("sk-or-v1"):
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json", "HTTP-Referer": "http://localhost:8080"}
                    payload = {"model": "deepseek/deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
                    provider_name = "OpenRouter"
                elif chave.startswith("gsk_"):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
                    payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}]}
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
                    # Zai ou outros - pula
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
                    if e.code in [402, 429, 401]:
                        anel.mark_dead(chave, cooldown_hours=1)
                    tentativas += 1
                except Exception as e:
                    tentativas += 1
            
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                    print(f"[MEMORIA] Ouro salvo para: {prompt[:30]}...")
                except Exception:
                    pass
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                self._send_json({"status": "error", "message": "Chaves esgotadas.", "fonte": "KeyRing Esgotado", "elapsed_ms": elapsed}, 500)
'''
    lines.append(rota)
    
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("[OK] Rota reconstruida com todos os provedores e cache local.")
else:
    print("[ERRO] Nao achei a rota no arquivo.")

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)