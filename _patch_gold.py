import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_gold_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Atualiza o bloco do /api/generate_cloud para garantir o aprendizado
old_cloud = '''                # 5. Guarda na memoria apenas se o codigo base for novo
                if fonte_local == "NUVEM_NECESSARIA":
                    cerebro.aprender_da_nuvem(prompt, final_html)
                    print("[MEMORIA] Novo padrao hibrido guardado.")'''

new_cloud = '''                # 5. GUARDA O OURO NA MEMORIA (Sempre que gerar um codigo valido)
                cerebro.aprender_da_nuvem(prompt, final_html)
                print("[MEMORIA] Ouro guardado na memoria.")'''

if old_cloud in code:
    code = code.replace(old_cloud, new_cloud)
    print("[OK] Logica de aprendizado de ouro aplicada.")
else:
    print("[AVISO] Bloco antigo nao encontrado. Tentando regex...")
    code = re.sub(r'# 5\. Guarda na memoria[\s\S]*?print\("\[MEMORIA\] Novo padrao hibrido guardado\."\)', new_cloud, code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)