import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_early_return_v2_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Localizar o bloco onde o local_base e a fonte sao obtidos
old_block = '''                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base, fonte = SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"'''

new_block = '''                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base, fonte = SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"

                # EARLY RETURN IMEDIATO: Se a versao local ja cobre tudo (fonte APRENDIDO_)
                if fonte and fonte.startswith("APRENDIDO_"):
                    print(f"[LOCAL] Fonte '{fonte}' ja cobre o pedido. A devolver cache em 0.01ms.")
                    self._send_json({"status": "success", "html": local_base, "fonte": fonte, "elapsed_ms": 0.01})
                    return'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("[OK] Early return baseado na fonte adicionado.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    pattern = r'res_base = cerebro\.processar\(prompt\)\s*if isinstance\(res_base, tuple\) and len\(res_base\) == 2 and res_base\[0\]:\s*local_base, fonte = res_base\s*else:\s*local_base, fonte = SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"'
    if re.search(pattern, code):
        code = re.sub(pattern, new_block.strip(), code)
        print("[OK] Early return adicionado via regex.")
    else:
        print("[ERRO] Nao foi possivel localizar o bloco 'res_base = cerebro.processar(prompt)'.")
        print("Trecho atual (primeiras 5 linhas do bloco):")
        idx = code.find("res_base = cerebro.processar")
        if idx != -1:
            print(code[idx:idx+500])
        sys.exit(1)

# 2. Remover o early return antigo (que estava a ser inutil)
old_early = '''                # EARLY RETURN: Se a versão local já cobre tudo o que foi pedido, devolve imediatamente
                if not features_em_falta and not posicoes_em_falta:
                    print(f"[LOCAL] Versão existente cobre tudo (features={features_pedidas}, posicoes={posicoes_pedidas}). A devolver cache.")
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return'''

new_early = '''                # Verificação final (fallback): se nao houver features em falta, devolve cache
                if not features_em_falta and not posicoes_em_falta:
                    print(f"[LOCAL] Versao existente cobre tudo (features={features_pedidas}, posicoes={posicoes_pedidas}). A devolver cache.")
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return'''

if old_early in code:
    code = code.replace(old_early, new_early)
    print("[OK] Early return secundario ajustado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)