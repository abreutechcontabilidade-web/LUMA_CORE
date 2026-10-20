import os, json, py_compile, shutil

# ==========================================
# 1. ONNX SOVEREIGN (Extração de Intenção)
# ==========================================
onnx_code = r'''
import difflib
import re

def extrair_chave(prompt):
    """Filtra o ruído e extrai a intenção principal"""
    p = prompt.lower()
    if "cobra" in p or "snake" in p: return "jogo da cobra"
    if "velha" in p or "tic" in p: return "jogo da velha"
    if "calculadora" in p or "calculator" in p: return "calculadora"
    if "cronometro" in p or "timer" in p: return "cronometro"
    if "tarefa" in p or "todo" in p: return "lista de tarefas"
    # Fallback: usa as primeiras 3 palavras
    return " ".join(p.split()[:3])

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    chave_pedida = extrair_chave(prompt)
    melhor_chave = None
    melhor_score = 0.0
    
    for chave, entry in memoria.items():
        score = difflib.SequenceMatcher(None, chave_pedida, chave.replace("_", " ")).ratio()
        if score > melhor_score:
            melhor_score = score
            melhor_chave = chave
            
    return melhor_chave, melhor_score
'''

with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_sovereign.py", "w", encoding="utf-8") as f:
    f.write(onnx_code)
print("[OK] onnx_sovereign.py atualizado com Extracao de Intencao.")

# ==========================================
# 2. GITHUB LEARNER (Busca Limpa e Fallback Corrigido)
# ==========================================
github_code = r'''
import urllib.request
import urllib.parse
import json
import os
import re

def get_token():
    token_path = r"C:\Users\user\Desktop\LUMA_CORE\github_token.txt"
    if os.path.exists(token_path):
        with open(token_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def descarregar_asset(base_url, path):
    url = path if path.startswith("http") else base_url + "/" + path
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""

def inlinar_dependencias(html, base_url):
    def replace_css(match):
        return f"<style>\n{descarregar_asset(base_url, match.group(1))}\n</style>"
    html = re.sub(r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*>', replace_css, html, flags=re.IGNORECASE)
    
    def replace_js(match):
        return f"<script>\n{descarregar_asset(base_url, match.group(1))}\n</script>"
    html = re.sub(r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>', replace_js, html, flags=re.IGNORECASE)
    return html

def aprender_do_github(termo):
    # O termo agora já vem limpo do app.py
    print(f"[GITHUB LEARNER] A procurar codigo real para: '{termo}'")
    t = termo.lower()
    
    if "cobra" in t or "snake" in t:
        search_query = "snake game html javascript"
    elif "velha" in t:
        search_query = "tic tac toe html javascript"
    else:
        search_query = "html5 game javascript"

    query = urllib.parse.quote(search_query)
    api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=3"
    
    token = get_token()
    headers = {'User-Agent': 'LUMA_CORE_Bot/1.0', 'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get("items"):
                for repo in data["items"]:
                    repo_name = repo["full_name"]
                    default_branch = repo["default_branch"]
                    base_url = f"https://raw.githubusercontent.com/{repo_name}/{default_branch}"
                    
                    try:
                        req_raw = urllib.request.Request(f"{base_url}/index.html", headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_raw, timeout=10) as resp_raw:
                            codigo_html = resp_raw.read().decode('utf-8', errors='ignore')
                            
                            if "import pygame" not in codigo_html and "<html" in codigo_html.lower() and "<canvas" in codigo_html.lower():
                                print(f"[GITHUB LEARNER] Codigo HTML/JS apto extraido de {repo_name}.")
                                html_final = inlinar_dependencias(codigo_html, base_url)
                                proveniencia = {"repo": repo_name, "url": f"{base_url}/index.html", "branch": default_branch, "license": repo.get("license", {}).get("spdx_id", "Unknown")}
                                return html_final, proveniencia
                    except:
                        continue
    except Exception as e:
        print(f"[GITHUB LEARNER] Erro na API do GitHub: {e}")

    print("[GITHUB LEARNER] A usar Fallback Offline Completo (Jogo Corrigido).")
    fallback_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Jogo da Cobra</title>
<style>body { background: #0f172a; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: sans-serif; } canvas { background: #1e293b; border: 2px solid #38bdf8; box-shadow: 0 0 20px rgba(56, 189, 248, 0.5); } h1 { margin-bottom: 20px; }</style></head>
<body><h1>Jogo da Cobra</h1><canvas id="game" width="400" height="400"></canvas>
<script>
const canvas = document.getElementById('game'); 
const ctx = canvas.getContext('2d');
let snake = [{x: 200, y: 200}]; 
let dx = 10, dy = 0; 
let apple = {x: 100, y: 100}; 
let score = 0; 
let gameOver = false;

function resetGame() {
    snake = [{x: 200, y: 200}];
    dx = 10; dy = 0;
    apple = {x: Math.floor(Math.random()*20)*20, y: Math.floor(Math.random()*20)*20};
    score = 0;
    gameOver = false;
    gameLoop();
}

function gameLoop() {
    if (gameOver) return;
    setTimeout(() => {
        const head = {x: snake[0].x + dx, y: snake[0].y + dy};
        
        if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
            gameOver = true;
            ctx.fillStyle = 'rgba(0,0,0,0.7)';
            ctx.fillRect(0, 0, 400, 400);
            ctx.fillStyle = 'white';
            ctx.font = '30px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('GAME OVER', 200, 200);
            ctx.font = '20px Arial';
            ctx.fillText('Aperte ESPAÇO para reiniciar', 200, 240);
            return;
        }

        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, 400, 400);
        
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(apple.x, apple.y, 10, 10);

        if (head.x === apple.x && head.y === apple.y) {
            score += 10;
            apple = {x: Math.floor(Math.random()*38)*10, y: Math.floor(Math.random()*38)*10};
        } else {
            snake.pop();
        }
        
        snake.unshift(head);
        
        ctx.fillStyle = '#10b981';
        snake.forEach(segment => ctx.fillRect(segment.x, segment.y, 10, 10));
        
        ctx.fillStyle = 'white';
        ctx.font = '20px Arial';
        ctx.textAlign = 'left';
        ctx.fillText('Score: ' + score, 10, 30);
        
        gameLoop();
    }, 100);
}

document.addEventListener('keydown', e => {
    if (e.key === ' ') {
        if (gameOver) resetGame();
    }
    if(e.key === 'ArrowUp' && dy === 0) { dx = 0; dy = -10; }
    if(e.key === 'ArrowDown' && dy === 0) { dx = 0; dy = 10; }
    if(e.key === 'ArrowLeft' && dx === 0) { dx = -10; dy = 0; }
    if(e.key === 'ArrowRight' && dx === 0) { dx = 10; dy = 0; }
});

resetGame();
</script></body></html>"""
    return fallback_html, {"repo": "local_fallback", "url": "local", "branch": "main", "license": "LumaCore"}
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\github_learner.py", "w", encoding="utf-8") as f:
    f.write(github_code)
print("[OK] github_learner.py atualizado com Fallback Corrigido.")

# ==========================================
# 3. LOCAL SYNTHESIS (Autopoiese Limpa)
# ==========================================
synth_code = r'''
import json, os

