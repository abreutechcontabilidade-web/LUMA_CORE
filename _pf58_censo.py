import os, re, hashlib
ROOT = r"C:\Users\user\Desktop\LUMA_CORE"
DEST = r"C:\Users\user\Desktop\stilb_censo_t77.txt"
padroes = [r'extrair_chave', r'aprender_do_github', r'Pesquisando codigo real',
           r'chave_limpa', r'snake game', r'STILB:BOOT_V1', r'STILB:DELIVERY_V3']
alvos, saida = [], []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".venv", "venv", "__pycache__", ".git", "node_modules")]
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        if fn.endswith(".py"):
            alvos.append(("PY", p))
        elif fn.endswith(".json"):
            alvos.append(("JSON", p))
for tipo, p in sorted(alvos):
    try:
        txt = open(p, "r", encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    linhas = txt.splitlines()
    for i, ln in enumerate(linhas, 1):
        if any(re.search(x, ln) for x in padroes):
            saida.append("%s %s:%d: %s" % (tipo, os.path.relpath(p, ROOT), i, ln.strip()[:130]))
    if tipo == "JSON" and re.search(r'jogo_da_cobra|ramazan|snake', txt, re.I):
        m = re.search(r'.{0,60}(jogo_da_cobra|ramazan|snake).{0,60}', txt, re.I | re.S)
        saida.append("GENOMA-HIT " + os.path.relpath(p, ROOT) + ": ..." + (m.group(0) if m else "?") + "...")
app = os.path.join(ROOT, "server", "app.py")
try:
    code = open(app, "r", encoding="utf-8", newline="").read()
    saida.insert(0, "IDENTIDADE app.py sha256[:8]=" + hashlib.sha256(code.encode("utf-8")).hexdigest()[:8])
except Exception as e:
    saida.insert(0, "IDENTIDADE app.py ILEGIVEL: " + repr(e))
open(DEST, "w", encoding="utf-8").write("\n".join(saida))
print("[CENSO-77] %d linhas de evidencia -> " % len(saida) + DEST)
for s in saida[:40]:
    print("  " + s)