import os, shutil, time, py_compile

# ==========================================
# 1. O NOVO MUTADOR DINÂMICO (Nível 2.5)
# ==========================================
mut_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\mutador_local_v1.py"

mut_code = r'''
import re

# O Livro de Receitas agora é um Dicionário de Ingredientes (Cores)
CORES = {
    "azul": "#00bfff",
    "vermelho": "#ff0000",
    "verde": "#32cd32",
    "roxo": "#8a2be2",
    "amarelo": "#ffd700",
    "laranja": "#ff8c00",
    "rosa": "#ff69b4",
    "branco": "#ffffff",
    "preto": "#000000"
}

CSS_BASE = (
    '<style id="stilb_mutation_v1">'
    "html,body{background:#050510 !important;color:#e0f7ff !important}"
    "canvas{background:#0a0a1a !important;border:2px solid #00ffe1 !important;"
    "box-shadow:0 0 24px #ff2fd6 !important}"
    "button,.btn{background:#0a0a1a !important;color:#00ffe1 !important;border:1px solid #ff2fd6 !important}"
    "h1,h2,h3,p{color:#ff2fd6 !important;text-shadow:0 0 10px #ff2fd6 !important}"
    "</style>"
)

SPEED = (
    '<script id="stilb_speed_v1">'
    "(function(){var O=window.setInterval;window.setInterval=function(f,t){"
    "return O(f,(t>=40&&t<=400)?Math.max(30,Math.round(t*0.6)):t)}})();"
    "</script>"
)

def aplicar_mutacoes(html, prompt):
    p = prompt.lower()
    muts = []
    
    # 1. Ingestão Dinâmica de Cores
    cor_escolhida = None
    for nome, hex_code in CORES.items():
        if nome in p:
            cor_escolhida = hex_code
            muts.append(nome)
            break
            
    if "cyberpunk" in p and not cor_escolhida:
        cor_escolhida = "#ff2fd6" # A cor padrão do cyberpunk
        muts.append("cyberpunk")

    if cor_escolhida:
        # Substitui o verde/vermelho do jogo pela cor escolhida
        html = re.sub(r"(fillStyle\s*=\s*['\"])(#00ff00|#0f0)(['\"])", r"\g<1>" + cor_escolhida + r"\3", html, flags=re.I)
        # A maçã fica com uma cor complementar (ex: ciano se a cobra for rosa)
        cor_maca = "#00ffe1" if cor_escolhida != "#00ffe1" else "#ff2fd6"
        html = re.sub(r"(fillStyle\s*=\s*['\"])(#ff0000|#f00)(['\"])", r"\g<1>" + cor_maca + r"\3", html, flags=re.I)
        
        # Injetar CSS Base
        html = re.sub(r'<style id="stilb_mutation_v1">.*?</style>', "", html, flags=re.S)
        i = html.lower().index("</head>") if "</head>" in html.lower() else len(html)
        html = html[:i] + CSS_BASE + html[i:]

    # 2. Ingestão Dinâmica de Velocidade
    if "velocidade" in p or "rapido" in p:
        muts.append("velocidade")
        html = re.sub(r'<script id="stilb_speed_v1">.*?</script>', "", html, flags=re.S)
        if "<head" in html.lower():
            j = html.lower().index("<head")
            j = html.index(">", j) + 1
            html = html[:j] + SPEED + html[j:]
        else:
            html = SPEED + html
            
    return html, muts
'''
with open(mut_path, "w", encoding="utf-8") as f:
    f.write(mut_code)
print("[OK] mutador_local_v1.py atualizado para o Nivel 2.5 (Dinamico).")

# ==========================================
# 2. LIMPANDO O GENOMA (Para forçar nova edição)
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
import json

with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

# Remove a chave da cobra para forçar o motor a buscar novamente e aplicar a nova cor
keys_to_remove = [k for k in mem.keys() if "cobr" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")

tmp = db_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, db_path)

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU.")