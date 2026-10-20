import math

def shannon_entropy(data):
    """Probabilístico: Mede a imprevisibilidade dos movimentos (Pacman, Snake)."""
    if not data: return 0.0
    freq = {}
    for item in data:
        freq[item] = freq.get(item, 0) + 1
    entropy = 0.0
    total = len(data)
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def cusum_detect(data, threshold=5.0, drift=0.5):
    """Determinístico/Probabilístico: Deteta mudanças de padrão (Asteroids, Metroid)."""
    if len(data) < 2: return False
    mean = sum(data) / len(data)
    s_pos = 0.0
    s_neg = 0.0
    for val in data:
        s_pos = max(0, s_pos + (val - mean) - drift)
        s_neg = max(0, s_neg - (val - mean) - drift)
        if s_pos > threshold or s_neg > threshold:
            return True
    return False

def cosine_similarity(v1, v2):
    """Vetorial: Encontra o alvo mais próximo (Recomendação, Perseguição)."""
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def obter_melhor_jogada_ia(board):
    """Minimax Alpha-Beta (Jogo da Velha - Imbatível)."""
    def minimax(b, depth, alpha, beta, is_max, player_ia='O', player_humano='X'):
        def check_win(b, p):
            wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
            return any(all(b[i] == p for i in w) for w in wins)
        if check_win(b, player_ia): return 10 - depth
        if check_win(b, player_humano): return depth - 10
        if '' not in b: return 0
        if is_max:
            best = -1000
            for i in range(9):
                if b[i] == '':
                    b[i] = player_ia
                    best = max(best, minimax(b, depth+1, alpha, beta, False))
                    b[i] = ''
                    alpha = max(alpha, best)
                    if beta <= alpha: break
            return best
        else:
            best = 1000
            for i in range(9):
                if b[i] == '':
                    b[i] = player_humano
                    best = min(best, minimax(b, depth+1, alpha, beta, True))
                    b[i] = ''
                    beta = min(beta, best)
                    if beta <= alpha: break
            return best
    best_val = -1000
    best_move = -1
    for i in range(9):
        if board[i] == '':
            board[i] = 'O'
            move_val = minimax(board, 0, -1000, 1000, False)
            board[i] = ''
            if move_val > best_val:
                best_move = i
                best_val = move_val
    return best_move
