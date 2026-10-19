import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_early_return_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Localizar o bloco de cálculo de features_em_falta
old_calc = '''                features_em_falta = features_pedidas - features_salvas
                posicoes_em_falta = posicoes_pedidas - posicoes_salvas

                if not features_em_falta and not posicoes_em_falta:
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return'''

new_calc = '''                features_em_falta = features_pedidas - features_salvas
                posicoes_em_falta = posicoes_pedidas - posicoes_salvas

                # EARLY RETURN: Se a versão local já cobre tudo o que foi pedido, devolve imediatamente
                if not features_em_falta and not posicoes_em_falta:
                    print(f"[LOCAL] Versão existente cobre tudo (features={features_pedidas}, posicoes={posicoes_pedidas}). A devolver cache.")
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return'''

if old_calc in code:
    code = code.replace(old_calc, new_calc)
    print("[OK] Early return adicionado.")
else:
    print("[AVISO] Padrão antigo não encontrado. Tentando regex...")
    code = re.sub(
        r'if not features_em_falta and not posicoes_em_falta:\s*self\._send_json\(\{"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0\.01\}\)\s*return',
        new_calc.strip(),
        code
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)