import os, shutil, time, py_compile

# ==========================================
# 1. ATUALIZANDO O ONNX BRIDGE (UI SOTA PARA A COBRA)
# ==========================================
bridge_code = '''
def inferir_mutacao(prompt, miolo):
    p = prompt.lower()
    mutacoes = []
    
    if "cor" in p and "background-color: #8b0000" not in miolo.get("html_bruto", ""):
        mutacoes.append({"tipo": "css", "valor": "body { background-color: #8b0000 !important; color: white; }"})
        
    if "cobra" in p and "snakeGameLoop" not in miolo.get("html_bruto", ""):
        js_cobra = """
        (function() {
            const canvas = document.getElementById('game');
            const snakeCtx = canvas.getContext('2d');
            let snake = [{x: 50, y: 50}, {x: 40, y: 50}, {x: 30, y: 50}];
            let dx = 10, dy = 0;
            let score = 0;
            let gameOver = false;
            
            function snakeGameLoop() {
                if (gameOver) return;
                setTimeout(() => {
                    snakeCtx.fillStyle = '#0f172a';
                    snakeCtx.fillRect(0, 0, 400, 400);
                    
                    const head = {x: snake[0].x + dx, y: snake[0].y + dy};
                    
                    // Colisão com as bordas
                    if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
                        gameOver = true;
                        snakeCtx.fillStyle = 'white';
                        snakeCtx.font = '30px Arial';
                        snakeCtx.fillText('GAME OVER', 120, 200);
                        return;
                    }
                    
                    snake.unshift(head);
                    snake.pop();
                    
                    snakeCtx.fillStyle = '#ef4444';
                    snake.forEach(segment => snakeCtx.fillRect(segment.x, segment.y, 10, 10));
                    
                    snakeGameLoop();
                }, 150);
            }
            
            document.addEventListener('keydown', e => {
                if(e.key === 'ArrowUp' && dy === 0) { dx = 0; dy = -10; }
                if(e.key === 'ArrowDown' && dy === 0) { dx = 0; dy = 10; }
                if(e.key === 'ArrowLeft' && dx === 0) { dx = -10; dy = 0; }
                if(e.key === 'ArrowRight' && dx === 0) { dx = 10; dy = 0; }
            });
            
            snakeGameLoop();
        })();
        """
        mutacoes.append({"tipo": "js", "valor": js_cobra})
        
    return mutacoes

def aplicar_mutacoes(html, mutacoes):
    novo_html = html
    for m in mutacoes:
        if m["tipo"] == "css" and "</style>" in novo_html:
            novo_html = novo_html.replace("</style>", m["valor"] + "</style>")
        if m["tipo"] == "js" and "</script>" in novo_html:
            novo_html = novo_html.replace("</script>", m["valor"] + "</script>")
    return novo_html
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_bridge.py", "w", encoding="utf-8") as f:
    f.write(bridge_code)
print("[OK] onnx_bridge.py atualizado com UI SOTA da Cobra.")

# ==========================================
# 2. CRIANDO O WEB LEARNER (DUCKDUCKGO)
# ==========================================
web_code = '''
import urllib.request
import urllib.parse
import re

def pesquisar_na_web(termo):
    print(f"[WEB LEARNER] Pesquisando no DuckDuckGo: '{termo}'...")
    query = urllib.parse.quote(termo)
    url = f"https://html.duckduckgo.com/html/?q={query}+html+css+js+source+code"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Procura por links de resultados
            links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)"', html)
            if links:
                print(f"[WEB LEARNER] Encontrados {len(links)} links. A descarregar o primeiro...")
                # Pega o primeiro link que parece ser de codigo
                for link in links:
                    if "github" in link or "stackoverflow" in link or "codepen" in link:
                        try:
                            req_code = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req_code, timeout=10) as resp_code:
                                codigo = resp_code.read().decode('utf-8', errors='ignore')
                                # Extrai blocos de codigo (simplificado)
                                if "<html" in codigo.lower() or "<script" in codigo.lower():
                                    return codigo[:5000] # Retorna um excerto
                        except: pass
    except Exception as e:
        print(f"[WEB LEARNER] Erro: {e}")
    return None
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\web_learner.py", "w", encoding="utf-8") as f:
    f.write(web_code)
print("[OK] web_learner.py criado (DuckDuckGo Scraper).")

