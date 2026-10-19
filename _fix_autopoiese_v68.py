import os, shutil, time, py_compile

# 1. ATUALIZANDO O ONNX SOVEREIGN (difflib para similaridade real)
onnx_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_sovereign.py"
onnx_code = '''
import difflib

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    melhor_chave = None
    melhor_score = 0.0
    p_clean = prompt.lower().replace("_", " ").strip()

    for chave, entry in memoria.items():
        k_clean = chave.lower().replace("_", " ").strip()
        # SequenceMatcher faz a similaridade de forma inteligente
        score = difflib.SequenceMatcher(None, p_clean, k_clean).ratio()
        
        if score > melhor_score:
            melhor_score = score
            melhor_chave = chave

    return melhor_chave, melhor_score
'''
with open(onnx_path, "w", encoding="utf-8") as f:
    f.write(onnx_code)
print("[OK] onnx_sovereign.py atualizado com difflib (Similaridade Real).")

# 2. ATUALIZANDO O LOCAL_SYNTHESIS (Autopoiese)
synth_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\local_synthesis.py"
synth_code = '''
import json, re, os

def gerar_esqueleto_local(prompt):
    p = prompt.lower()
    if "cobra" in p or "snake" in p:
        return """<!DOCTYPE html><html><head><style>body{background:#1e293b;color:white;display:flex;justify-content:center;align-items:center;height:100vh;} canvas{background:#0f172a;border:2px solid #38bdf8;}</style></head><body><canvas id="game" width="400" height="400"></canvas><script>const ctx=document.getElementById("game").getContext("2d");ctx.fillStyle="red";ctx.fillRect(50,50,10,10);</script></body></html>"""
    
    return f"""<!DOCTYPE html><html><head><style>body{{background:#1e293b;color:white;text-align:center;}}</style></head><body><h1>App Gerado Localmente</h1><p>Prompt: {prompt}</p></body></html>"""

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
            js_som = "\\nfunction tocarSom() { var audio = new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA='); audio.play(); }\\n"
            if "</script>" in html_novo:
                html_novo = html_novo.replace("</script>", js_som + "</script>")
            html_novo = html_novo.replace("</body>", "<button onclick='tocarSom()' style='position:fixed; bottom:10px; right:10px;'>Tocar Som</button></body>")
            features_adicionadas.append("som")

    return html_novo, features_adicionadas

def processar_sintese(prompt_usuario, force_create=False):
    db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
    memoria = {}
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            memoria = json.load(f)
        
    chave_alvo = None
    for k in memoria.keys():
        if "velha" in prompt_usuario.lower() and "velha" in k.lower():
            chave_alvo = k
            break
        if "cobra" in prompt_usuario.lower() and "cobra" in k.lower():
            chave_alvo = k
            break
            
    if not chave_alvo:
        if force_create:
            return None, "Precisa criar"
        return None, "Nao encontrado no cache."
        
    entry = memoria[chave_alvo]
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
print("[OK] local_synthesis.py atualizado com Autopoiese.")

# 3. ATUALIZANDO A ROTA NO APP.PY
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_auto_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = 'elif self.path == "/api/generate_cloud":'
start_idx = code.find(start_marker)

if start_idx != -1:
    match_end = code.find('\n    def ', start_idx)
    if match_end == -1: match_end = code.find('\nif __name__', start_idx)
    if match_end == -1: match_end = len(code)

    rota = '''elif self.path == "/api/generate_cloud":
            import time, json
            from intelligence.swarm_engine import disparar_enxame
            from intelligence.dom_parser import ler_miolo
            from intelligence.onnx_bridge import inferir_mutacao, aplicar_mutacoes
            from intelligence.onnx_sovereign import buscar_no_genoma
            from intelligence.local_synthesis import gerar_esqueleto_local, processar_sintese
            
            start_time = time.perf_counter()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return

            # 1. BUSCA SEMANTICA ONNX (CAMINHO C)
            print(f"[ONNX] Buscando correspondencia semantica para: '{prompt[:30]}...'")
            intent_onnx, score = buscar_no_genoma(prompt, cerebro.dynamic_tools)
            
            if intent_onnx and score > 0.4:
                print(f"[ONNX] Match encontrado! Chave: '{intent_onnx}' | Score: {score:.2f}")
                entry = cerebro.dynamic_tools[intent_onnx]
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                
                miolo = ler_miolo(html_atual)
                mutacoes = inferir_mutacao(prompt, miolo)
                
                if mutacoes:
                    print(f"[ONNX] Mutacoes decididas: {len(mutacoes)}")
                    html_evoluido = aplicar_mutacoes(html_atual, mutacoes)
                    
                    # GATE-19: Escrita via servidor
                    cerebro.dynamic_tools[intent_onnx] = {"html": html_evoluido, "features": ["mutacao_onnx"]}
                    with open(cerebro.db_path, "w", encoding="utf-8") as f:
                        json.dump(cerebro.dynamic_tools, f, ensure_ascii=False, indent=2)
                        
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Evolucao aplicada via ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_evoluido, "fonte": "ONNX_MUTACAO_LOCAL", "elapsed_ms": elapsed})
                    return
                else:
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache puro ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_atual, "fonte": "ONNX_CACHE_PURO", "elapsed_ms": elapsed})
                    return

            # 2. SE NAO ACHAR NO ONNX, ENXAME PARALELO
            print(f"[LOCAL] Nenhum match semantico (score: {score:.2f}). Acionando Enxame...")
            resposta_final, fonte = disparar_enxame(prompt, anel)
            
            if resposta_final:
                cerebro.aprender_da_nuvem(prompt, resposta_final)
                print(f"[MEMORIA] Ouro salvo via Enxame.")
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                # 3. AUTOPOIESE (GATE-19: Criacao via Servidor)
                print("[AUTOPOIESE] Nuvem falhou. Criando esqueleto local via API...")
                html_auto = gerar_esqueleto_local(prompt)
                
                # Salva no genoma
                intent_local = prompt.lower().replace(" ", "_")[:20]
                cerebro.dynamic_tools[intent_local] = {"html": html_auto, "features": ["autopoiese"]}
                with open(cerebro.db_path, "w", encoding="utf-8") as f:
                    json.dump(cerebro.dynamic_tools, f, ensure_ascii=False, indent=2)
                    
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                print(f"[AUTOPOIESE] Genoma atualizado via rota HTTP em {elapsed}ms.")
                self._send_json({"status": "success", "html": html_auto, "fonte": "AUTOPOIESE_LOCAL", "elapsed_ms": elapsed})

    '''
    code = code[:start_idx] + rota + code[match_end:]
    print("[OK] Rota /api/generate_cloud atualizada com Autopoiese (GATE-19).")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O Nucleo Neural Soberano esta pronto.")