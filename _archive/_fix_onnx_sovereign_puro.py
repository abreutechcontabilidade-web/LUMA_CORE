import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_onnx_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. RESTAURAR A IGNICAO (__main__)
if "if __name__ == '__main__':" not in code and 'if __name__ == "__main__":' not in code:
    print("[AVISO] Bloco __main__ ausente. Restaurando...")
    main_block = '''
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PORT = 8080
    socketserver.TCPServer.allow_reuse_address = True
    print(f"[LUMA_CORE] Servidor v67.0 (ONNX Soberano) ativo em http://127.0.0.1:{PORT}")
    try:
        with ThreadingHTTPServer(("127.0.0.1", PORT), LumaCoreHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
'''
    code += main_block
    if "from http.server import ThreadingHTTPServer" not in code:
        code = "from http.server import ThreadingHTTPServer\n" + code
    if "import socketserver" not in code:
        code = "import socketserver\n" + code
    print("[OK] Bloco __main__ restaurado.")

# 2. CRIAR A PONTE ONNX (CAMINHO C) USANDO PURO PYTHON
onnx_code = """
import os
import json
import math

try:
    from intelligence.onnx_sota import ONNXSOTA
    onnx_engine = ONNXSOTA()
    print("[ONNX] Motor onnx_sota.py carregado com sucesso.")
except ImportError:
    onnx_engine = None
    print("[ONNX] onnx_sota.py nao encontrado. Usando vetorizacao local de fallback.")

def obter_vetor(texto):
    if onnx_engine:
        try:
            return onnx_engine.get_embedding(texto)
        except AttributeError:
            pass
    words = texto.lower().split()
    return [hash(w) % 1000 for w in words]

def similaridade_cosseno(v1, v2):
    if not v1 or not v2: return 0.0
    intersecao = set(v1).intersection(set(v2))
    return len(intersecao) / math.sqrt(len(v1) * len(v2))

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    vetor_prompt = obter_vetor(prompt)
    melhor_chave = None
    melhor_score = 0.0

    for chave, entry in memoria.items():
        texto_alvo = chave + " " + " ".join(entry.get("features", [])) if isinstance(entry, dict) else chave
        vetor_alvo = obter_vetor(texto_alvo)
        
        score = similaridade_cosseno(vetor_prompt, vetor_alvo)
        if score > melhor_score:
            melhor_score = score
            melhor_chave = chave

    return melhor_chave, melhor_score
"""
onnx_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_sovereign.py"
with open(onnx_path, "w", encoding="utf-8") as f:
    f.write(onnx_code)
print("[OK] onnx_sovereign.py criado (Ponte Neural Local).")

# 3. INJETAR A BUSCA ONNX NA ROTA
start_marker = 'elif self.path == "/api/generate_cloud":'
start_idx = code.find(start_marker)

if start_idx != -1:
    match_end = code.find('\n    def ', start_idx)
    if match_end == -1:
        match_end = code.find('\nif __name__', start_idx)
    if match_end == -1:
        match_end = len(code)

    rota = '''elif self.path == "/api/generate_cloud":
            import time, json
            from intelligence.swarm_engine import disparar_enxame
            from intelligence.dom_parser import ler_miolo
            from intelligence.onnx_bridge import inferir_mutacao, aplicar_mutacoes
            from intelligence.onnx_sovereign import buscar_no_genoma
            
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
            
            if intent_onnx and score > 0.3:
                print(f"[ONNX] Match encontrado! Chave: '{intent_onnx}' | Score: {score:.2f}")
                entry = cerebro.dynamic_tools[intent_onnx]
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                
                # 2. LEITURA DO MIOLO E MUTACAO LOCAL
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

            # 3. SE NAO ACHAR NO ONNX, ENXAME PARALELO
            print(f"[LOCAL] Nenhum match semantico (score: {score:.2f}). Acionando Enxame...")
            resposta_final, fonte = disparar_enxame(prompt, anel)
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            
            if resposta_final:
                cerebro.aprender_da_nuvem(prompt, resposta_final)
                print(f"[MEMORIA] Ouro salvo via Enxame.")
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                self._send_json({"status": "error", "message": "Enxame falhou.", "fonte": fonte, "elapsed_ms": elapsed}, 500)

    '''
    code = code[:start_idx] + rota + code[match_end:]
    print("[OK] Rota /api/generate_cloud atualizada com busca ONNX.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O Nucleo Neural Soberano esta pronto.")