import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_features_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Importar o feature_engine
if "from intelligence.feature_engine import extrair_features, carregar_memoria, guardar_memoria, extrair_intencao" not in code:
    code = code.replace(
        "from intelligence.cure_engine import processar as curar_codigo, extrair_intencao",
        "from intelligence.cure_engine import processar as curar_codigo\nfrom intelligence.feature_engine import extrair_features, carregar_memoria, guardar_memoria, extrair_intencao"
    )
    print("[OK] Import do feature_engine adicionado ao app.py.")

# 2. Substituir a lógica de aprendizado para fazer merge incremental
old_save = '''                        # 5. CURADORIA: cura, testa, higieniza e poli antes de guardar
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

new_save = '''                        # 5. CURADORIA: cura, testa, higieniza e poli antes de guardar
                        print("[CURADORIA] A processar o codigo da Nuvem...")
                        codigo_curado = curar_codigo(final_html)
                        
                        if codigo_curado:
                            # Re-valida o CISO apos a curadoria
                            ok_curado, motivo_curado = WebCISOGate.validar_html(codigo_curado)
                            if ok_curado:
                                # MERGE INCREMENTAL: guarda o HTML e as features
                                intent = extrair_intencao(prompt)
                                features_novas = extrair_features(prompt)
                                
                                # Carrega a memória atual
                                memoria = carregar_memoria(cerebro.db_path)
                                
                                # Se já existe uma entrada para esta intenção, faz merge das features
                                if intent in memoria:
                                    entry_existente = memoria[intent]
                                    if isinstance(entry_existente, dict):
                                        features_existentes = entry_existente.get("features", [])
                                        features_todas = list(set(features_existentes + features_novas))
                                    else:
                                        features_todas = features_novas
                                else:
                                    features_todas = features_novas
                                
                                # Guarda o HTML curado e a lista de features atualizada
                                cerebro.dynamic_tools[intent] = {"html": codigo_curado, "features": features_todas}
                                guardar_memoria(cerebro.db_path, cerebro.dynamic_tools)
                                
                                print(f"[MEMORIA] Ouro CURADO e guardado para: '{prompt[:30]}...' (features: {features_todas})")
                                final_html = codigo_curado  # Usa o codigo curado na resposta
                            else:
                                print(f"[CURADORIA] Rejeitado pelo CISO apos curadoria: {motivo_curado}")
                        else:
                            print("[CURADORIA] Codigo rejeitado. Nao sera guardado.")'''

if old_save in code:
    code = code.replace(old_save, new_save)
    print("[OK] Merge Incremental aplicado no app.py.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    pattern = r'# 5\. CURADORIA: cura, testa, higieniza e poli antes de guardar[\s\S]*?print\("\[CURADORIA\] Codigo rejeitado\. Nao sera guardado\."\)'
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