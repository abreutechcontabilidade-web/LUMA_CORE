import re

def aplicar_mutacoes(html, prompt):
    if not isinstance(html, str) or not html:
        return html, []
        
    p = prompt.lower()
    muts = []
    
    # Limpa mutações antigas
    html = re.sub(r'<style id="stilb_mutation_v1">.*?</style>', "", html, flags=re.S)
    html = re.sub(r'<script id="stilb_canvas_v1">.*?</script>', "", html, flags=re.S)
    
    # Cores e Estilo
    if "cyberpunk" in p or "neon" in p or "cor" in p or "azul" in p or "vermelho" in p:
        muts.append("cyberpunk_v3")
        
        # CSS Nuclear (Interface)
        css = """
        <style id="stilb_mutation_v1">
        body, html, main, section, div, header, footer, .arena, .card, .container, .score-board {
            background-color: #050510 !important;
            background-image: none !important;
            color: #e0f7ff !important;
            border-color: #ff2fd6 !important;
        }
        h1, h2, h3, p, span, label {
            color: #ff2fd6 !important;
            text-shadow: 0 0 10px #ff2fd6 !important;
        }
        button, .btn {
            background-color: #1a1a2e !important;
            color: #00ffe1 !important;
            border: 1px solid #00ffe1 !important;
        }
        /* O Segredo está aqui: A Magia Matemática no Canvas */
        canvas {
            filter: hue-rotate(180deg) saturate(2) brightness(1.2) contrast(1.1) !important;
            border: 2px solid #00ffe1 !important;
            box-shadow: 0 0 20px #00ffe1 !important;
            background-color: #0a0a1a !important;
        }
        </style>
        """
        
        if "</head>" in html.lower():
            i = html.lower().index("</head>")
            html = html[:i] + css + html[i:]
        else:
            html = css + html

    return html, muts