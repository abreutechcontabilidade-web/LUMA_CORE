import re

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o bloco CHAVES inteiro para garantir a inclusão de 'carro' e 'tijolo'
novo_chaves = """CHAVES = [
    ("jogo_da_velha", ("jogo da velha", "tic tac toe")),
    ("jogo_da_cobra", ("cobra", "snake")),
    ("pong", ("pong", "raquete")),
    ("tetris", ("tetris",)),
    ("pacman", ("pacman",)),
    ("breakout", ("breakout", "tijolos", "tijolo")),
    ("space", ("space", "nave")),
    ("corrida", ("corrida", "race", "carro")),
    ("plataforma", ("plataforma", "mario")),
    ("rpg", ("rpg", "texto")),
    ("memoria", ("memoria", "memory")),
    ("shooter", ("shooter", "tiro")),
    ("tower", ("tower", "defesa")),
    ("calculadora", ("calculadora", "calculator")),
]"""

# Substitui o bloco PALAVRAS inteiro
novo_palavras = """PALAVRAS = {
    "jogo_da_cobra": ("cobra", "snake"), "jogo_da_velha": ("velha", "tictactoe"),
    "pong": ("pong", "raquete"), "tetris": ("tetris",), "pacman": ("pacman",),
    "breakout": ("breakout", "tijolos", "tijolo"), "space": ("space", "nave"),
    "corrida": ("corrida", "race", "carro"),
    "plataforma": ("plataforma", "mario"),
    "rpg": ("rpg", "texto"), "memoria": ("memoria", "memory"),
    "shooter": ("shooter", "tiro"), "tower": ("tower", "defesa"),
    "calculadora": ("calculadora", "calculator"),
}"""

# Aplica o regex de forma segura (DOTALL apanha multilinhas)
code = re.sub(r'CHAVES\s*=\s*\[.*?\]', novo_chaves, code, flags=re.DOTALL)
code = re.sub(r'PALAVRAS\s*=\s*\{.*?\}', novo_palavras, code, flags=re.DOTALL)

with open(APP, "w", encoding="utf-8") as f:
    f.write(code)
print("[OK] Dicionario CHAVES e PALAVRAS atualizado com sucesso.")
