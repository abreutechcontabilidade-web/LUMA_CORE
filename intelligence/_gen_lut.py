import os

LUT_PATH = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\minimax_lut.bin"

def check_win(b):
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for w in wins:
        if b[w[0]] == b[w[1]] == b[w[2]] != 0:
            return b[w[0]]
    return 0

def minimax(b, is_max):
    w = check_win(b)
    if w == 2: return 10
    if w == 1: return -10
    if 0 not in b: return 0
    
    if is_max:
        best = -1000
        for i in range(9):
            if b[i] == 0:
                b[i] = 2
                best = max(best, minimax(b, False))
                b[i] = 0
        return best
    else:
        best = 1000
        for i in range(9):
            if b[i] == 0:
                b[i] = 1
                best = min(best, minimax(b, True))
                b[i] = 0
        return best

def get_best_move(b):
    best_val = -1000
    best_move = -1
    for i in range(9):
        if b[i] == 0:
            b[i] = 2
            move_val = minimax(b, False)
            b[i] = 0
            if move_val > best_val:
                best_move = i
                best_val = move_val
    return best_move

print("[SOTA] A pre-computar a arvore de decisao perfeita...")
lut = bytearray([255] * 19683)
valid_count = 0

for i in range(19683):
    temp = i
    b = [0]*9
    for j in range(9):
        b[j] = temp % 3
        temp //= 3
    
    # Apenas estados validos onde e a vez da IA (O)
    x_count = b.count(1)
    o_count = b.count(2)
    if x_count != o_count: continue
    if check_win(b) != 0: continue
    if 0 not in b: continue
    
    best_move = get_best_move(b)
    lut[i] = best_move
    valid_count += 1

with open(LUT_PATH, "wb") as f:
    f.write(lut)

print(f"[OK] Tabela LUT gerada: {valid_count} estados validos de {19683} totais.")
print(f"[OK] Ficheiro binario: {LUT_PATH} ({len(lut)} bytes)")
