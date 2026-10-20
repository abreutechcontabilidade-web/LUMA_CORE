import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_nivel05_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Importar o mutador no topo do app.py (GATE-23)
if "from intelligence.mutador_local_v1 import aplicar_mutacoes" not in code:
    header = "import sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nfrom intelligence.mutador_local_v1 import aplicar_mutacoes\n"
    code = header + code
    print("[GATE-23] Import do mutador_local_v1 injetado no topo do app.py.")

# 2. Injetar a mutação no Nivel 1 (ONNX Cache)
old_cache = '''                if intent_onnx and score > 0.4:
                    print(f"[ONNX] Match! Chave: '{intent_onnx}' | Score: {score:.2f}")
                    entry = memoria.get(intent_onnx, {})
                    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry'''

new_cache = '''                if intent_onnx and score > 0.4:
                    print(f"[ONNX] Match! Chave: '{intent_onnx}' | Score: {score:.2f}")
                    entry = memoria.get(intent_onnx, {})
                    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                    
                    # --- NIVEL 0.5 STILB (MUTACAO NO CACHE) ---
                    try:
                        html_atual, _muts = aplicar_mutacoes(html_atual, prompt)
                        if _muts:
                            print(f"[NIVEL 0.5 STILB] Mutacoes aplicadas no cache: {_muts}")
                    except Exception as e:
                        print(f"[AVISO] Erro no mutador STILB (Cache): {e}")'''

if old_cache in code:
    code = code.replace(old_cache, new_cache)
    print("[OK] Mutacao STILB injetada no Nivel 1 (ONNX).")
else:
    print("[AVISO] Padrao do Nivel 1 nao encontrado. Verificando...")

# 3. Injetar a mutação no Nivel 3 (Web Learner)
old_web = '''            if codigo_web:
                # G-144 FIX: Usar a mesma chave que o ONNX vai procurar
                intent_web = chave_limpa.replace(" ", "_")'''

new_web = '''            if codigo_web:
                # G-144 FIX: Usar a mesma chave que o ONNX vai procurar
                intent_web = chave_limpa.replace(" ", "_")
                
                # --- NIVEL 0.5 STILB (MUTACAO NO WEB LEARNER) ---
                try:
                    codigo_web, _muts = aplicar_mutacoes(codigo_web, prompt)
                    if _muts:
                        print(f"[NIVEL 0.5 STILB] Mutacoes aplicadas no Web Learner: {_muts}")
                except Exception as e:
                    print(f"[AVISO] Erro no mutador STILB (Web): {e}")'''

if old_web in code:
    code = code.replace(old_web, new_web)
    print("[OK] Mutacao STILB injetada no Nivel 3 (Web Learner).")
else:
    print("[AVISO] Padrao do Nivel 3 nao encontrado. Verificando...")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O Nivel 0.5 esta integrado.")