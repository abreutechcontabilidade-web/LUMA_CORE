import os, shutil, time, py_compile, json

# ==========================================
# 1. CRIANDO O GITHUB LEARNER
# ==========================================
github_code = '''
import urllib.request
import urllib.parse
import json

def aprender_do_github(termo):
    print(f"[GITHUB LEARNER] A procurar codigo real para: '{termo}'...")
    t = termo.lower()
    
    # Vamos usar a API de busca do GitHub para encontrar repositorios
    query = urllib.parse.quote(f"{termo} html javascript")
    api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=1"
    
    headers = {
        'User-Agent': 'LUMA_CORE_Bot/1.0',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get("items"):
                repo = data["items"][0]
                repo_name = repo["full_name"]
                default_branch = repo["default_branch"]
                print(f"[GITHUB LEARNER] Repositorio encontrado: {repo_name}")
                
                # Tenta descarregar o index.html (o padrao da maioria dos jogos web)
                raw_url = f"https://raw.githubusercontent.com/{repo_name}/{default_branch}/index.html"
                
                req_raw = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_raw, timeout=10) as resp_raw:
                    codigo_html = resp_raw.read().decode('utf-8', errors='ignore')
                    
                    if "<html" in codigo_html.lower() and "<script" in codigo_html.lower():
                        print(f"[GITHUB LEARNER] Codigo HTML/JS extraido com sucesso de {repo_name}!")
                        return codigo_html
    except Exception as e:
        print(f"[GITHUB LEARNER] Erro na API do GitHub: {e}")
        
    # Fallback para repositorios de alta confianca (se a API falhar ou der rate limit)
    print("[GITHUB LEARNER] A usar fallback de alta confianca...")
    fallbacks = {
        "cobra": "https://raw.githubusercontent.com/CodeExplainedRepo/Snake-Game-JavaScript/master/index.html",
        "velha": "https://raw.githubusercontent.com/portexe/Tic-Tac-Toe-JS/master/index.html"
    }
    for k, v in fallbacks.items():
        if k in t:
            try:
                req = urllib.request.Request(v, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.read().decode('utf-8', errors='ignore')
            except: pass

    return None
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\github_learner.py", "w", encoding="utf-8") as f:
    f.write(github_code)
print("[OK] github_learner.py criado.")

# ==========================================
# 2. LIMPANDO O ONNX BRIDGE (Sem o meu codigo da cobra)
# ==========================================
bridge_code = '''
def inferir_mutacao(prompt, miolo):
    p = prompt.lower()
    mutacoes = []
    html_bruto = miolo.get("html_bruto", "")
    
    # Apenas mutacao de cor (basico)
    if "cor" in p and "background-color: #8b0000" not in html_bruto:
        mutacoes.append({"tipo": "css", "valor": "body { background-color: #8b0000 !important; color: white; }"})
        
    # REMOVIDO: O codigo hardcoded da cobra. O Web Learner deve trazer o jogo real.
    return mutacoes

def aplicar_mutacoes(html, mutacoes):
    novo_html = html
    for m in mutacoes:
        if m["tipo"] == "css" and "</style>" in novo_html:
            novo_html = novo_html.replace("</style>", m["valor"] + "</style>")
    return novo_html
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_bridge.py", "w", encoding="utf-8") as f:
    f.write(bridge_code)
print("[OK] onnx_bridge.py limpo. O 'blueprint' do CTO foi removido.")

# ==========================================
# 3. INTEGRANDO NA ROTA DO APP.PY
# ==========================================
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_gh_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Troca o import e a chamada do direct_web para o github_learner
code = code.replace(
    "from intelligence.direct_web_connector import ligar_a_web",
    "from intelligence.github_learner import aprender_do_github"
)
code = code.replace(
    "codigo_web = ligar_a_web(prompt)",
    "codigo_web = aprender_do_github(prompt)"
)
code = code.replace(
    "[DIRECT WEB] Enxame falhou. A ligar diretamente a Web...",
    "[GITHUB LEARNER] Enxame falhou. A procurar codigo real no GitHub..."
)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)
print("[OK] Rota /api/generate_cloud integrada com o GitHub Learner.")

# ==========================================
# 4. LIMPANDO O GENOMA DA COBRA
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

keys_to_remove = [k for k in mem.keys() if "cobra" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")

with open(db_path, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")