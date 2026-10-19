import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v61_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

# Encontra o início da rota
for i, line in enumerate(lines):
    if 'elif self.path == "/api/generate_cloud":' in line:
        start_idx = i
        # Encontra o fim da rota (próximo elif, else ou def)
        for j in range(i + 1, len(lines)):
            if lines[j].strip().startswith('elif self.path ==') or lines[j].strip().startswith('def ') or lines[j].strip().startswith('else:'):
                end_idx = j
                break
        break

if start_idx != -1 and end_idx != -1:
    rota_nova = '''        elif self.path == "/api/generate_cloud":
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
            
            from intelligence.key_ring import KeyRing
            # Tenta o caminho real do inventario, com fallback
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
                
                if chave.startswith("sk-or-v1"):
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {chave}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8080",
                        "X-Title": "LUMA_CORE"
                    }
                    payload = {
                        "model": "deepseek/deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    provider_name = "OpenRouter"
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
                    with urllib.request.urlopen(req, timeout=30) as response:
                        res_body = response.read().decode("utf-8", errors="replace")
                        res_json = json.loads(res_body)
                        
                        if chave.startswith("sk-or-v1"):
                            resposta_final = res_json["choices"][0]["message"]["content"]
                        else:
                            resposta_final = res_json["candidates"][0]["content"]["parts"][0]["text"]
                            
                        fonte = f"{provider_name} Nuvem"
                        break
                except urllib.error.HTTPError as e:
                    if e.code in [402, 429, 401]:
                        anel.mark_dead(chave, cooldown_hours=1)
                    tentativas += 1
                except Exception as e:
                    print(f"[ERRO] Falha na requisicao: {e}")
                    tentativas += 1
            
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            
            if resposta_final:
                # Salva no cerebro local
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                    print(f"[MEMORIA] Ouro salvo para: '{prompt[:30]}...'")
                except Exception as e:
                    print(f"[AVISO] Falha ao salvar na memoria: {e}")
                    
                self._send_json({
                    "status": "success",
                    "html": resposta_final,
                    "fonte": fonte,
                    "elapsed_ms": elapsed
                })
            else:
                self._send_json({
                    "status": "error",
                    "message": "Todas as chaves falharam ou estao em cooldown.",
                    "fonte": "KeyRing Esgotado",
                    "elapsed_ms": elapsed
                }, 500)
'''
    lines = lines[:start_idx] + [rota_nova] + lines[end_idx:]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("[OK] Rota /api/generate_cloud reconstruida com sucesso.")
else:
    print("[ERRO] Nao foi possivel encontrar os limites da rota.")
    import sys
    sys.exit(1)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. O app.py esta curado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)