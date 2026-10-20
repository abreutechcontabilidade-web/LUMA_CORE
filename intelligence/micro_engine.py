import os, math

LUT_PATH = os.path.join(os.path.dirname(__file__), "minimax_lut.bin")
try:
    with open(LUT_PATH, "rb") as f:
        LUT = f.read()
except Exception:
    LUT = None

def minimax_micro(board):
    """
    Minimax Ultra-Rapido (O(1)): Le a jogada perfeita da LUT na RAM.
    SOTA Embedded Style (Micro:bit / ONNX).
    """
    if LUT is None: return -1
    # Converte tabuleiro ['', 'X', 'O'] para Base-3
    # 0 = '', 1 = 'X', 2 = 'O'
    val = 0
    for i in range(8, -1, -1):
        val *= 3
        if board[i] == 'X': val += 1
        elif board[i] == 'O': val += 2
        
    if val < len(LUT):
        move = LUT[val]
        if move != 255: return move
    return -1

def shannon_entropy(data):
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
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)
