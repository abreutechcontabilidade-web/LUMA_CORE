import glob, hashlib, os, py_compile, re, shutil, sys, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
IMPORT = "from intelligence.mutador_stilb_v1 import aplicar_mutacoes, _stilb_mutar_seguro"

def compila(p):
    try:
        py_compile.compile(p, doraise=True)
        return True
    except Exception:
        return False

def limpa_e_injeta(code):
    eol = "\r\n" if "\r\n" in code else "\n"
    limpas, n_atrib = [], 0
    for ln in code.split(eol):
        if re.search(r'\b_muts\b', ln):
            limpas.append(re.sub(r'^([ \t]*)\S.*$', r'\1pass  # STILB:limpo', ln, count=1)); n_atrib += 1
        elif re.search(r'= aplicar_mutacoes\(|= _stilb_mutar_seguro\(|STILB:DELIVERY_V\d|STILB:limpo|\[AVISO\] Erro STILB Cache', ln):
            limpas.append(re.sub(r'^([ \t]*)\S.*$', r'\1pass  # STILB:limpo', ln, count=1)); n_atrib += 1
        elif 'from intelligence.mutador_stilb_v1 import' in ln:
            continue
        else:
            limpas.append(ln)
    code = eol.join(limpas)
    if IMPORT not in code:
        i = code.find("import json")
        if i == -1: i = code.find("import ")
        if i == -1: return None, 0
        j = code.rfind("\n", 0, i)
        code = code[:j+1] + IMPORT + eol + code[j+1:]
    pat = re.compile(r'^(?P<ind>[ \t]+)self\._send_json\(\{"status": "success", "html": (?P<var>\w+),', re.M)
    hits = list(pat.finditer(code))
    if not hits:
        return None, 0
    def escopo_tem_prompt(pos):
        defs = [m.start() for m in re.finditer(r'(?m)^[ \t]*def ', code)]
        antes = [d for d in defs if d < pos]
        ini = antes[-1] if antes else 0
        depois = [d for d in defs if d > pos]
        fim = depois[0] if depois else len(code)
        return "prompt" in code[ini:fim]
    out, ultimo, n = [], 0, 0
    for m in hits:
        out.append(code[ultimo:m.start()])
        ind, var = m.group("ind"), m.group("var")
        pexpr = "prompt" if escopo_tem_prompt(m.start()) else '""'
        out.append(f"{ind}{var} = _stilb_mutar_seguro({var}, {pexpr})  # STILB:DELIVERY_V3{eol}")
        out.append(m.group(0)); ultimo = m.end(); n += 1
    out.append(code[ultimo:])
    return "".join(out), n

def gravar_se_compila(app_path, cand):
    tmp = app_path + ".cand_tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(cand)
    if not compila(tmp):
        os.remove(tmp)
        return False
    bak = app_path + ".bak_v110_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(app_path, bak)
    os.replace(tmp, app_path)
    return True

# 1. Procura o backup mais limpo (sem aplicar_mutacoes inline)
baks = sorted(glob.glob(APP + ".bak*"), key=os.path.getctime)
limpo = None
for b in baks:
    bc = open(b, "r", encoding="utf-8", newline="").read()
    if "html\": aplicar_mutacoes(" not in bc and "html\": codigo_web" in bc and compila(b):
        limpo = bc
        print(f"[OK] DNA limpo encontrado: {b}")
        break

if not limpo:
    print("[CRITICO] Nenhum backup limpo. Usando o atual.")
    limpo = open(APP, "r", encoding="utf-8", newline="").read()

cand, n = limpa_e_injeta(limpo)
if not cand:
    print("[CRITICO] Falha ao injetar.")
    sys.exit(1)

if gravar_se_compila(APP, cand):
    print(f"[OK] app.py curado com {n} pontos de entrega (GATE-30).")
else:
    print("[CRITICO] Compilacao falhou. app.py intacto.")
    sys.exit(1)