import hashlib, py_compile, re
APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
code = open(APP, "r", encoding="utf-8", newline="").read()
sha = hashlib.sha256(code.encode("utf-8")).hexdigest()[:8]
try:
    py_compile.compile(APP, doraise=True); st = "COMPILA"
except Exception as e:
    st = "NAO COMPILA: " + str(e)[:80]
print("[CENSO] sha256[:8]=" + sha + " | " + st)
padroes = [r'\b_muts\b', r'aplicar_mutacoes', r'_stilb_mutar_seguro', r'STILB', r'SOTA Clean', r'Servidor v']
linhas = code.splitlines()
saida = ["sha256[:8]=" + sha + " | " + st]
n = 0
for i, ln in enumerate(linhas, 1):
    if any(re.search(p, ln) for p in padroes):
        print(f"{i:5d}: {ln.strip()[:130]}")
        saida.append(f"{i:5d}: {ln.strip()[:130]}")
        n += 1
print("[CENSO] " + str(n) + " linhas vivas de cicatriz/assinatura encontradas.")
open(r"C:\Users\user\Desktop\stilb_censo_t75.txt", "w", encoding="utf-8").write("\n".join(saida))