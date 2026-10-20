import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_stilb_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Encontra o bloco do ONNX (Nivel 1) onde o HTML e extraido
old_block = '''                entry = memoria.get(intent_onnx, {})
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry'''

new_block = '''                entry = memoria.get(intent_onnx, {})
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                
                # --- STILB MUTATOR NO CACHE (NIVEL 1) ---
                try:
                    from intelligence.mutador_local_v1 import aplicar_mutacoes
                    html_atual, _muts = aplicar_mutacoes(html_atual, prompt)
                    if _muts:
                        print(f"[NIVEL 1 STILB] Mutacoes aplicadas no cache: {_muts}")
                except Exception as e:
                    print(f"[AVISO] Erro no mutador STILB: {e}")
                # ----------------------------------------'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("[OK] Mutador STILB injetado no Nivel 1 (ONNX Cache).")
else:
    print("[ERRO] Nao foi possivel encontrar o bloco do ONNX. Verifique o app.py manualmente.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")