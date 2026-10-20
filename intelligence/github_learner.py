import urllib.request
import os
import re
from intelligence.github_game_search import search_game_repo, GitHubRateLimitError

ARTEFACTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artefacts")

TERMOS = {
    "jogo_da_cobra": "snake game canvas html5",
    "jogo_da_velha": "tic tac toe game javascript",
    "pong": "pong game javascript canvas",
    "tetris": "tetris game javascript canvas",
    "pacman": "pacman game canvas javascript",
    "calculadora": "calculator web app javascript",
}

def aprender_do_github(chave, prompt=None):
    q = TERMOS.get(chave) or re.sub(r'[^\w\s]', ' ', (prompt or chave))[:60].strip()
    print(f"[GITHUB LEARNER] Chave '{chave}' -> termos: '{q}'")
    try:
        data = search_game_repo(q)
        if not data.get("items"): return None, {"erro": "sem_resultados"}
        
        repo = data["items"][0]
        nome = repo.get("full_name", "")
        branch = repo.get("default_branch", "main")
        print(f"[GITHUB LEARNER] Repositorio: {nome} (branch {branch})")
        
        # G-189: Tratamento de index.html basico
        raw = f"https://raw.githubusercontent.com/{nome}/{branch}/index.html"
        req = urllib.request.Request(raw, headers={'User-Agent': 'LUMA_CORE_Agent'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
            
        # G-190: Salva com a nomenclatura CORRETA do Cache (chave_<chave>.html)
        try:
            os.makedirs(ARTEFACTOS_DIR, exist_ok=True)
            caminho = os.path.join(ARTEFACTOS_DIR, f"chave_{chave}.html")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[GITHUB LEARNER] Salvo no cache correto: chave_{chave}.html")
        except Exception as e:
            print(f"[GITHUB LEARNER] Erro ao salvar cache: {e}")
            
        return html, {"repo": nome}
    except GitHubRateLimitError as e:
        return None, {"erro": "rate_limit"}
    except Exception as e:
        return None, {"erro": repr(e)}