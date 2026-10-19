import os, shutil, time, py_compile

# ==========================================
# 1. CRIANDO O CONECTOR DIRETO (Wikipedia + GitHub)
# ==========================================
direct_web_code = '''
import urllib.request
import urllib.parse
import json

def ligar_a_web(termo):
    print(f"[DIRECT WEB] A ligar diretamente aos servidores para: '{termo}'...")
    t = termo.lower()
    
    # ==========================================
    # TRILHA 1: CODIGO (GitHub API Direta)
    # ==========================================
    if "cobra" in t or "snake" in t or "html" in t or "css" in t or "javascript" in t:
        url = "https://raw.githubusercontent.com/CodeExplainedRepo/Snake-Game-JavaScript/master/index.html"
        if "velha" in t or "tic" in t:
            url = "https://raw.githubusercontent.com/portexe/Tic-Tac-Toe-JS/master/index.html"
            
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8', errors='ignore')
                if "<html" in data.lower():
                    print("[DIRECT WEB] Codigo encontrado no repositorio GitHub!")
                    return data
        except Exception as e:
            print(f"[DIRECT WEB] Erro no GitHub: {e}")

    # ==========================================
    # TRILHA 2: CONHECIMENTO (Wikipedia API Direta)
    # ==========================================
    print("[DIRECT WEB] A consultar a API da Wikipedia...")
    try:
        # Limpa o termo (remove "o que e", "quem foi", etc)
        termo_limpo = t.replace("o que e ", "").replace("quem foi ", "").replace("criar ", "").strip()
        query = urllib.parse.quote(termo_limpo)
        
        # API Oficial da Wikipedia (Portugues)
        api_url = f"https://pt.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={query}&format=json"
        
        req = urllib.request.Request(api_url, headers={'User-Agent': 'LumaCoreBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1" and "extract" in page_data:
                    resumo = page_data["extract"][:2000] # Limita a 2000 caracteres
                    print(f"[DIRECT WEB] Conhecimento extraido da Wikipedia: {page_data.get('title')}!")
                    
                    # Cria uma pagina HTML bonita
                    html_conhecimento = f"""<!DOCTYPE html><html><head><style>body{{background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:40px;max-width:800px;margin:auto;line-height:1.6;}} h1{{color:#38bdf8;}}</style></head><body><h1>{page_data.get('title')}</h1><p>{resumo}</p><hr><small>Aprendido diretamente da Wikipedia API</small></body></html>"""
                    return html_conhecimento
                    
    except Exception as e:
        print(f"[DIRECT WEB] Erro na Wikipedia: {e}")

    print("[DIRECT WEB] Nenhum resultado encontrado.")
    return None
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\direct_web_connector.py", "w", encoding="utf-8") as f:
    f.write(direct_web_code)
print("[OK] direct_web_connector.py criado (Conexao Direta com a Matriz).")

# ==========================================
# 2. ATUALIZANDO A ROTA NO APP.PY
# ==========================================
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_direct_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o import do web_learner pelo direct_web_connector
code = code.replace(
    "from intelligence.web_learner import pesquisar_na_web",
    "from intelligence.direct_web_connector import ligar_a_web"
)
code = code.replace(
    "from intelligence.web_learner import pesquisar_na_web\n",
    ""
)
# Substitui a chamada da funcao
code = code.replace(
    "codigo_web = pesquisar_na_web(prompt)",
    "codigo_web = ligar_a_web(prompt)"
)
code = code.replace(
    "[WEB LEARNER] Enxame falhou. A tentar aprender na Web...",
    "[DIRECT WEB] Enxame falhou. A ligar diretamente a Web (Wikipedia/GitHub)..."
)
code = code.replace(
    "[WEB LEARNER]",
    "[DIRECT WEB]"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)
print("[OK] Rota /api/generate_cloud atualizada para usar o Direct Web Connector.")

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")