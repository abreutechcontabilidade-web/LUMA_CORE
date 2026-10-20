import os, re, shutil, glob, py_compile, time

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
backups = sorted(glob.glob(path + ".bak*"), key=os.path.getctime, reverse=True)

restored = False
for bak in backups:
    try:
        with open(bak, "r", encoding="utf-8") as f:
            content = f.read()
        if "_muts" not in content:
            shutil.copy2(bak, path)
            print(f"[OK] app.py restaurado do backup limpo: {bak}")
            restored = True
            break
    except Exception:
        pass

if not restored:
    print("[AVISO] Nenhum backup limpo. Limpando o atual manualmente...")
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    lines = [l for l in code.split('\n') if "_muts" not in l and "# STILB:" not in l and "STILB]" not in l]
    code = '\n'.join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace('intent_web = prompt.lower().replace(" ", "_")[:20]', 'intent_web = chave_limpa.replace(" ", "_")')

if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

code = re.sub(r'"html":\s*(html_atual|codigo_web|fallback_html),', r'"html": aplicar_mutacoes(\1, prompt)[0],', code)

tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(tmp, doraise=True)
    os.replace(tmp, path)
    print("[OK] app.py curado, namespace unificado e injecao inline aplicada.")
except Exception as e:
    os.remove(tmp)
    print(f"[CRITICO] Compilacao falhou: {e}")
    print("O app.py foi mantido no estado atual.")