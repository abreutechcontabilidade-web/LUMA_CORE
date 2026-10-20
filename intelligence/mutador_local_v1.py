"""STILB PURO - Mutador Local v1 (Bancada T70). Deterministico, idempotente, zero LLM."""
import re
MODS = {
    "cyberpunk": ('<style id="stilb_mutation_v1">\n'
        "html,body{background:#050510 !important;color:#e0f7ff !important}\n"
        "canvas{background:#0a0a1a !important;border:1px solid #00ffe1 !important;"
        "filter:drop-shadow(0 0 6px #00ffe1) drop-shadow(0 0 14px #ff00e0) !important}\n"
        "button,.btn{background:#0a0a1a !important;color:#00ffe1 !important;"
        "border:1px solid #ff00e0 !important;text-shadow:0 0 6px #00ffe1 !important}\n"
        "h1,h2,h3,p{color:#ff00e0 !important;text-shadow:0 0 10px #ff00e0 !important}\n"
        "</style>", "</head>"),
    "velocidade": ('<script id="stilb_speed_v1">\n'
        "(function(){var O=window.setInterval;window.setInterval=function(f,t){"
        "return O(f,(t>=40&&t<=400)?Math.max(30,Math.round(t*0.6)):t)}})();\n"
        "</script>", "<head>"),
}
_IDS = {"cyberpunk": "stilb_mutation_v1", "velocidade": "stilb_speed_v1"}

def aplicar_mutacoes(html, prompt):
    low, muts = prompt.lower(), []
    for m, (bloco, ancora) in MODS.items():
        if m not in low: continue
        muts.append(m)
        html = re.sub(r'<(?:style|script) id="' + _IDS[m] + r'">.*?</(?:style|script)>', "", html, flags=re.S)
        al = ancora.lower()
        if al in html.lower():
            i = html.lower().index(al)
            html = html[:i] + bloco + html[i:] if ancora == "</head>" else html[:i+len(ancora)] + bloco + html[i+len(ancora):]
        else:
            html = bloco + html
    return html, muts