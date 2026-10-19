import os, shutil, time, py_compile

# ==========================================
# 1. CONECTOR DIRETO (Wikipedia API Blindada)
# ==========================================
direct_web_code = '''
import urllib.request
import urllib.parse
import json

def ligar_a_web(termo):
    print(f"[DIRECT WEB] A ligar diretamente aos servidores para: '{termo}'...")
    t = termo.lower()
    
    # TRILHA 1: CODIGO (GitHub Raw)
    if "cobra" in t or "snake" in t or "html" in t or "javascript" in t:
        url = "https://raw.githubusercontent.com/CodeExplainedRepo/Snake-Game-JavaScript/master/index.html"
        if "velha" in t: url = "https://raw.githubusercontent.com/portexe/Tic-Tac-Toe-JS/master/index.html"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"[DIRECT WEB] Erro no GitHub: {e}")

    # TRILHA 2: CONHECIMENTO (Wikipedia API Oficial)
    print("[DIRECT WEB] A consultar a API de busca da Wikipedia...")
    try:
        # Limpa o termo
        termo_limpo = t.replace("o que e ", "").replace("quem foi ", "").replace("criar ", "").strip()
        query = urllib.parse.quote(termo_limpo)
        
        # Passo 1: Buscar o ID exato da pagina
        search_url = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=1&format=json"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            search_results = data.get("query", {}).get("search", [])
            
            if not search_results:
                print("[DIRECT WEB] Wikipedia nao tem artigo sobre isto.")
                return None
                
            page_title = search_results[0]["title"]
            print(f"[DIRECT WEB] Artigo encontrado na Wikipedia: '{page_title}'")
            
            # Passo 2: Extrair o texto do artigo
            extract_url = f"https://pt.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&exsectionformat=plain&titles={urllib.parse.quote(page_title)}&format=json"
            req_extract = urllib.request.Request(extract_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            
            with urllib.request.urlopen(req_extract, timeout=10) as resp_ext:
                ext_data = json.loads(resp_ext.read().decode('utf-8'))
                pages = ext_data.get("query", {}).get("pages", {})
                
                for page_id, page_data in pages.items():
                    if "extract" in page_data:
                        resumo = page_data["extract"][:2000]
                        print("[DIRECT WEB] Texto extraido com sucesso!")
                        
                        html_conhecimento = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:40px;max-width:800px;margin:auto;line-height:1.6;}} h1{{color:#38bdf8;border-bottom:1px solid #334155;padding-bottom:10px;}}</style></head><body><h1>{page_title}</h1><p>{resumo}</p><hr><small>Aprendido diretamente da Wikipedia API</small></body></html>"""
                        return html_conhecimento
                        
    except Exception as e:
        print(f"[DIRECT WEB] Erro na Wikipedia: {e}")

    print("[DIRECT WEB] Nenhum resultado encontrado.")
    return None
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\direct_web_connector.py", "w", encoding="utf-8") as f:
    f.write(direct_web_code)
print("[OK] direct_web_connector.py atualizado (Wikipedia API Blindada).")

# ==========================================
# 2. LIMPANDO O GENOMA (Para forçar a busca)
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

# Remove qualquer chave que tenha "dna" ou "o_que_e" para forçar o Web Learner
keys_to_remove = [k for k in mem.keys() if "dna" in k.lower() or "o_que_e" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")

with open(db_path, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU.")