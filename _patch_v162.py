import re
APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
with open(APP, "r", encoding="utf-8") as f: code = f.read()

novo_chaves = """CHAVES = [
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
    ("flappy", ("flappy", "passaro", "bird")),
    ("asteroids", ("asteroids", "asteroide")),
    ("forca", ("forca", "hangman")),
    ("calculadora", ("calculadora", "calculator")),
]"""
code = re.sub(r'CHAVES\s*=\s*\[.*?\]', novo_chaves, code, flags=re.DOTALL)

novo_palavras = """PALAVRAS = {
    "jogo_da_cobra": ("cobra", "snake"), "jogo_da_velha": ("velha", "tictactoe"),
    "pong": ("pong", "raquete"), "tetris": ("tetris",), "pacman": ("pacman",),
    "breakout": ("breakout", "tijolos", "tijolo"), "space": ("space", "nave"),
    "corrida": ("corrida", "race", "carro"), "metroid": ("metroid", "plataforma", "mario", "tiro"),
    "rpg": ("rpg", "texto"), "memoria": ("memoria", "memory"),
    "tower": ("tower", "defesa"), "velha_ia": ("minimax",),
    "flappy": ("flappy", "passaro", "bird"), "asteroids": ("asteroids", "asteroide"),
    "forca": ("forca", "hangman"),
    "calculadora": ("calculadora", "calculator"),
}"""
code = re.sub(r'PALAVRAS\s*=\s*\{.*?\}', novo_palavras, code, flags=re.DOTALL)
with open(APP, "w", encoding="utf-8") as f: f.write(code)
print("[OK] app.py atualizado para v162.")
