import http.server, socketserver, json, os, sys, re, time, shutil, difflib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from intelligence.sintetizador_local import sintetizar_jogo
    from intelligence.orquestrador import similaridade_cosseno, analisar_dna, classificar_intencao
except ImportError as e:
    print(f"[BOOT ERROR] {e}"); sys.exit(1)

PORT = int(os.environ.get("PORT", 8080))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTEFACTOS_DIR = os.path.join(ROOT_DIR, "intelligence", "artefacts")

CHAVES = [
    ("jogo_da_velha", ("jogo da velha", "tic tac toe")),
    ("jogo_da_cobra", ("cobra", "snake")),
    ("pong", ("pong", "raquete")),
    ("tetris", ("tetris",)),
    ("pacman", ("pacman",)),
    ("breakout", ("breakout", "tijolos", "tijolo")),
    ("space", ("space", "nave")),
    ("corrida", ("corrida", "race", "carro")),
    ("metroid", ("metroid", "plataforma", "mario", "tiro")),
    ("rpg", ("rpg", "texto")),
    ("memoria", ("memoria", "memory")),
    ("tower", ("tower", "defesa")),
    ("velha_ia", ("velha ia", "minimax")),
    ("calculadora", ("calculadora", "calculator")),
]

def extrair_chave(prompt):
    p = (prompt or "").lower()
    for chave, marcas in CHAVES:
        for m in marcas:
            if re.search(r"(?<![a-z0-9])" + re.escape(m) + r"s?(?![a-z0-9])", p): return chave
    universo = {}
    for chave, ws in CHAVES:
        for w in ws: universo[w] = chave
    for w in re.findall(r'[a-z0-9]+', p):
        m = difflib.get_close_matches(w, list(universo.keys()), n=1, cutoff=0.75)
        if m and abs(len(w) - len(m[0])) <= 1: return universo[m[0]]
    return ""

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args): return

    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        if path.startswith("/artefacts/"):
            filename = path.replace("/artefacts/", "")
            return os.path.join(ARTEFACTOS_DIR, filename)
        return super().translate_path(path)
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        if self.path == "/api/status":
            self._send_json({"status": "LUMA_CORE v158 (Dashboard)", "services": ["games", "dna", "recommendation"]}); return
        
        if self.path == "/" or self.path == "/hub":
            try: arquivos = [f for f in os.listdir(ARTEFACTOS_DIR) if f.startswith("chave_") and f.endswith(".html")]
            except Exception: arquivos = []
            
            cards = "".join([f'<div class="card"><h2>{f.replace("chave_","").replace(".html","").title()}</h2><a href="/artefacts/{f}" target="_blank">JOGAR</a></div>' for f in arquivos])
            
            hub = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><title>LUMA_CORE // DASHBOARD</title>