# ==========================================
# 3. INJETANDO NO APP.PY (Hierarquia de 4 Níveis)
# ==========================================
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_web_" + time.strftime("%Y%m%d_%H%M%S")
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
            import time, json, os
            from intelligence.swarm_engine import disparar_enxame
            from intelligence.dom_parser import ler_miolo
            from intelligence.onnx_bridge import inferir_mutacao, aplicar_mutacoes
            from intelligence.onnx_sovereign import buscar_no_genoma
            from intelligence.local_synthesis import gerar_esqueleto_local
            from intelligence.web_learner import pesquisar_na_web
            
            start_time = time.perf_counter()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return

            # NIVEL 1: ONNX
            print(f"[ONNX] Buscando correspondencia para: '{prompt[:30]}...'")
            intent_onnx, score = buscar_no_genoma(prompt, cerebro.dynamic_tools)
            
            if intent_onnx and score > 0.4:
                print(f"[ONNX] Match! Chave: '{intent_onnx}' | Score: {score:.2f}")
                with open(cerebro.db_path, "r", encoding="utf-8") as f:
                    mem_disco = json.load(f)
                entry = mem_disco.get(intent_onnx, {})
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                
                miolo = ler_miolo(html_atual)
                mutacoes = inferir_mutacao(prompt, miolo)
                
                if mutacoes:
                    print(f"[ONNX] Mutacoes decididas: {len(mutacoes)}")
                    html_evoluido = aplicar_mutacoes(html_atual, mutacoes)
                    features_antigas = entry.get("features", []) if isinstance(entry, dict) else []
                    features_todas = list(set(features_antigas + ["mutacao_onnx"]))
                    mem_disco[intent_onnx] = {"html": html_evoluido, "features": features_todas}
                    
                    tmp_path = cerebro.db_path + ".tmp"
                    with open(tmp_path, "w", encoding="utf-8") as f:
                        json.dump(mem_disco, f, ensure_ascii=False, indent=2)
                    os.replace(tmp_path, cerebro.db_path)
                    cerebro.dynamic_tools = mem_disco
                    
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Evolucao aplicada via ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_evoluido, "fonte": "ONNX_MUTACAO_LOCAL", "elapsed_ms": elapsed})
                    return
                else:
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache puro ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_atual, "fonte": "ONNX_CACHE_PURO", "elapsed_ms": elapsed})
                    return

            # NIVEL 2: ENXAME
            print(f"[LOCAL] Nenhum match. Acionando Enxame...")
            resposta_final, fonte = disparar_enxame(prompt, anel)
            
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                except: pass
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
                return

            # NIVEL 3: WEB LEARNER (DUCKDUCKGO)
            print("[WEB LEARNER] Enxame falhou. A tentar aprender na Web...")
            codigo_web = pesquisar_na_web(prompt)
            
            if codigo_web:
                print("[WEB LEARNER] Codigo encontrado na Web! A salvar no genoma...")
                intent_web = prompt.lower().replace(" ", "_")[:20]
                
                with open(cerebro.db_path, "r", encoding="utf-8") as f:
                    mem_disco = json.load(f)
                mem_disco[intent_web] = {"html": codigo_web, "features": ["aprendido_web"]}
                
                tmp_path = cerebro.db_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(mem_disco, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, cerebro.db_path)
                cerebro.dynamic_tools = mem_disco
                
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": codigo_web, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed})
                return

            # NIVEL 4: AUTOPOIESE (Fallback Final)
            print("[AUTOPOIESE] Tudo falhou. Criando esqueleto local...")
            html_auto = gerar_esqueleto_local(prompt)
            miolo_auto = ler_miolo(html_auto)
            mutacoes_auto = inferir_mutacao(prompt, miolo_auto)
            if mutacoes_auto:
                html_auto = aplicar_mutacoes(html_auto, mutacoes_auto)
            
            intent_local = prompt.lower().replace(" ", "_")[:20]
            with open(cerebro.db_path, "r", encoding="utf-8") as f:
                mem_disco = json.load(f)
            mem_disco[intent_local] = {"html": html_auto, "features": ["autopoiese_evoluida"]}
            
            tmp_path = cerebro.db_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(mem_disco, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, cerebro.db_path)
            cerebro.dynamic_tools = mem_disco
            
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            self._send_json({"status": "success", "html": html_auto, "fonte": "AUTOPOIESE_LOCAL", "elapsed_ms": elapsed})

    '''
    code = code[:start_idx] + rota + code[match_end:]
    print("[OK] Rota atualizada com Web Learner (DuckDuckGo) e Hierarquia de 4 Niveis.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")