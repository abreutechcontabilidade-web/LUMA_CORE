import sys, os, json
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")

from intelligence.github_learner import aprender_do_github
from intelligence.mutador_stilb_v1 import _stilb_mutar_seguro

# 1. Pesquisa e Download
prompt = "classic tetris html5 canvas javascript"
html, info = aprender_do_github(prompt)

if html:
    # 2. Validação GATE-33
    has_canvas = "<canvas" in html.lower()
    has_input = "keydown" in html.lower() or "arrowup" in html.lower() or "touchstart" in html.lower()
    
    if has_canvas and has_input:
        print("[GATE-33] VALIDADO: O Tetris tem Canvas e Inputs.")
        # 3. Mutação STILB
        html_mutado = _stilb_mutar_seguro(html, prompt)
        
        # 4. Salvar no Genoma
        artefacto_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\artefacts\tetris_classico.html"
        os.makedirs(os.path.dirname(artefacto_path), exist_ok=True)
        with open(artefacto_path, "w", encoding="utf-8") as f:
            f.write(html_mutado)
        print(f"[OK] Tetris Clássico salvo em: {artefacto_path}")
        print(f"[INFO] Proveniência: {info}")
    else:
        print("[GATE-33] REPROVADO: O repositório não contém Canvas ou Inputs.")
else:
    print("[ERRO] O GitHub Learner não conseguiu descarregar o Tetris.")