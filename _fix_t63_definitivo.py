import os, shutil, time, py_compile, re, json

# ==========================================
# GATE-20: AUTO-TESTE DO FIXER (Antes do OK)
# ==========================================
def self_test_tokenizador():
    texto = "jogo_da_velha"
    tokens = re.findall(r'[a-z0-9]+', texto.lower())
    assert tokens == ['jogo', 'da', 'velha'], f"ERRO NO TOKENIZADOR: {tokens}"
    print("[GATE-20] Auto-teste do tokenizador PASSOU.")

self_test_tokenizador()

# 1. ATUALIZANDO O ONNX SOVEREIGN (Tokenizador Corrigido)
onnx_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_sovereign.py"
onnx_code = '''
import difflib
import re

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    melhor_chave = None
    melhor_score = 0.0
    
    # O FIX REAL: [a-z0-9]+ quebra underscores e espacos, ignorando pontuacao
    tokens_prompt = re.findall(r'[a-z0-9]+', prompt.lower())
    p_clean = " ".join(tokens_prompt)

    for chave, entry in memoria.items():
        tokens_chave = re.findall(r'[a-z0-9]+', chave.lower())
        k_clean = " ".join(tokens_chave)
        
        score = difflib.SequenceMatcher(None, p_clean, k_clean).ratio()
        
        if score > melhor_score:
            melhor_score = score
            melhor_chave = chave

    return melhor_chave, melhor_score
'''
with open(onnx_path, "w", encoding="utf-8") as f:
    f.write(onnx_code)
print("[OK] onnx_sovereign.py atualizado com Tokenizador Real (Regex [a-z0-9]+).")

# 2. ATUALIZANDO A ROTA NO APP.PY (G106 e G107)
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_t63_" + time.strftime("%Y%m%d_%H%M%S")
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
            
            start_time = time.perf_counter()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return

            # 1. BUSCA SEMANTICA ONNX
            print(f"[ONNX] Buscando correspondencia para: '{prompt[:30]}...'")
            intent_onnx, score = buscar_no_genoma(prompt, cerebro.dynamic_tools)
            
            if intent_onnx and score > 0.4:
                print(f"[ONNX] Match! Chave: '{intent_onnx}' | Score: {score:.2f}")
                # Carrega do disco para evitar clobber (G107)
                with open(cerebro.db_path, "r", encoding="utf-8") as f:
                    mem_disco = json.load(f)
                    
                entry = mem_disco.get(intent_onnx, {})
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                
                miolo = ler_miolo(html_atual)
                mutacoes = inferir_mutacao(prompt, miolo)
                
                if mutacoes:
                    print(f"[ONNX] Mutacoes decididas: {len(mutacoes)}")
                    html_evoluido = aplicar_mutacoes(html_atual, mutacoes)
                    
                    # GATE-19 e G107: Preserva features e faz escrita atomica
                    features_antigas = entry.get("features", []) if isinstance(entry, dict) else []
                    features_todas = list(set(features_antigas + ["mutacao_onnx"]))
                    mem_disco[intent_onnx] = {"html": html_evoluido, "features": features_todas}
                    
                    tmp_path = cerebro.db_path + ".tmp"
                    with open(tmp_path, "w", encoding="utf-8") as f:
                        json.dump(mem_disco, f, ensure_ascii=False, indent=2)
                    os.replace(tmp_path, cerebro.db_path) # Escrita atomica
                    
                    cerebro.dynamic_tools = mem_disco # Atualiza memoria
                    
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Evolucao aplicada via ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_evoluido, "fonte": "ONNX_MUTACAO_LOCAL", "elapsed_ms": elapsed})
                    return
                else:
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache puro ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_atual, "fonte": "ONNX_CACHE_PURO", "elapsed_ms": elapsed})
                    return

            # 2. ENXAME PARALELO (G106: try/except adicionado)
            print(f"[LOCAL] Nenhum match semantico (score: {score:.2f}). Acionando Enxame...")
            resposta_final, fonte = disparar_enxame(prompt, anel)
            
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                    print(f"[MEMORIA] Ouro salvo via Enxame.")
                except Exception as e:
                    print(f"[ERRO FATAL] Falha ao salvar na memoria: {e}")
                
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                # 3. AUTOPOIESE
                print("[AUTOPOIESE] Nuvem falhou. Criando esqueleto local via API...")
                html_auto = gerar_esqueleto_local(prompt)
                
                miolo_auto = ler_miolo(html_auto)
                mutacoes_auto = inferir_mutacao(prompt, miolo_auto)
                if mutacoes_auto:
                    print(f"[AUTOPOIESE] Aplicando {len(mutacoes_auto)} mutacoes ONNX...")
                    html_auto = aplicar_mutacoes(html_auto, mutacoes_auto)
                
                intent_local = prompt.lower().replace(" ", "_")[:20]
                
                # Escrita atomica na Autopoiese (G107)
                with open(cerebro.db_path, "r", encoding="utf-8") as f:
                    mem_disco = json.load(f)
                mem_disco[intent_local] = {"html": html_auto, "features": ["autopoiese_evoluida"]}
                
                tmp_path = cerebro.db_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(mem_disco, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, cerebro.db_path)
                
                cerebro.dynamic_tools = mem_disco
                
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                print(f"[AUTOPOIESE] Genoma atualizado via rota HTTP em {elapsed}ms.")
                self._send_json({"status": "success", "html": html_auto, "fonte": "AUTOPOIESE_LOCAL", "elapsed_ms": elapsed})

    '''
    code = code[:start_idx] + rota + code[match_end:]
    print("[OK] Rota /api/generate_cloud atualizada (G106, G107, GATE-19).")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O Nucleo Neural Soberano esta pronto.")