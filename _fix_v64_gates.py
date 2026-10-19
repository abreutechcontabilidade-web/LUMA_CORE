import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v64_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. GARANTIR IMPORTS NO TOPO (G13)
if "from intelligence.key_ring import KeyRing" not in code:
    code = "from intelligence.key_ring import KeyRing\n" + code
if "from http.server import ThreadingHTTPServer" not in code:
    code = "from http.server import ThreadingHTTPServer\n" + code
if "import socketserver" not in code:
    code = "import socketserver\n" + code

# 2. KEYRING SINGLETON (G12)
if "anel = KeyRing(" not in code:
    # Injeta o anel logo antes do bloco __main__
    if 'if __name__ == "__main__":' in code:
        code = code.replace(
            'if __name__ == "__main__":',
            "vault_path = r'C:\\Users\\user\\Desktop\\cpf_arboreo_repo\\_bancada\\motor\\lib\\vault.json'\nif not os.path.exists(vault_path): vault_path = r'C:\\Users\\user\\Desktop\\lumazbit\\vault.json'\nanel = KeyRing(vault_path)\n\nif __name__ == \"__main__\":"
        )
        print("[OK] KeyRing instanciado como Singleton (G12).")

# 3. CIRURGIA DELIMITADA (G10)
start_marker = 'elif self.path == "/api/generate_cloud":'
start_idx = code.find(start_marker)

if start_idx != -1:
    # Acha o fim da rota (o próximo "def " ou o bloco "__main__")
    rest_code = code[start_idx:]
    match_end = re.search(r'\n    def |\nif __name__', rest_code)
    
    if match_end:
        end_idx = start_idx + match_end.start()
    else:
        end_idx = len(code)

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

            # NUVEM (FALLBACK)
            tentativas = 0
            max_tentativas = len(anel.keys) if anel.keys else 1
            resposta_final = None
            fonte = "Falha Total"
            
            while tentativas < max_tentativas:
                chave = anel.get_key()
                if not chave:
                    break
                
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
                    print(f"[ERRO] {provider_name} {e.code}: {e.read().decode('utf-8')[:100]}")
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
                    print(f"[ERRO] Falha ao salvar na memoria: {e}")
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                self._send_json({"status": "error", "message": "Chaves esgotadas.", "fonte": "KeyRing Esgotado", "elapsed_ms": elapsed}, 500)

    '''
    code = code[:start_idx] + rota_nova + code[end_idx:]
    print("[OK] Cirurgia delimitada (G10) concluida.")
else:
    print("[ERRO] Rota nao encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

# CENSO POS-PATCH (G11)
print("\n=== CENSO POS-PATCH (G11) ===")
print(f"__main__ presente: {'if __name__' in code}")
print(f"Rota generate_cloud presente: {'/api/generate_cloud' in code}")

try:
    py_compile.compile(path, doraise=True)
    print("\n[OK] py_compile PASSOU. Nenhum cadáver.")
except Exception as e:
    print(f"\n[FALHA] {e}")
    shutil.copy2(bak, path)