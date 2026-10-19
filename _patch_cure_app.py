import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_cure_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Importar o cure_engine
if "from intelligence.cure_engine import processar as curar_codigo" not in code:
    code = code.replace(
        "from intelligence.virtual_onnx import VirtualONNX",
        "from intelligence.virtual_onnx import VirtualONNX\nfrom intelligence.cure_engine import processar as curar_codigo, extrair_intencao"
    )

# 2. Usar o cure_engine antes de guardar
old_save = '''                        # 5. GUARDA O OURO NA MEMORIA (Sempre que passar no CISO)
                        cerebro.aprender_da_nuvem(prompt, final_html)
                        print(f"[MEMORIA] Ouro guardado para: '{prompt[:30]}...'")'''

new_save = '''                        # 5. CURADORIA: cura, testa, higieniza e poli antes de guardar
                        print("[CURADORIA] A processar o codigo da Nuvem...")
                        codigo_curado = curar_codigo(final_html)
                        
                        if codigo_curado:
                            # Re-valida o CISO apos a curadoria
                            ok_curado, motivo_curado = WebCISOGate.validar_html(codigo_curado)
                            if ok_curado:
                                cerebro.aprender_da_nuvem(prompt, codigo_curado)
                                print(f"[MEMORIA] Ouro CURADO e guardado para: '{prompt[:30]}...'")
                                final_html = codigo_curado  # Usa o codigo curado na resposta
                            else:
                                print(f"[CURADORIA] Rejeitado pelo CISO apos curadoria: {motivo_curado}")
                        else:
                            print("[CURADORIA] Codigo rejeitado. Nao sera guardado.")'''

if old_save in code:
    code = code.replace(old_save, new_save)
    print("[OK] Cure Engine integrado no app.py.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    pattern = r'# 5\. GUARDA O OURO NA MEMORIA[\s\S]*?print\(f"\[MEMORIA\] Ouro guardado para:.*?"\)'
    code = re.sub(pattern, new_save, code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)