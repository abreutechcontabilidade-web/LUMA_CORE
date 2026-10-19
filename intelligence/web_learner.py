
import urllib.request
import json

def pesquisar_na_web(termo):
    print(f"[WEB LEARNER] Pesquisando codigo real para: '{termo}'...")
    t = termo.lower()
    
    # Para jogos classicos, vamos direto a um cofre publico de codigo (GitHub Raw)
    if "cobra" in t or "snake" in t:
        url = "https://raw.githubusercontent.com/CodeExplainedRepo/Snake-Game-JavaScript/master/index.html"
    elif "velha" in t or "tic" in t:
        url = "https://raw.githubusercontent.com/portexe/Tic-Tac-Toe-JS/master/index.html"
    else:
        # Se for algo desconhecido, tenta a API do GitHub
        url = f"https://api.github.com/search/code?q={urllib.parse.quote(termo)}+extension:html"
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('utf-8', errors='ignore')
            
            # Se for a API do GitHub, processa o JSON
            if "api.github.com" in url:
                json_data = json.loads(data)
                if json_data.get("items"):
                    # Pega o primeiro link raw
                    raw_url = json_data["items"][0]["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                    req_raw = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_raw, timeout=10) as resp_raw:
                        return resp_raw.read().decode('utf-8', errors='ignore')
            else:
                # Se for o GitHub Raw direto
                if "<html" in data.lower() or "<script" in data.lower():
                    print("[WEB LEARNER] Codigo de alta qualidade encontrado no GitHub!")
                    return data
    except Exception as e:
        print(f"[WEB LEARNER] Erro ao descarregar da Web: {e}")
    return None
