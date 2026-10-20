import os, shutil, time, py_compile, re, json

# 1. RESTAURAR O MUTADOR V1.3 (O MEU, SEM CANIBALIZACAO)
mut_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\mutador_local_v1.py"
mut_code = r'''
import re

CORES = {
    "azul": "hue-rotate(180deg) saturate(3) brightness(1.2)",
    "vermelho": "hue-rotate(0deg) saturate(3) brightness(1.2)",
    "verde": "hue-rotate(120deg) saturate(3) brightness(1.2)",
    "roxo": "hue-rotate(270deg) saturate(3) brightness(1.2)",
    "amarelo": "hue-rotate(60deg) saturate(3) brightness(1.2)",
    "rosa": "hue-rotate(300deg) saturate(3) brightness(1.2)"
}

def aplicar_mutacoes(html, prompt):
    p = prompt.lower()
    muts = []
    
    # LIMPEZA FORA DO LOOP (Correcao do CR-71)
    html = re.sub(r'<style id="stilb_mutation_v1">.*?</style>', "", html, flags=re.S)
    html = re.sub(r'<script id="stilb_speed_v1">.*?</script>', "", html, flags=re.S)
    
    cor_escolhida = None
    for nome, filtro in CORES.items():
        if nome in p:
            cor_escolhida = filtro
            muts.append(nome)
            break
            
    if "cyberpunk" in p or "neon" in p:
        if not cor_escolhida:
            cor_escolhida = CORES["rosa"]
            muts.append("cyberpunk")
            
    css_filter = f"filter: {cor_escolhida} !important;" if cor_escolhida else ""
    
    speed_js = ""
    if "velocidade" in p or "rapido" in p:
        muts.append("velocidade")
        speed_js = """
        <script id="stilb_speed_v1">
        (function(){var O=window.setInterval;window.setInterval=function(f,t){
        return O(f,(t>=40&&t<=400)?Math.max(30,Math.round(t*0.6)):t)}})();
        </script>
        """
        
    if not muts:
        return html, muts
        
    css_block = f"""
    <style id="stilb_mutation_v1">
    html,body{{background:#050510 !important;color:#e0f7ff !important}}
    canvas{{background:#0a0a1a !important;border:2px solid #00ffe1 !important; box-shadow:0 0 24px #ff2fd6 !important; {css_filter}}}
    button,.btn{{background:#0a0a1a !important;color:#00ffe1 !important;border:1px solid #ff2fd6 !important}}
    h1,h2,h3,p{{color:#ff2fd6 !important;text-shadow:0 0 10px #ff2fd6 !important}}
    </style>
    """
    
    if "</head>" in html.lower():
        i = html.lower().index("</head>")
        html = html[:i] + css_block + speed_js + html[i:]
    else:
        html = css_block + speed_js + html
        
    return html, muts
'''
with open(mut_path, "w", encoding="utf-8") as f:
    f.write(mut_code)
print("[OK] mutador_local_v1.py v1.3 restaurado (Sem canibalizacao).")

# 2. CIRURGIA NO APP.PY (Injetar STILB no Cache - G-154 Fix)
app_path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = app_path + ".bak_v100_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(app_path, bak)

with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove injeções antigas
code = re.sub(r"\n\s*# --- NIVEL 0\.5 STILB.*?\n\s*print\(f\"\[AVISO\] Erro STILB.*?\)", "", code, flags=re.S)
code = re.sub(r"\n\s*# --- STILB MUTATOR NO CACHE.*?\n\s*print\(f\"\[AVISO\] Erro no mutador STILB.*?\)", "", code, flags=re.S)

# Alvo: logo apos extrair html_atual do cache
target = r"(html_atual = entry\.get\(\"html\", \"\"\) if isinstance\(entry, dict\) else entry)"
match = re.search(target, code)
if match:
    indent = re.search(r"\n(\s+)html_atual", match.group(0))
    # Como o match.group(0) nao tem \n, vamos calcular a indentacao da linha
    linha_inteira = code[code.rfind("\n", 0, match.start())+1 : code.find("\n", match.end())]
    indent = re.match(r"(\s+)", linha_inteira).group(1)
    
    inject = (
        f"\n{indent}# --- NIVEL 0.5 STILB (CTO DECISION) ---"
        f"\n{indent}try:\n"
        f"{indent}    from intelligence.mutador_local_v1 import aplicar_mutacoes\n"
        f"{indent}    html_atual, _muts = aplicar_mutacoes(html_atual, prompt)\n"
        f"{indent}    if _muts:\n"
        f"{indent}        print(f\"[NIVEL 1 STILB] Mutacoes no cache: {{_muts}}\")\n"
        f"{indent}except Exception as e:\n"
        f"{indent}    print(f\"[AVISO] Erro STILB Cache: {{e}}\")"
    )
    code = code.replace(match.group(0), match.group(0) + inject)
    print("[OK] STILB injetado no Cache (Nivel 1) via Regex.")
else:
    print("[ERRO] Alvo do cache nao encontrado.")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(code)

# 3. Limpar o genoma para forcar nova criacao e novo cache
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)
keys_to_remove = [k for k in mem.keys() if "cobr" in k.lower()]
for k in keys_to_remove:
    del mem[k]
tmp = db_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, db_path)
print("[OK] Genoma limpo.")

py_compile.compile(app_path, doraise=True)
print("[OK] py_compile PASSOU. O CTO assumiu o comando.")