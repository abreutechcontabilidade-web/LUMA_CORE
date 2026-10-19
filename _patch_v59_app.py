import re, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v59_app_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove o early return cego
early = '''                if fonte and isinstance(fonte, str) and fonte.startswith("APRENDIDO_"):
                    print(f"[LOCAL] Fonte '{fonte}' ja cobre o pedido. A devolver cache em 0.01ms.")
                    self._send_json({"status": "success", "html": local_base, "fonte": fonte, "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)})
                    return'''

if early in code:
    code = code.replace(early, "")
    print("[OK] Early return cego removido.")
else:
    print("[AVISO] Early return nao encontrado (pode ter outro formato).")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)