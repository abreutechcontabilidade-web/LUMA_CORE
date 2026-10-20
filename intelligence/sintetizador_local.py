import zlib, base64, json, os

GENOMA_PATH = os.path.join(os.path.dirname(__file__), "genoma_cripto.bin")

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
    
    if "pong ia" in p or "pong ai" in p:
        logica = f"{blocos.get('CANVAS')}\n{blocos.get('PHYS_PONG_IA')}\n{blocos.get('INPUT_PONG_IA')}\n"
        func = f"function draw(){{{blocos.get('DRAW_PONG_IA')}}}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'
    elif "pong" in p:
        logica = f"{blocos.get('CANVAS')}\nlet p1={{x:10,y:200}},p2={{x:780,y:200}},ball={{x:400,y:250,dx:5,dy:5}};\n"
        func = "function draw(){ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);ctx.fillStyle='#00ffe1';ctx.fillRect(p1.x,p1.y,10,80);ctx.fillStyle='#ff2fd6';ctx.fillRect(p2.x,p2.y,10,80);ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(ball.x,ball.y,8,0,Math.PI*2);ctx.fill();}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'
    elif "corrida" in p or "race" in p or "carro" in p:
        logica = f"{blocos.get('CANVAS')}\n{blocos.get('PHYS_RACE')}\n{blocos.get('INPUT_RACE')}\n"
        func = f"function draw(){{ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);{blocos.get('DRAW_RACE')}}}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'
    else:
        logica = f"{blocos.get('CANVAS')}\nlet p1={{x:10,y:200}},p2={{x:780,y:200}},ball={{x:400,y:250,dx:5,dy:5}};\n"
        func = "function draw(){ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);ctx.fillStyle='#00ffe1';ctx.fillRect(p1.x,p1.y,10,80);ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(ball.x,ball.y,8,0,Math.PI*2);ctx.fill();}"
        html_canvas = '<canvas id="game" width="800" height="500"></canvas>'

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Jogo Sintetizado</title>{blocos.get('STYLE')}</head>
<body>{html_canvas}<script>
{logica}
{func}
{blocos.get('LOOP')}
update();
</script></body></html>"""
    return html
