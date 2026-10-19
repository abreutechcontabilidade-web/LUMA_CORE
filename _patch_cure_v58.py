import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_cure_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remover o early return quebrado que ignorava as features em falta
broken_early = """                # EARLY RETURN: Se a versao local ja cobre tudo (fonte APRENDIDO_)
                if fonte and isinstance(fonte, str) and fonte.startswith("APRENDIDO_"):
                    print(f"[LOCAL] Fonte '{fonte}' ja cobre o pedido. A devolver cache em 0.01ms.")
                    self._send_json({"status": "success", "html": local_base, "fonte": fonte, "elapsed_ms": 0.01})
                    return"""

if broken_early in code:
    code = code.replace(broken_early, "")
    print("[OK] Early return quebrado removido (Fixes G64).")
else:
    print("[AVISO] Early return quebrado nao encontrado. Pode ja ter sido removido.")

# 2. Substituir qualquer "elapsed_ms": 0.01 restante por um calculo real
# O t0 ja esta definido no inicio da rota no patch anterior.
old_cache_return = 'self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})'
new_cache_return = '''elapsed = round((time.perf_counter() - t0) * 1000, 2)
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": elapsed})'''

if old_cache_return in code:
    code = code.replace(old_cache_return, new_cache_return)
    print("[OK] Tempo do cache substituido por perf_counter (Fixes G63).")

# Substituir qualquer outro 0.01 por seguranca
if '"elapsed_ms": 0.01' in code:
    code = code.replace('"elapsed_ms": 0.01', '"elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)')
    print("[OK] Outros tempos 0.01 substituidos.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py curado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)