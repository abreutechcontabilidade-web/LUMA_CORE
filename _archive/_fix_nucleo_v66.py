import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v66_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = 'elif self.path == "/api/generate_cloud":'
start_idx = code.find(start_marker)

if start_idx != -1:
    # O GATE-19 diz que a escrita do genoma é feita AQUI, na rota.
    rota = '''elif self.path == "/api/generate_cloud":
            import time, json
            from intelligence.swarm_engine import disparar_enxame
            from intelligence.dom_parser import ler_miolo
            from intelligence.onnx_bridge import inferir_mutacao, aplicar_mutacoes
            from intelligence.feature_engine import extrair_intencao
            
            start_time = time.perf_counter()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return

            # 1. IDENTIFICAR INTENÇÃO E LER O MIOLO LOCAL
            intent = extrair_intencao(prompt)
            entry = cerebro.dynamic_tools.get(intent)
            
            if entry:
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                print(f"[MIOLO] Lendo arvore do cache para '{intent}'...")
                miolo = ler_miolo(html_atual)
                print(f"[MIOLO] Tags: {miolo['tags']} | Classes: {miolo['classes']}")
                
                # 2. PONTE NEURAL (ONNX)
                mutacoes = inferir_mutacao(prompt, miolo)
                if mutacoes:
                    print(f"[ONNX] Mutacoes decididas: {len(mutacoes)}")
                    html_evoluido = aplicar_mutacoes(html_atual, mutacoes)
                    
                    # GATE-19: A escrita acontece AQUI, dentro do sistema.
                    cerebro.dynamic_tools[intent] = {"html": html_evoluido, "features": ["mutacao_onnx"]}
                    with open(cerebro.db_path, "w", encoding="utf-8") as f:
                        json.dump(cerebro.dynamic_tools, f, ensure_ascii=False, indent=2)
                        
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Evolucao aplicada via ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_evoluido, "fonte": "ONNX_MUTACAO_LOCAL", "elapsed_ms": elapsed})
                    return
                else:
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache puro (sem mutacao necessaria) em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_atual, "fonte": "CACHE_LOCAL_PURO", "elapsed_ms": elapsed})
                    return

            # 3. SE NÃO TIVER NO CACHE, ENXAME PARALELO
            print(f"[LOCAL] '{intent}' nao esta no cache. Acionando Enxame...")
            resposta_final, fonte = disparar_enxame(prompt, anel)
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            
            if resposta_final:
                cerebro.aprender_da_nuvem(prompt, resposta_final)
                print(f"[MEMORIA] Ouro salvo via Enxame.")
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                self._send_json({"status": "error", "message": "Enxame falhou.", "fonte": fonte, "elapsed_ms": elapsed}, 500)

    '''
    
    match_end = code.find('\n    def ', start_idx)
    if match_end == -1: match_end = len(code)
    
    code = code[:start_idx] + rota + code[match_end:]
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("[OK] Nucleo Universal (v66.0) injetado no app.py.")

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. A arquitetura esta compilada.")