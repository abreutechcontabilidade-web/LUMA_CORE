import re

def aplicar_patch_tetris_avancado(html_classico):
    if not isinstance(html_classico, str) or not html_classico:
        return html_classico

    # 1. CSS Cyberpunk (substitui o fundo branco)
    css_cyberpunk = """
    <style id="stilb_patch_css">
    body { background: #050510 !important; color: #00ffe1 !important; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    canvas { border: 2px solid #00ffe1 !important; box-shadow: 0 0 15px #00ffe1 !important; }
    #score { color: #ff2fd6 !important; text-shadow: 0 0 10px #ff2fd6 !important; }
    </style>
    """
    if "</head>" in html_classico.lower():
        i = html_classico.lower().index("</head>")
        html_classico = html_classico[:i] + css_cyberpunk + html_classico[i:]

    # 2. Injetar variáveis de estado (Hold) no início do script
    script_match = re.search(r'(<script>)(.*?)(</script>)', html_classico, re.S | re.I)
    if not script_match: return html_classico
    js = script_match.group(2)

    if "let holdPiece" not in js:
        js = js.replace("const arena =", "let holdPiece = null;\nlet canHold = true;\nconst arena =")

    # 3. GHOST PIECE: Encontra a chamada de desenho da peça atual e injeta a sombra antes
    # O Code Explained usa a função drawPiece(player) dentro do loop de renderização
    ghost_logic = """
    // GATE-38: GHOST PIECE
    if (player) {
        let ghostY = player.pos.y;
        while (!collide(arena, {pos: {x: player.pos.x, y: ghostY + 1}, matrix: player.matrix})) ghostY++;
        ctx.globalAlpha = 0.25;
        player.pos.y = ghostY;
        drawPiece(player);
        ctx.globalAlpha = 1.0;
    }
    """
    if "drawPiece(player);" in js and "GATE-38: GHOST PIECE" not in js:
        js = js.replace("drawPiece(player);", ghost_logic + "\ndrawPiece(player);")

    # 4. HOLD PIECE: Adiciona a tecla 'C' no listener de eventos
    if "case 'c':" not in js:
        js = js.replace("case 'ArrowUp':", """
        case 'c':
        case 'C':
            if (canHold && player) {
                if (holdPiece) {
                    let temp = holdPiece;
                    holdPiece = player;
                    player = temp;
                } else {
                    holdPiece = player;
                    player = createPiece();
                }
                canHold = false;
                player.pos = {x: 3, y: 0};
            }
            break;
        case 'ArrowUp':""")

    html_classico = html_classico[:script_match.start(2)] + js + html_classico[script_match.end(2):]
    return html_classico