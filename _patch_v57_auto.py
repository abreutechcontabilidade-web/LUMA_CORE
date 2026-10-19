import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v57_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Localizar o bloco onde local_base/fonte sao obtidos
old_block = """                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base, fonte = SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO\""""

new_block = """                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base, fonte = SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"

                # EARLY RETURN: Se a versao local ja cobre tudo (fonte APRENDIDO_)
                if fonte and isinstance(fonte, str) and fonte.startswith("APRENDIDO_"):
                    print(f"[LOCAL] Fonte '{fonte}' ja cobre o pedido. A devolver cache em 0.01ms.")
                    self._send_json({"status": "success", "html": local_base, "fonte": fonte, "elapsed_ms": 0.01})
                    return"""

if old_block in code:
    code = code.replace(old_block, new_block)
    print("[OK] Early return baseado na fonte adicionado.")
else:
    print("[ERRO] Bloco nao encontrado. O patch nao foi aplicado.")
    sys.exit(1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)