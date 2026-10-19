import urllib.request, urllib.error, json, concurrent.futures

def _bater_chave(chave, prompt):
    try:
        if chave.startswith("sk-or-v1"):
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
            payload = {"model": "deepseek/deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            provider = "OpenRouter"
        elif chave.startswith("gsk_"):
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
            payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]}
            provider = "Groq"
        elif chave.startswith("sk-") and not chave.startswith("sk-or-v1"):
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
            payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            provider = "DeepSeek"
        elif chave.startswith("AIza") or chave.startswith("AQ."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chave}"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            provider = "Gemini"
        else:
            return (chave, None, "Desconhecido")

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = response.read().decode("utf-8", errors="replace")
            res_json = json.loads(res_body)
            if provider == "Gemini": texto = res_json["candidates"][0]["content"]["parts"][0]["text"]
            else: texto = res_json["choices"][0]["message"]["content"]
            return (chave, texto, None)
    except urllib.error.HTTPError as e:
        return (chave, None, f"HTTP {e.code}")
    except Exception as e:
        return (chave, None, str(e))

def disparar_enxame(prompt, anel):
    if not anel.keys: return None, "KeyRing vazio"
    chaves_ativas = [k for k in anel.keys if k not in anel.dead_keys]
    if not chaves_ativas: return None, "Todas em cooldown"

    print(f"[ENXAME] Disparando {len(chaves_ativas)} chaves em paralelo...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(chaves_ativas)) as executor:
        futuros = {executor.submit(_bater_chave, k, prompt): k for k in chaves_ativas}
        done, _ = concurrent.futures.wait(futuros, timeout=15)
        
        for futuro in done:
            chave, resposta, erro = futuro.result()
            if resposta:
                print(f"[ENXAME] Vitoria! O Enxame respondeu.")
                executor.shutdown(wait=False, cancel_futures=True)
                return resposta, "Enxame Nuvem"
            elif erro in ["HTTP 402", "HTTP 429", "HTTP 401"]:
                anel.mark_dead(chave, cooldown_hours=1)
                
    print("[ENXAME] Todas as chaves falharam ou deram timeout.")
    return None, "Falha Total"