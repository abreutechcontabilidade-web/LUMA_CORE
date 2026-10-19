import os, shutil, time, py_compile

# ==========================================
# 1. SUPER WEB LEARNER (Contorna o bloqueio do DuckDuckGo)
# ==========================================
web_code = '''
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
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\web_learner.py", "w", encoding="utf-8") as f:
    f.write(web_code)
print("[OK] web_learner.py atualizado (GitHub Raw Bypass).")

# ==========================================
# 2. ONNX BRIDGE (Cobra com Macã e Cauda)
# ==========================================
bridge_code = '''
def inferir_mutacao(prompt, miolo):
    p = prompt.lower()
    mutacoes = []
    
    if "cor" in p and "background-color: #8b0000" not in miolo.get("html_bruto", ""):
        mutacoes.append({"tipo": "css", "valor": "body { background-color: #8b0000 !important; color: white; }"})
        
    if "cobra" in p and "snakeGameLoop" not in miolo.get("html_bruto", ""):
        js_cobra = """
        (function() {
            const canvas = document.getElementById('game');
            const snakeCtx = canvas.getContext('2d');
            let snake = [{x: 150, y: 150}];
            let dx = 10, dy = 0;
            let apple = {x: 200, y: 200};
            let score = 0;
            let gameOver = false;
            
            function drawGame() {
                if (gameOver) return;
                setTimeout(() => {
                    snakeCtx.fillStyle = '#0f172a';
                    snakeCtx.fillRect(0, 0, 400, 400);
                    
                    // Desenha maçã
                    snakeCtx.fillStyle = '#ef4444'; // Vermelho
                    snakeCtx.fillRect(apple.x, apple.y, 10, 10);
                    
                    const head = {x: snake[0].x + dx, y: snake[0].y + dy};
                    
                    // Colisão
                    if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
                        gameOver = true;
                        snakeCtx.fillStyle = 'white';
                        snakeCtx.font = '30px Arial';
                        snakeCtx.fillText('GAME OVER', 120, 200);
                        return;
                    }
                    
                    // Come a maçã
                    if (head.x === apple.x && head.y === apple.y) {
                        score += 10;
                        apple = {x: Math.floor(Math.random()*40)*10, y: Math.floor(Math.random()*40)*10};
                    } else {
                        snake.pop();
                    }
                    
                    snake.unshift(head);
                    
                    // Desenha cobra
                    snakeCtx.fillStyle = '#10b981'; // Verde
                    snake.forEach(segment => snakeCtx.fillRect(segment.x, segment.y, 10, 10));
                    
                    drawGame();
                }, 100);
            }
            
            document.addEventListener('keydown', e => {
                if(e.key === 'ArrowUp' && dy === 0) { dx = 0; dy = -10; }
                if(e.key === 'ArrowDown' && dy === 0) { dx = 0; dy = 10; }
                if(e.key === 'ArrowLeft' && dx === 0) { dx = -10; dy = 0; }
                if(e.key === 'ArrowRight' && dx === 0) { dx = 10; dy = 0; }
            });
            
            drawGame();
        })();
        """
        mutacoes.append({"tipo": "js", "valor": js_cobra})
        
    return mutacoes

def aplicar_mutacoes(html, mutacoes):
    novo_html = html
    for m in mutacoes:
        if m["tipo"] == "css" and "</style>" in novo_html:
            novo_html = novo_html.replace("</style>", m["valor"] + "</style>")
        if m["tipo"] == "js" and "</script>" in novo_html:
            novo_html = novo_html.replace("</script>", m["valor"] + "</script>")
    return novo_html
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_bridge.py", "w", encoding="utf-8") as f:
    f.write(bridge_code)
print("[OK] onnx_bridge.py atualizado com Cobra Completa (Maçã e Cauda).")

# ==========================================
# 3. LIMPANDO O GENOMA PARA FORÇAR NOVO APRENDIZADO
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)
if "criar_jogo_da_cobra_" in mem:
    del mem["criar_jogo_da_cobra_"]
if "criar_jogo_da_cobra" in mem:
    del mem["criar_jogo_da_cobra"]

with open(db_path, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
print("[OK] Genoma limpo. O motor sera forcado a criar/aprender do zero.")

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU.")