
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
    if path.startswith("http"):
        url = path
    else:
        url = base_url + "/" + path
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[GITHUB LEARNER] Erro ao descarregar asset {path}: {e}")
        return ""

def inlinar_dependencias(html, base_url):
    print("[GITHUB LEARNER] A inlinar CSS e JS externos...")
    
    def replace_css(match):
        href = match.group(1)
        css = descarregar_asset(base_url, href)
        return f"<style>\n{css}\n</style>"
    html = re.sub(r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*>', replace_css, html, flags=re.IGNORECASE)
    
    def replace_js(match):
        src = match.group(1)
        js = descarregar_asset(base_url, src)
        return f"<script>\n{js}\n</script>"
    html = re.sub(r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>', replace_js, html, flags=re.IGNORECASE)
    
    return html

def aprender_do_github(termo):
    print(f"[GITHUB LEARNER] A procurar codigo real para: '{termo}'...")
    t = termo.lower()
    
    if "cobra" in t or "snake" in t:
        search_query = "snake game html javascript"
    elif "velha" in t or "tic" in t:
        search_query = "tic tac toe html javascript"
    else:
        search_query = "html javascript game"
        
    query = urllib.parse.quote(search_query)
    api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=1"
    
    token = get_token()
    headers = {'User-Agent': 'LUMA_CORE_Bot/1.0', 'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        print("[GITHUB LEARNER] A usar Token de autenticacao (API Liberada).")
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get("items"):
                repo = data["items"][0]
                repo_name = repo["full_name"]
                default_branch = repo["default_branch"]
                print(f"[GITHUB LEARNER] Repositorio encontrado: {repo_name}")
                
                base_url = f"https://raw.githubusercontent.com/{repo_name}/{default_branch}"
                raw_url = f"{base_url}/index.html"
                
                req_raw = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_raw, timeout=10) as resp_raw:
                    codigo_html = resp_raw.read().decode('utf-8', errors='ignore')
                    
                    if "import pygame" in codigo_html:
                        print("[GITHUB LEARNER] Rejeitado: Encontrado codigo Python em vez de HTML.")
                    elif "<html" in codigo_html.lower() and ("<canvas" in codigo_html.lower() or "<script" in codigo_html.lower()):
                        print(f"[GITHUB LEARNER] Codigo HTML/JS apto extraido de {repo_name}.")
                        codigo_html = inlinar_dependencias(codigo_html, base_url)
                        return codigo_html
    except Exception as e:
        print(f"[GITHUB LEARNER] Erro na API do GitHub: {e}")

    print("[GITHUB LEARNER] A usar fallback offline completo (HTML/JS).")
    # Fallback Garantido: Jogo da Cobra Completo em um unico ficheiro
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Jogo da Cobra</title>
<style>
body { background: #0f172a; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: sans-serif; }
canvas { background: #1e293b; border: 2px solid #38bdf8; box-shadow: 0 0 20px rgba(56, 189, 248, 0.5); }
h1 { margin-bottom: 20px; }
</style>
</head>
<body>
<h1>Jogo da Cobra</h1>
<canvas id="game" width="400" height="400"></canvas>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let snake = [{x: 150, y: 150}];
let dx = 10, dy = 0;
let apple = {x: 200, y: 200};
let score = 0;
let gameOver = false;

function gameLoop() {
    if (gameOver) return;
    setTimeout(() => {
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, 400, 400);
        
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(apple.x, apple.y, 10, 10);
        
        const head = {x: snake[0].x + dx, y: snake[0].y + dy};
        
        if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
            gameOver = true;
            ctx.fillStyle = 'white';
            ctx.font = '30px Arial';
            ctx.fillText('GAME OVER', 120, 200);
            return;
        }
        
        if (head.x === apple.x && head.y === apple.y) {
            score += 10;
            apple = {x: Math.floor(Math.random()*40)*10, y: Math.floor(Math.random()*40)*10};
        } else {
            snake.pop();
        }
        
        snake.unshift(head);
        
        ctx.fillStyle = '#10b981';
        snake.forEach(segment => ctx.fillRect(segment.x, segment.y, 10, 10));
        
        ctx.fillStyle = 'white';
        ctx.font = '20px Arial';
        ctx.fillText('Score: ' + score, 10, 30);
        
        gameLoop();
    }, 100);
}

document.addEventListener('keydown', e => {
    if(e.key === 'ArrowUp' && dy === 0) { dx = 0; dy = -10; }
    if(e.key === 'ArrowDown' && dy === 0) { dx = 0; dy = 10; }
    if(e.key === 'ArrowLeft' && dx === 0) { dx = -10; dy = 0; }
    if(e.key === 'ArrowRight' && dx === 0) { dx = 10; dy = 0; }
});

gameLoop();
</script>
</body>
</html>"""
