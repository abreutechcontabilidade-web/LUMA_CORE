import math

# 1. MINIMAX ALPHA-BETA (Jogo da Velha - Imbatível)
def minimax_alpha_beta(board, depth, alpha, beta, is_max, player_ia='O', player_humano='X'):
    def check_win(b, p):
        wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        return any(all(b[i] == p for i in w) for w in wins)
    if check_win(board, player_ia): return 10 - depth
    if check_win(board, player_humano): return depth - 10
    if '' not in board: return 0
    if is_max:
        best = -1000
        for i in range(9):
            if board[i] == '':
                board[i] = player_ia
                best = max(best, minimax_alpha_beta(board, depth+1, alpha, beta, False))
                board[i] = ''
                alpha = max(alpha, best)
                if beta <= alpha: break
        return best
    else:
        best = 1000
        for i in range(9):
            if board[i] == '':
                board[i] = player_humano
                best = min(best, minimax_alpha_beta(board, depth+1, alpha, beta, True))
                board[i] = ''
                beta = min(beta, best)
                if beta <= alpha: break
        return best

def obter_melhor_jogada_ia(board):
    best_val = -1000
    best_move = -1
    for i in range(9):
        if board[i] == '':
            board[i] = 'O'
            move_val = minimax_alpha_beta(board, 0, -1000, 1000, False)
            board[i] = ''
            if move_val > best_val:
                best_move = i
                best_val = move_val
    return best_move

# 2. HEURÍSTICA DE PREVISÃO (Pong)
def ia_pong(ball_y, paddle_y):
    """A IA move a raquete para a posição Y da bola"""
    if ball_y > paddle_y + 10: return 5  # Move para baixo
    if ball_y < paddle_y - 10: return -5 # Move para cima
    return 0

# 3. HEURÍSTICA DE PERSEGUIÇÃO (Pacman)
def ia_pacman(pac_x, pac_y, ghost_x, ghost_y):
    """O fantasma persegue o Pacman"""
    dx = 2 if pac_x > ghost_x else (-2 if pac_x < ghost_x else 0)
    dy = 2 if pac_y > ghost_y else (-2 if pac_y < ghost_y else 0)
    return dx, dy

# 4. HEURÍSTICA GULOSA (Snake)
def ia_snake(snake_x, snake_y, apple_x, apple_y):
    """A cobra vai na direção da maçã"""
    if apple_x > snake_x: return 1, 0   # Direita
    if apple_x < snake_x: return -1, 0  # Esquerda
    if apple_y > snake_y: return 0, 1   # Baixo
    if apple_y < snake_y: return 0, -1  # Cima
    return 1, 0
