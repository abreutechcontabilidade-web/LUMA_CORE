import os, shutil, time, py_compile, re, glob

# 1. RESTAURAR O MUTADOR EXATO DA BANCADA (O que funcionou!)
mut_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\mutador_local_v1.py"
mut_code = r'''
import re

PALETA = {
    "#00ff00": "#ff2fd6", "#0f0": "#ff2fd6", 
    "#ff0000": "#00ffe1", "#f00": "#00ffe1", 
    "#cccccc": "#12122b", "#ccc": "#12122b"
}

CSS = (
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
    
    if "cyberpunk" not in p and "neon" not in p and "velocidade" not in p:
        return html, muts
        
    muts.append("cyberpunk")
    
    # Substituicao Cega de Cores (O Segredo da Bancada)
    for s, d in PALETA.items():
        html = re.sub(re.escape(s), d, html, flags=re.I)
        
    # Injetar CSS
    html = re.sub(r'<style id="stilb_mutation_v1">.*?</style>', "", html, flags=re.S)
    i = html.lower().index("</head>") if "</head>" in html.lower() else len(html)
    html = html[:i] + CSS + html[i:]
    
    # Injetar Velocidade
    if "velocidade" in p:
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
print("[OK] mutador_local_v1.py restaurado ao original da Bancada.")

# 2. RESTAURAR O APP.PY (Para limpar os erros de sintaxe)
app_path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
backups = glob.glob(app_path + ".bak_*")
backups.sort(key=os.path.getmtime, reverse=True)

restaurado = False
for b in backups:
    try:
        shutil.copy2(b, app_path)
        py_compile.compile(app_path, doraise=True)
        print(f"[OK] app.py restaurado do backup: {os.path.basename(b)}")
        restaurado = True
        break
    except:
        continue

if not restaurado:
    print("[ERRO FATAL] Nenhum backup compila.")
    exit(1)

with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

# 3. INJETAR O STILB (De forma simples e segura)
target_cache = '''                    entry = memoria.get(intent_onnx, {})
                    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry'''

inject_cache = '''                    entry = memoria.get(intent_onnx, {})
                    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                    
                    try:
                        from intelligence.mutador_local_v1 import aplicar_mutacoes
                        html_atual, _muts = aplicar_mutacoes(html_atual, prompt)
                        if _muts:
                            print("[NIVEL 1 STILB] Mutacoes Cache: " + str(_muts))
                    except Exception as e:
                        print("[AVISO] Erro STILB Cache: " + str(e))'''

if target_cache in code and "NIVEL 1 STILB" not in code:
    code = code.replace(target_cache, inject_cache)
    print("[OK] STILB injetado no Cache (Nivel 1).")

target_web = '''                intent_web = chave_limpa.replace(" ", "_")'''
inject_web = '''                intent_web = chave_limpa.replace(" ", "_")
                
                try:
                    from intelligence.mutador_local_v1 import aplicar_mutacoes
                    codigo_web, _muts = aplicar_mutacoes(codigo_web, prompt)
                    if _muts:
                        print("[NIVEL 1 STILB] Mutacoes Web: " + str(_muts))
                except Exception as e:
                    print("[AVISO] Erro STILB Web: " + str(e))'''

if target_web in code and "Mutacoes Web:" not in code:
    code = code.replace(target_web, inject_web)
    print("[OK] STILB injetado no Web Learner (Nivel 3).")

# Desativar a injeção antiga de fundo vermelho para o neon brilhar
code = code.replace("mutacoes = inferir_mutacao(prompt, miolo)", "mutacoes = []")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(app_path, doraise=True)
print("[OK] py_compile PASSOU. O Servidor esta estavel e mutado.")