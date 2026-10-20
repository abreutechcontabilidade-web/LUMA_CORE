import os, shutil, time, py_compile, json

# 1. O MUTADOR V1.3 (Limpeza Fora do Loop + Filtro Dinâmico)
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
    
    # 1. LIMPEZA (Fim da auto-canibalizacao - G-154)
    html = re.sub(r'<style id="stilb_mutation_v1">.*?</style>', "", html, flags=re.S)
    html = re.sub(r'<script id="stilb_speed_v1">.*?</script>', "", html, flags=re.S)
    
    # 2. DETECAO DE COR
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
    
    # 3. DETECAO DE VELOCIDADE
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
print("[OK] mutador_local_v1.py atualizado para v1.3 (Sem canibalizacao).")

# 2. LIMPAR O GENOMA (Para forçar a edição)
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

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