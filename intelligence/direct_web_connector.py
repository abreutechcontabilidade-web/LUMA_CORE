
import urllib.request
import urllib.parse
import json

def ligar_a_web(termo):
    print(f"[DIRECT WEB] A ligar diretamente aos servidores para: '{termo}'...")
    t = termo.lower()
    
    # TRILHA 1: CODIGO (GitHub Raw)
    if "cobra" in t or "snake" in t:
        url = "https://raw.githubusercontent.com/CodeExplainedRepo/Snake-Game-JavaScript/master/index.html"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"[DIRECT WEB] Erro no GitHub: {e}")

    # TRILHA 2: CONHECIMENTO (Wikipedia REST API)
    print("[DIRECT WEB] A consultar a API REST da Wikipedia...")
    try:
        termo_limpo = t.replace("o que e ", "").replace("quem foi ", "").replace("criar ", "").strip()
        # A API REST e muito mais simples e nao exige tokens
        api_url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termo_limpo)}"
        
        # User-Agent oficial e obrigatorio pela Wikipedia
        headers = {
            'User-Agent': 'LUMA_CORE_Bot/1.0 (https://github.com/abreutechcontabilidade-web/LUMA_CORE; admin@luma.com)',
            'Accept': 'application/json'
        }
        
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if "extract" in data:
                resumo = data["extract"]
                titulo = data["title"]
                print(f"[DIRECT WEB] Conhecimento extraido da Wikipedia: {titulo}!")
                
                html_conhecimento = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:40px;max-width:800px;margin:auto;line-height:1.6;}} h1{{color:#38bdf8;border-bottom:1px solid #334155;padding-bottom:10px;}}</style></head><body><h1>{titulo}</h1><p>{resumo}</p><hr><small>Aprendido diretamente da Wikipedia REST API</small></body></html>"""
                return html_conhecimento
            else:
                print("[DIRECT WEB] Artigo nao encontrado na Wikipedia.")
                
    except Exception as e:
        print(f"[DIRECT WEB] Erro na Wikipedia: {e}")

    return None
