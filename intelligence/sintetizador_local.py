import zlib, base64, json, os

GENOMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "genoma_cripto.bin")

def carregar_genoma():
    if not os.path.exists(GENOMA_PATH): return {}
    try:
        with open(GENOMA_PATH, "rb") as f: criptografado = f.read()
        comprimido = base64.b64decode(criptografado)
        return json.loads(zlib.decompress(comprimido).decode('utf-8'))
    except Exception as e: return {}

def sintetizar_jogo(prompt):
    print(f"[SINTETIZADOR] A ler 01010101 do disco para sintetizar: '{prompt}'")
    blocos = carregar_genoma()
    if not blocos: return None
        
    p = prompt.lower()
    
    if "pong ia" in p or "pong ai" in p or "pong minimax" in p:
        logica = f"{blocos.get('CANVAS')}\n{blocos.get('PHYS_PONG_IA')}\n{blocos.get('INPUT_PONG_IA')}\n"
        func = f"function draw(){{{blocos.get('DRAW_PONG_IA')}}}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'
    elif "snake ia" in p or "cobra ia" in p or "snake minimax" in p:
        logica = f"{blocos.get('CANVAS')}\n{blocos.get('PHYS_SNAKE_IA')}\n{blocos.get('INPUT_SNAKE_IA')}\n"
        func = f"function draw(){{{blocos.get('DRAW_SNAKE_IA')}}}"
        html_canvas = '<canvas id="game" width="400" height="400"></canvas>'
    elif "flappy" in p or "passaro" in p:
        logica = f"{blocos.get('CANVAS')}\n{blocos.get('PHYS_FLAPPY')}\n{blocos.get('INPUT_FLAPPY')}\n"
        func = f"function draw(){{{blocos.get('DRAW_FLAPPY')}}}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'
    elif "asteroids" in p or "asteroide" in p:
        logica = f"{blocos.get('CANVAS')}\n{blocos.get('PHYS_ASTEROIDS')}\n{blocos.get('INPUT_ASTEROIDS')}\n"
        func = f"function draw(){{{blocos.get('DRAW_ASTEROIDS')}}}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'
    elif "forca" in p or "hangman" in p:
        logica = f"{blocos.get('CANVAS')}\n{blocos.get('PHYS_FORCA')}\n{blocos.get('INPUT_FORCA')}\n"
        func = f"function draw(){{{blocos.get('DRAW_FORCA')}}}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'
    else:
        # Jogo normal (sem IA) para manter a compatibilidade
        logica = f"{blocos.get('CANVAS')}\nlet p1={{x:10,y:200}},p2={{x:780,y:200}},ball={{x:400,y:250,dx:5,dy:5}};\n"
        func = "function draw(){ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);ctx.fillStyle='#00ffe1';ctx.fillRect(p1.x,p1.y,10,80);ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(ball.x,ball.y,8,0,Math.PI*2);ctx.fill();}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Jogo com IA</title>{blocos.get('STYLE')}</head>
<body>{html_canvas}<script>\n{logica}\n{func}\n{blocos.get('LOOP')}\nupdate();\n</script></body></html>"""
    return html