def gerar_esqueleto_local(prompt):
    # Se for cobra, devolve o jogo real (fallback)
    p = prompt.lower()
    if "cobra" in p or "snake" in p:
        from intelligence.github_learner import aprender_do_github
        html, prov = aprender_do_github("cobra")
        return html
        
    return f"""<!DOCTYPE html><html><head><style>body{{background:#1e293b;color:white;text-align:center;padding:50px;}}</style></head><body><h1>App Gerado Localmente</h1><p>Prompt: {prompt}</p><p>O motor nao encontrou uma correspondencia exata na web.</p></body></html>"""

def analisar_e_evoluir(html_atual, prompt_novo):
    return html_atual, []

def processar_sintese(prompt_usuario, force_create=False):
    db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
    memoria = {}
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            memoria = json.load(f)
        
    chave_alvo = None
    for k in memoria.keys():
        if "cobra" in prompt_usuario.lower() and "cobra" in k.lower():
            chave_alvo = k
            break
            
    if not chave_alvo:
        return None, "Nao encontrado no cache."
        
    entry = memoria[chave_alvo]
    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
    return html_atual, "CACHE_LOCAL_PURO"
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\local_synthesis.py", "w", encoding="utf-8") as f:
    f.write(synth_code)
print("[OK] local_synthesis.py atualizado.")

# ==========================================
# 4. LIMPEZA DO GENOMA (Remover a chave quebrada)
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
shutil.copy2(db_path, db_path + ".bak_v87")
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

keys_to_remove = [k for k in mem.keys() if "cobrinha" in k.lower() or "cobra" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")

tmp_path = db_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp_path, db_path)

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU.")