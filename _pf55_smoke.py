import sys
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from intelligence.mutador_stilb_v1 import aplicar_mutacoes
h, m = aplicar_mutacoes("<html><head></head><body></body></html>", "criar jogo da cobra cyberpunk com fundo neon e mais velocidade")
assert "stilb_mutation_v1" in h, "CSS ausente - mutador quebrado"
assert "strokeStyle" in h and "shadowColor" in h, "G-162 VIVO: mutador VELHO no disco"
assert "stilb_speed_v1" in h, "speed hook ausente"
h2, _ = aplicar_mutacoes(h, "criar jogo da cobra cyberpunk com fundo neon e mais velocidade")
assert h2 == h, "mutador nao-idempotente"
print("[OK] GATE-29 VERDE: importa, interceptor total, idempotente.")