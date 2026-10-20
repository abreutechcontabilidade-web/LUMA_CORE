import re

_MARKERS = re.compile(r'<(style|script) id="stilb_[a-z0-9_]+">.*?</\1>', re.S)

_CSS = """<style id="stilb_mutation_v1">
body, html, main, section, div, header, footer, .arena, .card, .container, .score-board, #app {
  background-color: #050510 !important;
  background-image: none !important;
  color: #e0f7ff !important;
  border-color: #ff2fd6 !important;
}
h1, h2, h3, p, span, label, li { color: #ff2fd6 !important; text-shadow: 0 0 10px #ff2fd6 !important; }
button, .btn { background-color: #1a1a2e !important; color: #00ffe1 !important; border: 1px solid #00ffe1 !important; }
canvas { border: 2px solid #00ffe1 !important; box-shadow: 0 0 18px #00ffe1 !important; background-color: #0a0a1a !important; }
</style>"""

_JS = r"""<script id="stilb_canvas_v1">
(function(){
  var MAP = {'#00ff00':'#ff2fd6','#0f0':'#ff2fd6','green':'#ff2fd6','lime':'#ff2fd6',
             '#ff0000':'#00ffe1','#f00':'#00ffe1','red':'#00ffe1',
             '#000000':'#0a0a1a','#000':'#0a0a1a','black':'#0a0a1a',
             '#ffffff':'#e0f7ff','white':'#e0f7ff'};
  function map(v){
    if (typeof v !== 'string') return v;
    var k = v.toLowerCase().replace(/\s+/g,'');
    if (MAP[k]) return MAP[k];
    var m = k.match(/^rgba?\((\d+),(\d+),(\d+)/);
    if (m){
      var r = +m[1], g = +m[2], b = +m[3];
      if (g > 180 && r < 120 && b < 120) return '#ff2fd6';
      if (r > 180 && g < 120 && b < 120) return '#00ffe1';
      if (r < 40 && g < 40 && b < 40)    return '#0a0a1a';
    }
    return v;
  }
  ['fillStyle','strokeStyle','shadowColor'].forEach(function(prop){
    var d = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, prop);
    if (!d || !d.set) return;
    Object.defineProperty(CanvasRenderingContext2D.prototype, prop, {
      set: function(v){ d.set.call(this, map(v)); },
      get: function(){ return d.get.call(this); },
      configurable: true
    });
  });
})();
</script>"""

_SPEED = """<script id="stilb_speed_v1">
(function(){var O=window.setInterval;window.setInterval=function(f,t){
return O(f,(t>=40&&t<=400)?Math.max(30,Math.round(t*0.6)):t)}})();
</script>"""

def _inject(html, bloco):
    low = html.lower()
    i = low.find("</head>")
    if i != -1: return html[:i] + bloco + html[i:]
    j = low.find("<head")
    if j != -1:
        k = low.find(">", j)
        if k != -1: return html[:k + 1] + bloco + html[k + 1:]
    return bloco + html

def aplicar_mutacoes(html, prompt):
    if not isinstance(html, str) or not html: return html, []
    p = (prompt or "").lower()
    muts = []
    html = _MARKERS.sub("", html)
    if any(w in p for w in ("cyberpunk", "neon", "cor", "rosa", "azul", "escuro", "colorido")):
        muts.append("cyberpunk")
        html = _inject(html, _CSS)
        html = _inject(html, _JS)
    if any(w in p for w in ("velocidade", "rapido", "rápido", "speed", "fast")):
        muts.append("velocidade")
        html = _inject(html, _SPEED)
    return html, muts

def _stilb_mutar_seguro(html, prompt):
    try:
        return aplicar_mutacoes(html, prompt)[0]
    except Exception as e:
        print("[STILB][CRITICO] Falha na ULTIMA MILHA - jogo base servido sem mutacao:", repr(e))
        return html