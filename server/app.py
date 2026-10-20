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
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        if self.path == "/api/status":
            self._send_json({"status": "LUMA_CORE v161 (Engine API)", "services": ["games", "dna", "recommendation"]}); return
        # Deixa o servidor base lidar com os artefactos (jogos) e ficheiros estáticos
        super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

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
HOST = "0.0.0.0" if os.environ.get("RENDER") or os.environ.get("VERCEL") else "127.0.0.1"
print(f"[V159 CLOUD] Servidor a arrancar em {HOST}:{PORT}...")
with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    httpd.serve_forever()


