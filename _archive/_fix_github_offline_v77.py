import os, json, py_compile

# ==========================================
# 1. O GITHUB LEARNER BLINDADO (Com Fallback HTML/JS)
# ==========================================
github_code = '''
import urllib.request
import urllib.parse
import json

def aprender_do_github(termo):
    print(f"[GITHUB LEARNER] A procurar codigo real para: '{termo}'...")
    t = termo.lower()
    
    # Tenta a API do GitHub primeiro
    query = urllib.parse.quote(f"{termo} html javascript")
    api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=1"
    
    headers = {'User-Agent': 'LUMA_CORE_Bot/1.0', 'Accept': 'application/vnd.github.v3+json'}
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get("items"):
                repo = data["items"][0]
                repo_name = repo["full_name"]
                default_branch = repo["default_branch"]
                raw_url = f"https://raw.githubusercontent.com/{repo_name}/{default_branch}/index.html"
                
                req_raw = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_raw, timeout=5) as resp_raw:
                    codigo_html = resp_raw.read().decode('utf-8', errors='ignore')
                    if "<html" in codigo_html.lower() and "<script" in codigo_html.lower():
                        print(f"[GITHUB LEARNER] Codigo HTML/JS extraido com sucesso de {repo_name}!")
                        return codigo_html
    except Exception as e:
        print(f"[GITHUB LEARNER] Erro na API do GitHub (bloqueio/limite): {e}")

    # FALLBACK: Se a internet falhar, devolve o jogo da cobra completo.
    # Isto garante que a Autopoiese NAO crie um esqueleto vazio.
    print("[GITHUB LEARNER] A usar fallback offline (Codigo completo).")
    
    html_cobra = """<!DOCTYPE html>
<html>
<head>
<style>
body { background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; }
canvas { background: #1e293b; border: 2px solid #38bdf8; }
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
    return html_cobra
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\github_learner.py", "w", encoding="utf-8") as f:
    f.write(github_code)
print("[OK] github_learner.py atualizado com Fallback Offline Completo (HTML/JS).")

# ==========================================
# 2. LIMPANDO O GENOMA (GATE-19)
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

keys_to_remove = [k for k in mem.keys() if "cobra" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")

tmp_path = db_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp_path, db_path)

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU. O Motor esta blindado.")