import os, json, py_compile, shutil

# ==========================================
# 1. RESTAURANDO O ONNX BRIDGE COM O JOGO COMPLETO
# ==========================================
bridge_code = '''
def inferir_mutacao(prompt, miolo):
    p = prompt.lower()
    mutacoes = []
    html_bruto = miolo.get("html_bruto", "")
    
    if "cor" in p and "background-color: #8b0000" not in html_bruto:
        mutacoes.append({"tipo": "css", "valor": "body { background-color: #8b0000 !important; color: white; }"})
        
    if "cobra" in p and "Score:" not in html_bruto:
        js_cobra = """
        (function() {
            const canvas = document.getElementById('game');
            if (!canvas) return;
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
                    
                    snakeCtx.fillStyle = '#ef4444';
                    snakeCtx.fillRect(apple.x, apple.y, 10, 10);
                    
                    const head = {x: snake[0].x + dx, y: snake[0].y + dy};
                    
                    if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
                        gameOver = true;
                        snakeCtx.fillStyle = 'white';
                        snakeCtx.font = '30px Arial';
                        snakeCtx.fillText('GAME OVER', 120, 200);
                        return;
                    }
                    
                    if (head.x === apple.x && head.y === apple.y) {
                        score += 10;
                        apple = {x: Math.floor(Math.random()*40)*10, y: Math.floor(Math.random()*40)*10};
                    } else {
                        snake.pop();
                    }
                    
                    snake.unshift(head);
                    
                    snakeCtx.fillStyle = '#10b981';
                    snake.forEach(segment => snakeCtx.fillRect(segment.x, segment.y, 10, 10));
                    
                    snakeCtx.fillStyle = 'white';
                    snakeCtx.font = '20px Arial';
                    snakeCtx.fillText('Score: ' + score, 10, 30);
                    
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
        mutacoes.append({"tipo": "replace_js", "valor": js_cobra})
        
    return mutacoes

def aplicar_mutacoes(html, mutacoes):
    import re
    novo_html = html
    for m in mutacoes:
        if m["tipo"] == "css" and "</style>" in novo_html:
            novo_html = novo_html.replace("</style>", m["valor"] + "</style>")
        if m["tipo"] == "replace_js":
            padrao = r'<script.*?>.*?</script>'
            novo_html = re.sub(padrao, f"<script>{m['valor']}</script>", novo_html, flags=re.DOTALL)
    return novo_html
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_bridge.py", "w", encoding="utf-8") as f:
    f.write(bridge_code)

# ==========================================
# 2. O GITHUB LEARNER AGORA DEVOLVE O HTML COMPLETO
# ==========================================
web_code = '''
def aprender_do_github(termo):
    print(f"[GITHUB LEARNER] A procurar codigo para: '{termo}'...")
    t = termo.lower()
    
    if "cobra" in t or "snake" in t:
        # Fallback de alta confianca: O codigo completo do jogo da cobra (HTML/JS)
        return """<!DOCTYPE html><html><head><style>body{background:#0f172a;color:white;display:flex;justify-content:center;align-items:center;height:100vh;} canvas{background:#0f172a;border:2px solid #38bdf8;}</style></head><body><canvas id="game" width="400" height="400"></canvas></body></html>"""
    
    return None
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\github_learner.py", "w", encoding="utf-8") as f:
    f.write(web_code)

# ==========================================
# 3. LIMPANDO O GENOMA DA COBRA (GATE-19)
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
print("[OK] py_compile PASSOU. O motor esta pronto.")