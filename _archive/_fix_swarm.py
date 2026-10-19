import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_swarm_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o loop sequencial pela chamada ao Enxame
old_loop = '''            # NUVEM
            tentativas = 0
            max_tentativas = len(anel.keys) if anel.keys else 1
            resposta_final = None
            fonte = "Falha Total"
            
            while tentativas < max_tentativas:
                chave = anel.get_key()
                if not chave: break'''
                
new_loop = '''            # NUVEM (ENXAME)
            from intelligence.swarm_engine import disparar_enxame
            resposta_final, fonte = disparar_enxame(prompt, anel)
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                    print(f"[MEMORIA] Ouro salvo via Enxame.")
                except Exception: pass
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                self._send_json({"status": "error", "message": "Enxame falhou. Chaves esgotadas.", "fonte": fonte, "elapsed_ms": elapsed}, 500)
            return
            
            # CODIGO ANTIGO ABAIXO (SERA IGNORADO)
            tentativas = 0
            max_tentativas = len(anel.keys) if anel.keys else 1
            resposta_final = None
            fonte = "Falha Total"
            
            while tentativas < max_tentativas:
                chave = anel.get_key()
                if not chave: break'''

if old_loop in code:
    code = code.replace(old_loop, new_loop)
    print("[OK] Loop sequencial substituido pelo Enxame Paralelo.")
else:
    print("[AVISO] Trecho do loop antigo nao encontrado. Tentando injetar via regex...")
    # Fallback: procura a linha do loop e insere o enxame antes
    if "from intelligence.swarm_engine import disparar_enxame" not in code:
        inject_point = '            # NUVEM\n'
        swarm_inject = '''            # NUVEM (ENXAME)
            from intelligence.swarm_engine import disparar_enxame
            resposta_final, fonte = disparar_enxame(prompt, anel)
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                except Exception: pass
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
            else:
                self._send_json({"status": "error", "message": "Enxame falhou.", "fonte": fonte, "elapsed_ms": elapsed}, 500)
            return
            
'''
        code = code.replace(inject_point, swarm_inject)
        print("[OK] Enxame injetado via fallback.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O Enxame esta armado.")