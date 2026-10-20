import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intelligence.sintetizador_local import sintetizar_jogo

GAMES = ["pong", "pong ia", "snake", "snake ia", "corrida", "memoria",
         "tower", "rpg", "metroid", "flappy", "asteroids", "forca",
         "pacman", "space"]

os.makedirs("intelligence/artefacts", exist_ok=True)
for g in GAMES:
    html = sintetizar_jogo(g)
    if html:
        key = g.replace(" ", "_")
        with open(f"intelligence/artefacts/chave_{key}.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated chave_{key}.html")