<style>
    body {{ background: #050510; color: #00ffe1; font-family: 'Courier New', monospace; padding: 30px; }}
    h1 {{ color: #ff2fd6; text-shadow: 0 0 20px #ff2fd6; text-align: center; }}
    h2 {{ color: #ff2fd6; border-bottom: 1px solid #ff2fd6; padding-bottom: 5px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
    .panel {{ border: 2px solid #00ffe1; padding: 20px; background: #0a0a1a; box-shadow: 0 0 10px rgba(0,255,225,0.2); }}
    textarea, input {{ width: 100%; background: #050510; color: #00ffe1; border: 1px solid #00ffe1; padding: 10px; margin: 10px 0; font-family: monospace; }}
    button {{ background: #00ffe1; color: #000; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; }}
    button:hover {{ background: #ff2fd6; color: #fff; }}
    .result {{ margin-top: 15px; padding: 10px; border-left: 4px solid #ff2fd6; background: rgba(255,47,214,0.1); }}
    .arcade-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
    .card {{ border: 1px solid #00ffe1; padding: 15px; text-align: center; }}
    .card a {{ color: #000; background: #00ffe1; padding: 5px 10px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }}
</style>
</head>
<body>
    <h1>LUMA_CORE UNIFIED DASHBOARD</h1>
    
    <div class="grid">
        <!-- DNA ENGINE -->
        <div class="panel">
            <h2>CPF ArbÃ³reo // AnÃ¡lise GenÃ©tica</h2>
            <textarea id="dnaInput" rows="3" placeholder="Cole a sequÃªncia (ex: ATGCGATCGTAGCT..."></textarea>
            <button onclick="analisarDNA()">Analisar SequÃªncia</button>
            <div id="dnaResult" class="result">Aguardando...</div>
        </div>

        <!-- RECOMMENDATION ENGINE -->
        <div class="panel">
            <h2>Spotify Engine // Similaridade Cosseno</h2>
            <input type="text" id="v1" placeholder="Vetor 1 (ex: 1, 2, 3)">
            <input type="text" id="v2" placeholder="Vetor 2 (ex: 2, 3, 4)">
            <button onclick="calcularSim()">Calcular Similaridade</button>
            <div id="simResult" class="result">Aguardando...</div>
        </div>
    </div>

    <!-- ARCADE -->
    <h2 style="margin-top: 40px;">Arcade Local // Sintetizador</h2>
    <div class="arcade-grid">
        {cards}
    </div>

<script>
    async function analisarDNA() {{
        const seq = document.getElementById('dnaInput').value;
        const res = await fetch('/api/dna', {{
            method: 'POST', headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{sequencia: seq}})
        }});
        const data = await res.json();
        if(data.status === 'success') {{
            document.getElementById('dnaResult').innerHTML = `
                <b>Tamanho:</b> ${{data.resultado.tamanho}} bp<br>
                <b>GC Content:</b> ${{data.resultado.gc_percent}}%<br>
                <b>AT Content:</b> ${{data.resultado.at_percent}}%`;
        }}
    }}

    async function calcularSim() {{
        const v1 = document.getElementById('v1').value.split(',').map(Number);
        const v2 = document.getElementById('v2').value.split(',').map(Number);
        const res = await fetch('/api/recommend', {{
            method: 'POST', headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{v1: v1, v2: v2}})
        }});
        const data = await res.json();
        if(data.status === 'success') {{
            document.getElementById('simResult').innerHTML = `<b>Similaridade:</b> ${{data.similaridade.toFixed(4)}}`;
        }}
    }}
</script>
</body>
</html>"""
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers(); self.wfile.write(hub.encode('utf-8')); return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/generate_cloud":
            n = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(n).decode('utf-8'))
            prompt = body.get("prompt", "")
            intencao = classificar_intencao(prompt)
            
            if intencao == "dna":
                res = analisar_dna(prompt.replace("analisar dna ", "").strip())
                self._send_json({"status": "success", "fonte": "DNA_ENGINE", "resultado": res}); return
            elif intencao == "recommend":
                self._send_json({"status": "success", "fonte": "SPOTIFY_ENGINE", "resultado": "Use a dashboard ou a API /api/recommend."}); return
            
            chave = extrair_chave(prompt)
            if chave:
                file_path = os.path.join(ARTEFACTOS_DIR, f"chave_{chave}.html")
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f: html = f.read()
                    self._send_json({"status": "success", "html": html, "fonte": "CACHE_VALIDADO"}); return
                html = sintetizar_jogo(prompt)
                if html:
                    with open(file_path, "w", encoding="utf-8") as f: f.write(html)
                    self._send_json({"status": "success", "html": html, "fonte": "SINTETIZADOR_LOCAL"}); return
            self._send_json({"status": "error", "msg": "Nao reconhecido."}); return

        if self.path == "/api/game":
            n = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(n).decode('utf-8'))
            html = sintetizar_jogo(body.get("prompt", ""))
            self._send_json({"status": "success", "html": html, "fonte": "GAME_ENGINE"}); return

        if self.path == "/api/dna":
            n = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(n).decode('utf-8'))
            res = analisar_dna(body.get("sequencia", ""))
            self._send_json({"status": "success", "resultado": res, "fonte": "BIO_ENGINE"}); return

        if self.path == "/api/recommend":
            n = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(n).decode('utf-8'))
            v1 = body.get("v1", []); v2 = body.get("v2", [])
            sim = similaridade_cosseno(v1, v2)
            self._send_json({"status": "success", "similaridade": sim, "fonte": "RECOMMENDATION_ENGINE"}); return

        self.send_response(404); self.end_headers()

socketserver.TCPServer.allow_reuse_address = True
print(f"[V158 DASHBOARD] Servidor a arrancar em 127.0.0.1:{PORT}...")
HOST = "0.0.0.0" if os.environ.get("RENDER") or os.environ.get("VERCEL") else "127.0.0.1"
with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    httpd.serve_forever()
