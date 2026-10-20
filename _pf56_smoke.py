import sys
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
import intelligence.mutador_stilb_v1 as mm
from intelligence.mutador_stilb_v1 import aplicar_mutacoes, _stilb_mutar_seguro
h, m = aplicar_mutacoes("<html><head></head></html>", "criar jogo da cobra cyberpunk com fundo neon e mais velocidade")
assert "stilb_mutation_v1" in h and "stilb_speed_v1" in h, "CSS/speed ausentes"
assert "fillStyle','strokeStyle','shadowColor" in h, "G-162 VIVO: interceptor incompleto"
h2, _ = aplicar_mutacoes(h, "criar jogo da cobra cyberpunk com fundo neon e mais velocidade")
assert h2 == h, "nao-idempotente"
hb = _stilb_mutar_seguro("<html><head></head></html>", "cyberpunk velocidade")
assert "stilb_mutation_v1" in hb, "seguro: mutacao basica falhou"
orig = mm.aplicar_mutacoes
def boom(a, b):
    raise RuntimeError("boom")
mm.aplicar_mutacoes = boom
hfail = mm._stilb_mutar_seguro("<html><body>base</body></html>", "cyberpunk")
mm.aplicar_mutacoes = orig
assert hfail == "<html><body>base</body></html>", "GATE-30: base nao preservada no fail"
print("[OK] GATE-29+30 VERDE: importa, interceptor triplo, idempotente, fail-vocal.")