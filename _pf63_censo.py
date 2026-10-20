import os, re, hashlib
ROOT = r"C:\Users\user\Desktop\LUMA_CORE"
DEST = r"C:\Users\user\Desktop\stilb_censo_t80.txt"
saida = []
app = os.path.join(ROOT, "server", "app.py")
try:
    code = open(app, "r", encoding="utf-8", newline="").read()
    saida.append("IDENTIDADE app.py sha8=" + hashlib.sha256(code.encode("utf-8")).hexdigest()[:8])
    era = ("V145" if "[V145/BANCADA]" in code else
           "V144" if "[V144/BANCADA]" in code else
           "QUANTUM-v4.0" if "QUANTUM CORE v4.0" in code else
           "AUTONOMOUS-v143" if "AUTONOMOUS CORE" in code else
           "MINIMAL-v137" if "MINIMAL CORE" in code else "DESCONHECIDA")
    saida.append("ERA no disco: " + era)
    for rot, pat in [("extrair_chave", r'def\s+extrair_chave'),
                     ("_gate33_validar", r'def\s+_gate33_validar'),
                     ("fuzzy difflib", r'get_close_matches'),
                     ("decifrador com portao", r'def\s+decifrar_seguro'),
                     ("cache validado", r'def\s+cache_(ler|gravar)'),
                     ("github_learner", r'github_learner'),
                     ("mutador_stilb", r'mutador_stilb|_stilb_mutar_seguro')]:
        saida.append("APP %-26s %s" % (rot, "PRESENTE" if re.search(pat, code) else "AUSENTE"))
except Exception as e:
    saida.append("app.py ILEGIVEL: " + repr(e))
int_dir = os.path.join(ROOT, "intelligence")
if os.path.isdir(int_dir):
    for fn in sorted(os.listdir(int_dir)):
        p = os.path.join(int_dir, fn)
        if os.path.isfile(p):
            try:
                t = open(p, "r", encoding="utf-8", errors="replace").read()
            except Exception:
                t = ""
            if fn == "github_game_search.py":
                saida.append("INT %s: cliente Lovable %s" % (fn, "VIVO (search_game_repo presente)" if "def search_game_repo" in t else "MORTO/AUSENTE"))
            elif fn == "github_learner.py":
                saida.append("INT %s: %s" % (fn, "era V144" if "GATE-32/LEARNER-V144" in t else "era QUANTUM-v4.0 do par" if "Q-NEURAL" in t else "outra era"))
            elif fn == "mutador_stilb_v1.py":
                saida.append("INT %s: _stilb_mutar_seguro %s" % (fn, "PRESENTE" if "_stilb_mutar_seguro" in t else "AUSENTE"))
open(DEST, "w", encoding="utf-8").write("\n".join(saida))
print("[CENSO-80] %d linhas -> " % len(saida) + DEST)
for s in saida:
    print("  " + s)