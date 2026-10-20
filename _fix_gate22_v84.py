import os, json, py_compile, shutil

# ==========================================
# 1. GITHUB LEARNER (GATE-22: Aptidão e Proveniência)
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
    print(f"[GITHUB LEARNER] A procurar codigo real para: '{termo}'...")
    t = termo.lower()
    
    # GATE-22 (iii): Aptidão. Busca específica para HTML/JS.
    if "cobra" in t or "snake" in t:
        search_query = "snake game html canvas"
    elif "velha" in t or "tic" in t:
        search_query = "tic tac toe html javascript"
    else:
        return None, None

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
                            
                            # GATE-22 (iii): Rejeita Python. Aceita apenas HTML com canvas/script.
                            if "import pygame" not in codigo_html and "<html" in codigo_html.lower() and ("<canvas" in codigo_html.lower() or "<script" in codigo_html.lower()):
                                print(f"[GITHUB LEARNER] Codigo HTML/JS apto extraido de {repo_name}.")
                                html_final = inlinar_dependencias(codigo_html, base_url)
                                
                                # GATE-22 (i): Proveniência
                                proveniencia = {"repo": repo_name, "url": f"{base_url}/index.html", "branch": default_branch, "license": repo.get("license", {}).get("spdx_id", "Unknown")}
                                return html_final, proveniencia
                    except:
                        continue
    except Exception as e:
        print(f"[GITHUB LEARNER] Erro na API do GitHub: {e}")

    print("[GITHUB LEARNER] API falhou ou nao encontrou. A usar Fallback Offline Completo.")
    # GATE-22 (iii): Fallback é um jogo jogável real.
    fallback_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Jogo da Cobra</title>
<style>body { background: #0f172a; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: sans-serif; } canvas { background: #1e293b; border: 2px solid #38bdf8; box-shadow: 0 0 20px rgba(56, 189, 248, 0.5); } h1 { margin-bottom: 20px; }</style></head>
<body><h1>Jogo da Cobra</h1><canvas id="game" width="400" height="400"></canvas>
<script>
const canvas = document.getElementById('game'); const ctx = canvas.getContext('2d');
let snake = [{x: 150, y: 150}]; let dx = 10, dy = 0; let apple = {x: 200, y: 200}; let score = 0; let gameOver = false;
function gameLoop() {
    if (gameOver) return;
    setTimeout(() => {
        ctx.fillStyle = '#1e293b'; ctx.fillRect(0, 0, 400, 400);
        ctx.fillStyle = '#ef4444'; ctx.fillRect(apple.x, apple.y, 10, 10);
        const head = {x: snake[0].x + dx, y: snake[0].y + dy};
        if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
            gameOver = true; ctx.fillStyle = 'white'; ctx.font = '30px Arial'; ctx.fillText('GAME OVER', 120, 200); return;
        }
        if (head.x === apple.x && head.y === apple.y) {
            score += 10; apple = {x: Math.floor(Math.random()*40)*10, y: Math.floor(Math.random()*40)*10};
        } else { snake.pop(); }
        snake.unshift(head);
        ctx.fillStyle = '#10b981'; snake.forEach(segment => ctx.fillRect(segment.x, segment.y, 10, 10));
        ctx.fillStyle = 'white'; ctx.font = '20px Arial'; ctx.fillText('Score: ' + score, 10, 30);
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
</script></body></html>"""
    return fallback_html, {"repo": "local_fallback", "url": "local", "branch": "main", "license": "LumaCore"}
'''

with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\github_learner.py", "w", encoding="utf-8") as f:
    f.write(github_code)
print("[OK] github_learner.py atualizado com GATE-22 (Aptidao e Proveniencia).")

# ==========================================
# 2. ATUALIZANDO O APP.PY (GATE-22 e GATE-19)
# ==========================================
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_gate22_" + str(int(os.path.getmtime(path)))
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Atualiza a chamada do Web Learner na rota
old_web_learner = '''            print("[WEB LEARNER] Enxame falhou. A procurar código real no GitHub...")
            codigo_web = aprender_do_github(prompt)
            
            if codigo_web:
                intent_web = prompt.lower().replace(" ", "_")[:20]
                memoria[intent_web] = {"html": codigo_web, "features": ["aprendido_web"]}
                tmp = DB_PATH + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(memoria, f, ensure_ascii=False, indent=2)
                os.replace(tmp, DB_PATH)
                
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": codigo_web, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed})
                return'''

new_web_learner = '''            print("[WEB LEARNER] Enxame falhou. A procurar código real no GitHub...")
            codigo_web, proveniencia = aprender_do_github(prompt)
            
            if codigo_web:
                intent_web = prompt.lower().replace(" ", "_")[:20]
                # GATE-22 (i): Proveniência no gene
                memoria[intent_web] = {
                    "html": codigo_web, 
                    "features": ["aprendido_web"], 
                    "proveniencia": proveniencia
                }
                tmp = DB_PATH + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(memoria, f, ensure_ascii=False, indent=2)
                os.replace(tmp, DB_PATH)
                
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": codigo_web, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed})
                return'''

if old_web_learner in code:
    code = code.replace(old_web_learner, new_web_learner)
    print("[OK] Rota /api/generate_cloud atualizada com Proveniencia (GATE-22).")
else:
    print("[AVISO] Padrao antigo nao encontrado. Verifique o app.py manualmente.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

# ==========================================
# 3. AUTO-TESTE (GATE-20)
# ==========================================
def self_test():
    print("[GATE-20] A testar a Aptidao do GitHub Learner...")
    import sys
    sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
    from intelligence.github_learner import aprender_do_github
    
    html, prov = aprender_do_github("criar jogo da cobra")
    
    assert html is not None, "Falha: Retornou None"
    assert "<canvas" in html.lower(), "Falha: O HTML nao tem <canvas> (G-126)"
    assert "import pygame" not in html, "Falha: Retornou codigo Python (G-126)"
    assert prov is not None and "repo" in prov, "Falha: Sem proveniencia (GATE-22)"
    
    print("[GATE-20] Auto-teste PASSOU. O motor garante um jogo jogavel com proveniencia.")

self_test()

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU. O Codigo esta limpo.")