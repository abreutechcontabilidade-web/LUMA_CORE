import zlib, base64, json, os
GENOMA_PATH = os.path.join(os.path.dirname(__file__), "genoma_cripto.bin")
def carregar_genoma():
    if not os.path.exists(GENOMA_PATH): return {}
    with open(GENOMA_PATH, "rb") as f: c = f.read()
    return json.loads(zlib.decompress(base64.b64decode(c)).decode('utf-8'))
def sintetizar_jogo(prompt):
    blocos = carregar_genoma()
    if not blocos: return None
    p = prompt.lower()
    if "pong ia" in p:
        logica = blocos['CANVAS'] + '\n' + blocos['PHYS_PONG_IA']
        func = 'function draw(){' + blocos['DRAW_PONG_IA'] + '}'
    elif "corrida" in p or "race" in p or "carro" in p:
        logica = blocos['CANVAS'] + '\n' + blocos['PHYS_RACE']
        func = 'function draw(){' + blocos['DRAW_RACE'] + '}'
    else:
        return None
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Jogo</title>{blocos['STYLE']}</head><body><canvas id='game' width='800' height='500'></canvas><script>\n{logica}\n{func}\n{blocos['LOOP']}\nupdate();\n</script></body></html>"
