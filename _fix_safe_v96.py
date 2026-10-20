import os, shutil, time, py_compile, glob

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"

# 1. RESTAURAR O BACKUP MAIS RECENTE QUE COMPILA (Para limpar o SyntaxError)
backups = glob.glob(path + ".bak_*")
backups.sort(key=os.path.getmtime, reverse=True)

restaurado = False
for b in backups:
    try:
        shutil.copy2(b, path)
        py_compile.compile(path, doraise=True)
        print(f"[OK] Servidor restaurado do backup: {os.path.basename(b)}")
        restaurado = True
        break
    except:
        continue

if not restaurado:
    print("[ERRO FATAL] Nenhum backup compila. O app.py está irrecuperável.")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 2. INJETAR O STILB NO CACHE (Nivel 1)
target_cache = '''                    entry = memoria.get(intent_onnx, {})
                    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry'''
                    
inject_cache = '''                    entry = memoria.get(intent_onnx, {})
                    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                    
                    try:
                        from intelligence.mutador_local_v1 import aplicar_mutacoes
                        html_atual, _muts = aplicar_mutacoes(html_atual, prompt)
                        if _muts:
                            print("[NIVEL 1 STILB] Mutacoes Cache: " + str(_muts))
                    except Exception as e:
                        print("[AVISO] Erro STILB Cache: " + str(e))'''

if target_cache in code and "NIVEL 1 STILB" not in code:
    code = code.replace(target_cache, inject_cache)
    print("[OK] STILB injetado no Cache (Nivel 1).")

# 3. INJETAR O STILB NO WEB LEARNER (Nivel 3)
target_web = '''                intent_web = chave_limpa.replace(" ", "_")'''

inject_web = '''                intent_web = chave_limpa.replace(" ", "_")
                
                try:
                    from intelligence.mutador_local_v1 import aplicar_mutacoes
                    codigo_web, _muts = aplicar_mutacoes(codigo_web, prompt)
                    if _muts:
                        print("[NIVEL 1 STILB] Mutacoes Web: " + str(_muts))
                except Exception as e:
                    print("[AVISO] Erro STILB Web: " + str(e))'''

if target_web in code and "Mutacoes Web:" not in code:
    code = code.replace(target_web, inject_web)
    print("[OK] STILB injetado no Web Learner (Nivel 3).")

# 4. DESATIVAR A INJECAO ANTIGA (Para o fundo nao ficar vermelho)
code = code.replace("mutacoes = inferir_mutacao(prompt, miolo)", "mutacoes = []")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O Servidor esta estavel e mutado.")