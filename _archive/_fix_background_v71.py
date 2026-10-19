import os, shutil, time, py_compile

# ==========================================
# 1. CRIANDO O BACKGROUND LEARNER (Consciência Paralela)
# ==========================================
bg_code = '''
import threading
import json
import os
from intelligence.swarm_engine import disparar_enxame
from intelligence.web_learner import pesquisar_na_web

# Lock global para evitar que as threads corrompam o JSON
json_lock = threading.Lock()

def _atualizar_genoma(db_path, intent, novo_html, fonte):
    with json_lock:
        try:
            # Lê do disco para evitar clobber
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    mem = json.load(f)
            else:
                mem = {}
                
            # Se o código novo for diferente do antigo, atualiza
            antigo = mem.get(intent, {}).get("html", "")
            if novo_html and novo_html != antigo:
                if intent not in mem or not isinstance(mem[intent], dict):
                    mem[intent] = {"html": novo_html, "features": ["background_learn"]}
                else:
                    mem[intent]["html"] = novo_html
                    if "background_learn" not in mem[intent].get("features", []):
                        mem[intent].setdefault("features", []).append("background_learn")
                
                tmp_path = db_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(mem, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, db_path) # Escrita Atómica (GATE-19)
                print(f"[BACKGROUND] Genoma evoluido via {fonte} para '{intent}'.")
        except Exception as e:
            print(f"[BACKGROUND] Erro ao atualizar genoma: {e}")

def _tarefa_nuvem(prompt, intent, anel, db_path):
    print(f"[BACKGROUND] Disparando Enxame para evoluir '{intent}'...")
    resposta, fonte = disparar_enxame(prompt, anel)
    if resposta:
        _atualizar_genoma(db_path, intent, resposta, fonte)

def _tarefa_web(prompt, intent, db_path):
    print(f"[BACKGROUND] Pesquisando na Web (DuckDuckGo) para evoluir '{intent}'...")
    codigo_web = pesquisar_na_web(prompt)
    if codigo_web:
        _atualizar_genoma(db_path, intent, codigo_web, "Web Learner")

def aprender_em_segundo_plano(prompt, intent, anel, db_path):
    """
    Dispara a Nuvem e a Web ao mesmo tempo, sem bloquear o servidor.
    """
    t1 = threading.Thread(target=_tarefa_nuvem, args=(prompt, intent, anel, db_path))
    t2 = threading.Thread(target=_tarefa_web, args=(prompt, intent, db_path))
    
    t1.daemon = True
    t2.daemon = True
    
    t1.start()
    t2.start()
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\background_learner.py", "w", encoding="utf-8") as f:
    f.write(bg_code)
print("[OK] background_learner.py criado (Consciência Paralela).")

# ==========================================
# 2. ATUALIZANDO A ROTA NO APP.PY
# ==========================================
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_bg_" + time.strftime("%Y%m%d_%H%M%S")
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
            from intelligence.background_learner import aprender_em_segundo_plano
            
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
                
                # Dispara a Consciencia Paralela (Nuvem + Web) em background
                aprender_em_segundo_plano(prompt, intent_onnx, anel, cerebro.db_path)
                
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

            # NIVEL 2 e 3: ENXAME e WEB (Se nao tiver no cache, espera o resultado)
            print(f"[LOCAL] Nenhum match. Acionando Enxame...")
            resposta_final, fonte = disparar_enxame(prompt, anel)
            
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                except: pass
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
                return

            print("[WEB LEARNER] Enxame falhou. A tentar aprender na Web...")
            from intelligence.web_learner import pesquisar_na_web
            codigo_web = pesquisar_na_web(prompt)
            
            if codigo_web:
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

            # NIVEL 4: AUTOPOIESE
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
    print("[OK] Rota atualizada com Background Learner (Consciencia Paralela).")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")