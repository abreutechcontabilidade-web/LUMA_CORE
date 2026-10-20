import os, random

LUT_PATH = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\minimax_variants.bin"
NUM_MODES = 3
STATE_SIZE = 19683  # 3^9

def check_win(b):
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for w in wins:
        if b[w[0]] == b[w[1]] == b[w[2]] != 0:
            return b[w[0]]
    return 0

def minimax(b, is_max, depth=0, max_depth=None):
    w = check_win(b)
    if w == 2: return 10 - depth
    if w == 1: return depth - 10
    if 0 not in b: return 0
    
    if max_depth is not None and depth >= max_depth:
        # Heurística simples: conta linhas abertas
        return (b.count(2) - b.count(1)) * 0.1
    
    if is_max:
        best = -1000
        for i in range(9):
            if b[i] == 0:
                b[i] = 2
                best = max(best, minimax(b, False, depth+1, max_depth))
                b[i] = 0
        return best
    else:
        best = 1000
        for i in range(9):
            if b[i] == 0:
                b[i] = 1
                best = min(best, minimax(b, True, depth+1, max_depth))
                b[i] = 0
        return best

def get_best_move(b, mode):
    if mode == 0:
        # Imbatível (Minimax/Alpha-Beta)
        best_val = -1000
        best_move = -1
        for i in range(9):
            if b[i] == 0:
                b[i] = 2
                val = minimax(b, False)
                b[i] = 0
                if val > best_val: best_val = val; best_move = i
        return best_move
    elif mode == 1:
        # Médio (Expectimax simplificado: 20% de erro)
        if random.random() < 0.2:
            return random.choice([i for i in range(9) if b[i] == 0])
        best_val = -1000
        best_move = -1
        for i in range(9):
            if b[i] == 0:
                b[i] = 2
                val = minimax(b, False)
                b[i] = 0
                if val > best_val: best_val = val; best_move = i
        return best_move
    elif mode == 2:
        # Fácil (Depth-Limited 2 + Heurística)
        best_val = -1000
        best_move = -1
        for i in range(9):
            if b[i] == 0:
                b[i] = 2
                val = minimax(b, False, max_depth=2)
                b[i] = 0
                if val > best_val: best_val = val; best_move = i
        return best_move
    return -1

print("[SOTA] Gerando LUT multicamada...")
lut = bytearray()
lut.extend(NUM_MODES.to_bytes(4, 'little'))
lut.extend(STATE_SIZE.to_bytes(4, 'little'))

valid_states = []
for i in range(STATE_SIZE):
    temp = i
    b = [0]*9
    for j in range(9):
        b[j] = temp % 3
        temp //= 3
    if b.count(1) == b.count(2) + 1 and check_win(b) == 0 and 0 in b:
        valid_states.append(b)

print(f"[INFO] Estados válidos (turno da IA): {len(valid_states)}")

for mode in range(NUM_MODES):
    print(f"[MODE {mode}] A pre-calcular...")
    layer = bytearray([255] * STATE_SIZE)
    for i in range(STATE_SIZE):
        temp = i
        b = [0]*9
        for j in range(9):
            b[j] = temp % 3
            temp //= 3
        if b.count(1) == b.count(2) + 1 and check_win(b) == 0 and 0 in b:
            move = get_best_move(b, mode)
            layer[i] = move
    lut.extend(layer)
    print(f"[MODE {mode}] Camada pronta ({len(layer)} bytes)")

with open(LUT_PATH, "wb") as f:
    f.write(lut)
print(f"[OK] Ficheiro multicamada criado: {LUT_PATH} ({len(lut)} bytes)")
