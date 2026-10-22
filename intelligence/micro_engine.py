import os, math, struct

LUT_PATH = os.path.join(os.path.dirname(__file__), "minimax_variants.bin")
try:
    with open(LUT_PATH, "rb") as f:
        LUT_DATA = f.read()
    NUM_MODES = struct.unpack("<I", LUT_DATA[0:4])[0]
    STATE_SIZE = struct.unpack("<I", LUT_DATA[4:8])[0]
except Exception:
    LUT_DATA = None
    NUM_MODES = 0
    STATE_SIZE = 0

def minimax_micro(board, mode=0):
    if LUT_DATA is None or mode >= NUM_MODES: return -1
    val = 0
    for i in range(8, -1, -1):
        val *= 3
        if board[i] == 'X': val += 1
        elif board[i] == 'O': val += 2
    offset = 8 + mode * STATE_SIZE
    if offset + val >= len(LUT_DATA): return -1
    move = LUT_DATA[offset + val]
    return move if move != 255 else -1

def shannon_entropy(data):
    """Opcao 2: Usando collections.Counter e list comprehension."""
    import math
    from collections import Counter
    if not data: return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((c/length) * math.log2(c/length) for c in counts.values())

def cusum_detect(data, threshold=5.0, drift=0.5):
    if len(data) < 2: return False
    mean = sum(data) / len(data); s_pos = 0.0; s_neg = 0.0
    for val in data:
        s_pos = max(0, s_pos + (val - mean) - drift)
        s_neg = max(0, s_neg - (val - mean) - drift)
        if s_pos > threshold or s_neg > threshold: return True
    return False

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)


def health_check():
    return {'status': 'ok', 'engine': 'STILB'}
